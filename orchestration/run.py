"""Run or resume the feature workflow with a role adapter and SQLite checkpoints."""

import argparse
import json
import subprocess
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from workflow import build_workflow


def run_role(argv, timeout, request, workspace):
    try:
        result = subprocess.run(
            argv, cwd=workspace, input=json.dumps(request), capture_output=True,
            text=True, timeout=timeout, check=False,
        )
        if result.returncode:
            return {"status": "blocked", "reason": f"Adapter exited {result.returncode}: {result.stderr[-2000:]}"}
        reply = json.loads(result.stdout)
        if not isinstance(reply, dict) or reply.get("status") not in ("pass", "fail", "blocked"):
            raise ValueError("Expected a JSON object with status pass, fail, or blocked.")
        if request["role"].endswith("-planner") and reply["status"] == "pass":
            slices = reply.get("slices")
            if (not isinstance(slices, list) or not slices
                    or any(not isinstance(item, str) or not item.strip() for item in slices)
                    or len(set(slices)) != len(slices)):
                raise ValueError("Planner must return a nonempty list of unique slice IDs.")
        return reply
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return {"status": "blocked", "reason": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--thread", required=True)
    parser.add_argument("--adapter", required=True, help="JSON array containing the adapter command")
    parser.add_argument("--timeout", type=int, default=900)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--workspace", type=Path, required=True)
    start.add_argument("--ticket", required=True)
    start.add_argument("--scope", choices=("backend", "frontend", "both"), required=True)
    start.add_argument("--api-scope", choices=("none", "existing", "changed"), default="none")
    resume = commands.add_parser("resume")
    resume.add_argument("decision", choices=("approve", "retry", "cancel", "continue"))
    args = parser.parse_args()
    try:
        argv = json.loads(args.adapter)
        if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or not arg for arg in argv):
            raise ValueError("Expected a nonempty JSON array of command arguments.")
        if args.timeout < 1:
            raise ValueError("Timeout must be positive.")
    except ValueError as error:
        parser.error(str(error))

    with SqliteSaver.from_conn_string(args.db) as saver:
        workflow = build_workflow(
            lambda request, workspace: run_role(argv, args.timeout, request, workspace), saver
        )
        config = {"configurable": {"thread_id": args.thread}, "recursion_limit": 1000}
        snapshot = workflow.get_state(config)
        if args.command == "start":
            if snapshot.values:
                parser.error("Thread already exists. Resume it or choose a new thread ID.")
            if args.scope == "frontend" and args.api_scope == "changed":
                parser.error("A changed API requires both backend and frontend work.")
            if not args.workspace.is_dir():
                parser.error("Workspace must be an existing directory.")
            graph_input = {
                "ticket": args.ticket, "workspace": str(args.workspace.resolve()),
                "thread_id": args.thread, "scope": args.scope, "api_scope": args.api_scope,
            }
        else:
            if not snapshot.values or not snapshot.next:
                parser.error("Thread does not exist or has already finished.")
            if snapshot.interrupts:
                kind = snapshot.interrupts[0].value["kind"]
                allowed = ("approve", "cancel") if kind == "approval" else ("retry", "cancel")
                if args.decision not in allowed:
                    parser.error(f"This interrupt accepts: {', '.join(allowed)}.")
                graph_input = Command(resume=args.decision)
            else:
                if args.decision != "continue":
                    parser.error("Use continue to recover an interrupted controller process.")
                graph_input = None
        result = workflow.invoke(graph_input, config)
        print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()
