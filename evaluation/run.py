"""Compare two coding workflows against external acceptance and regression checks."""

import argparse
import json
import math
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path


MODES = ("single", "pipeline")


def git(workspace, *args):
    return subprocess.check_output(["git", "-C", str(workspace), *args])


def checkout(repo, commit, destination):
    # A detached, independent clone avoids sharing writable Git metadata with another run.
    subprocess.run(
        ["git", "clone", "--quiet", "--no-local", str(repo), str(destination)],
        check=True,
    )
    git(destination, "checkout", "--quiet", "--detach", commit)


def run_command(argv, workspace, log, timeout, *, prompt=None):
    start = time.monotonic()
    with log.open("wb") as handle:
        try:
            result = subprocess.run(
                argv, cwd=workspace, input=prompt, stdout=handle,
                stderr=subprocess.STDOUT, timeout=timeout, check=False,
            )
            status = "passed" if result.returncode == 0 else "failed"
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            status, exit_code = "timeout", None
        except OSError as error:
            handle.write(str(error).encode())
            status, exit_code = "unavailable", None
    return {
        "status": status,
        "exit_code": exit_code,
        "seconds": round(time.monotonic() - start, 3),
        "log": str(log),
    }


def score(checks, workspace, output, timeout, prefix):
    return {
        name: run_command(argv, workspace, output / f"{prefix}-{name}.log", timeout)
        for name, argv in checks.items()
    }


def measure(repo, commit, ticket, mode, adapter, checks, output, agent_timeout, check_timeout):
    output.mkdir()
    with tempfile.TemporaryDirectory(prefix="mobile-dev-eval-") as temp:
        agent = Path(temp) / "agent"
        checkout(repo, commit, agent)
        prompt = ticket if mode == "single" else "/cto " + ticket
        execution = run_command(
            adapter, agent, output / "agent.log", agent_timeout, prompt=prompt.encode(),
        )
        metrics_file = agent / ".evaluation-metrics.json"
        cost = None
        if metrics_file.is_file():
            value = json.loads(metrics_file.read_text()).get("cost_usd")
            if value is not None:
                if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
                    raise ValueError("cost_usd must be a finite nonnegative number")
                cost = value
            metrics_file.unlink()
        git(agent, "add", "-A")
        patch = git(agent, "diff", "--cached", "--binary", "--no-ext-diff", commit, "--")
        patch_file = output / "change.patch"
        patch_file.write_bytes(patch)

        # The evaluator starts from the pinned base and receives only the submitted patch.
        # Run each check in a fresh checkout so one check cannot affect another.
        results = {}
        for index, (name, command) in enumerate(checks.items()):
            candidate = Path(temp) / f"check-{index}"
            checkout(repo, commit, candidate)
            if patch:
                git(candidate, "apply", str(patch_file))
            results.update(score({name: command}, candidate, output, check_timeout, "candidate"))
            shutil.rmtree(candidate)
    return {"agent": execution, "cost_usd": cost, "changed": bool(patch), "checks": results}


def evaluate(config, output, repetitions, agent_timeout, check_timeout):
    repo = Path(config["repository"]).resolve(strict=True)
    cases = config["cases"]
    if not cases:
        raise ValueError("at least one case is required")
    rows = []
    case_ids = set()
    for case in cases:
        case_id = case["id"]
        if not case_id.replace("-", "").replace("_", "").isalnum() or case_id in case_ids:
            raise ValueError(f"invalid or duplicate case id: {case_id}")
        case_ids.add(case_id)
        commit = git(repo, "rev-parse", "--verify", case["base"] + "^{commit}").decode().strip()
        checks = {key: case[key] for key in ("acceptance", "regression")}
        case_dir = output / case_id
        case_dir.mkdir()
        baseline = {}
        for name, command in checks.items():
            with tempfile.TemporaryDirectory(prefix="mobile-dev-base-") as temp:
                workspace = Path(temp) / "base"
                checkout(repo, commit, workspace)
                baseline.update(score({name: command}, workspace, case_dir, check_timeout, "base"))
        if baseline["acceptance"]["status"] != "failed" or baseline["regression"]["status"] != "passed":
            raise ValueError(f"{case_id}: base must fail acceptance and pass regression. Check {case_dir}")

        for attempt in range(1, repetitions + 1):
            # Alternate first position to reduce ordering effects.
            order = MODES if attempt % 2 else reversed(MODES)
            for mode in order:
                result = measure(
                    repo, commit, case["ticket"], mode, config["adapters"][mode], checks,
                    case_dir / f"{attempt}-{mode}", agent_timeout, check_timeout,
                )
                rows.append({
                    "case": case_id, "base": commit, "attempt": attempt, "mode": mode,
                    "baseline": baseline, **result,
                })
    return rows


def summarize(rows):
    summary = {}
    for mode in MODES:
        runs = [row for row in rows if row["mode"] == mode]
        costs = [row["cost_usd"] for row in runs if row["cost_usd"] is not None]
        summary[mode] = {
            "runs": len(runs),
            "successful_runs": sum(
                row["agent"]["status"] == "passed"
                and all(check["status"] == "passed" for check in row["checks"].values())
                for row in runs
            ),
            "acceptance_passes": sum(row["checks"]["acceptance"]["status"] == "passed" for row in runs),
            "regression_failures": sum(row["checks"]["regression"]["status"] == "failed" for row in runs),
            "regression_checks_incomplete": sum(
                row["checks"]["regression"]["status"] in ("timeout", "unavailable") for row in runs
            ),
            "median_agent_seconds": statistics.median(row["agent"]["seconds"] for row in runs),
            "median_cost_usd": statistics.median(costs) if costs else None,
            "runs_with_cost": len(costs),
        }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--agent-timeout", type=int, default=1800)
    parser.add_argument("--check-timeout", type=int, default=300)
    args = parser.parse_args()
    if min(args.repetitions, args.agent_timeout, args.check_timeout) < 1:
        parser.error("repetitions and timeouts must be positive")
    config = json.loads(args.config.read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    rows = evaluate(config, output, args.repetitions, args.agent_timeout, args.check_timeout)
    report = {"experiment": config.get("experiment", {}), "summary": summarize(rows), "runs": rows}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
