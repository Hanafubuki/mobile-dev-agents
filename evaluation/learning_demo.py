"""Reproduce and fix a cross-stack contract failure using deterministic adapters."""

import json
import subprocess
import sys
from pathlib import Path

from compare import compare


HERE = Path(__file__).resolve().parent


def main(output):
    output = output.resolve()
    output.mkdir(parents=True)
    repo = output / "fixture"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "backend.py").write_text("def staff():\n    return {'staff': []}\n")
    (repo / "mobile.py").write_text("def names(payload):\n    return []\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Demo", "-c", "user.email=demo@example.test",
         "commit", "-qm", "Seed staff directory fixture"], cwd=repo, check=True,
    )
    checker = output / "check.py"
    checker.write_text(
        "import json, sys\n"
        "sys.path.insert(0, '.')\n"
        "from backend import staff\n"
        "from mobile import names\n"
        "payload = json.loads(json.dumps(staff()))\n"
        "if sys.argv[1] == 'acceptance':\n"
        "    assert names(payload) == ['Ari'], 'Wrong rendered staff list'\n"
        "else:\n"
        "    assert names({'staff': []}) == []\n"
    )
    adapter = output / "adapter.py"
    adapter.write_text(
        "import sys\nfrom pathlib import Path\n"
        "sys.stdin.read()\n"
        "Path('backend.py').write_text(\"def staff():\\n    return {'staff': [{'name': 'Ari'}]}\\n\")\n"
        "key = 'staff' if sys.argv[1] == 'verified' else 'items'\n"
        "Path('mobile.py').write_text(f\"def names(payload):\\n    return [r['name'] for r in payload.get({key!r}, [])]\\n\")\n"
    )
    old_adapter = [sys.executable, str(adapter), "original"]
    new_adapter = [sys.executable, str(adapter), "verified"]
    config = {
        "repository": str(repo),
        "experiment": {"type": "deterministic contract fixture"},
        "adapters": {"single": old_adapter, "pipeline": old_adapter},
        "cases": [{
            "id": "staff-directory", "base": "HEAD", "ticket": "Show staff names in the app.",
            "acceptance": [sys.executable, str(checker), "acceptance"],
            "regression": [sys.executable, str(checker), "regression"],
        }],
    }
    reports = []
    for variant, pipeline_adapter in (("before", old_adapter), ("after", new_adapter)):
        config["adapters"]["pipeline"] = pipeline_adapter
        settings = output / f"{variant}.json"
        settings.write_text(json.dumps(config))
        run_dir = output / variant
        subprocess.run(
            [sys.executable, str(HERE / "run.py"), str(settings), "--output", str(run_dir)],
            check=True,
        )
        reports.append(json.loads((run_dir / "report.json").read_text()))
    result = compare(*reports)
    (output / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    assert result["counts_by_mode"]["pipeline"].get("fixed") == 1
    assert result["counts_by_mode"]["single"].get("still_failing") == 1
    assert all("regressed" not in counts for counts in result["counts_by_mode"].values())
    print(f"Cross-stack learning demo passed. Evidence: {output / 'comparison.json'}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 evaluation/learning_demo.py NEW_OUTPUT_DIRECTORY")
    main(Path(sys.argv[1]))
