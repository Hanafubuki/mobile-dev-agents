"""Compare paired benchmark reports after changing a skill, check, or adapter."""

import argparse
import json
from pathlib import Path


def paired_runs(report):
    runs = {}
    for row in report["runs"]:
        key = (row["case"], row["base"], row["mode"], row["attempt"])
        if key in runs:
            raise ValueError(f"Duplicate benchmark trial: {key}")
        runs[key] = row
    return runs


def compare(before, after):
    old_runs, new_runs = paired_runs(before), paired_runs(after)
    if not old_runs or old_runs.keys() != new_runs.keys():
        raise ValueError("Reports must include the same cases, source commits, modes and attempts.")

    changes = []
    counts = {}
    for key, old in sorted(old_runs.items()):
        new = new_runs[key]
        if old["checks"].keys() != new["checks"].keys():
            raise ValueError(f"Check names differ for trial {key}")
        old_checks = {"execution": old["agent"], **old["checks"]}
        new_checks = {"execution": new["agent"], **new["checks"]}
        for name, old_check in old_checks.items():
            new_check = new_checks[name]
            pair = (old_check["status"], new_check["status"])
            if pair == ("failed", "passed"):
                outcome = "fixed"
            elif pair == ("passed", "failed"):
                outcome = "regressed"
            elif pair == ("failed", "failed"):
                outcome = "still_failing"
            elif pair == ("passed", "passed"):
                outcome = "still_passing"
            else:
                outcome = "inconclusive"
            mode_counts = counts.setdefault(key[2], {})
            mode_counts[outcome] = mode_counts.get(outcome, 0) + 1
            if outcome != "still_passing":
                changes.append({
                    "case": key[0], "base": key[1], "mode": key[2], "attempt": key[3],
                    "check": name, "outcome": outcome,
                    "before": old_check, "after": new_check,
                })
    return {"paired_trials": len(old_runs), "counts_by_mode": counts, "findings": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    try:
        report = compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
