"""Invoke a single repository role per Claude Code session."""

import json
import subprocess
import sys
from pathlib import Path


SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"enum": ["pass", "fail", "blocked"]},
        "reason": {"type": "string"},
        "owner": {"enum": ["frontend", "backend", "contract"]},
        "slices": {"type": "array", "items": {"type": "string"}},
        "artifacts": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "reason", "artifacts"],
    "additionalProperties": False,
}


def main():
    request = json.load(sys.stdin)
    role = request["role"]
    skill = "cto" if role.startswith("cto-") else role
    skill_path = Path(".claude/skills") / skill / "SKILL.md"
    if not skill_path.is_file():
        print(json.dumps({"status": "blocked", "reason": f"Missing skill file: {skill_path}"}))
        return
    stage_notes = {
        "cto-intake": "Only prepare the brief and task folders for this feature. Stop before starting implementation.",
        "cto-accept": "Only run final acceptance on the indicated side. Reuse the cross-stack report when applicable.",
    }
    prompt = (
        f"Read CLAUDE.md and {skill_path}. Execute only the {role} stage. "
        "LangGraph owns scheduling, checkpoints, retries, human approval and handoffs. "
        "Return control after this stage. Skip any instructions to invoke other roles, "
        "run the cross-stack gate from CTO acceptance, or update the Markdown run checkpoint. "
        "Review existing artifacts and workspace changes before writing. If a matching stage "
        "already completed, reuse its evidence instead of repeating writes. "
        "If a prerequisite or decision is missing, report blocked with a concrete explanation. "
        "For a planner pass, return slice IDs in dependency order. "
        "For an integration failure, identify its owner. "
        "For a task-level repair with no slice ID, use the prior failing report to locate the affected slice. "
        f"{stage_notes.get(role, '')}\nStage input:\n{json.dumps(request)}"
    )
    response = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--json-schema", json.dumps(SCHEMA)],
        input=prompt, text=True, capture_output=True, check=False,
    )
    if response.returncode:
        raise SystemExit(response.stderr or f"Claude Code exited {response.returncode}")
    envelope = json.loads(response.stdout)
    output = envelope.get("structured_output")
    if not isinstance(output, dict) or envelope.get("is_error"):
        raise SystemExit("Claude Code did not return a structured role result.")
    print(json.dumps(output))


if __name__ == "__main__":
    main()
