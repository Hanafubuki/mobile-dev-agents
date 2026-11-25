"""Exercise the harness with deterministic adapters and external checks."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("run.py").resolve()


def main():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        repo = root / "app"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "feature.txt").write_text("old\n")
        (repo / "existing.txt").write_text("keep\n")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Evaluation", "-c", "user.email=eval@example.test",
             "commit", "-qm", "Fixture base"], cwd=repo, check=True,
        )
        adapter = root / "adapter.py"
        adapter.write_text(
            "import sys\nfrom pathlib import Path\n"
            "assert not Path('checks.py').exists()\n"
            "assert Path('feature.txt').read_text() == 'old\\n'\n"
            "if sys.stdin.read().startswith('/cto '):\n"
            "    Path('feature.txt').write_text('new\\n')\n"
            "    Path('new.txt').write_text('created\\n')\n"
            "    Path('.evaluation-metrics.json').write_text('{\"cost_usd\": 0.1}')\n"
            "else:\n    Path('existing.txt').unlink()\n"
        )
        checker = root / "checks.py"
        checker.write_text(
            "import sys\nfrom pathlib import Path\n"
            "assert not Path('.evaluation-metrics.json').exists()\n"
            "if sys.argv[1] == 'acceptance':\n"
            "    assert Path('feature.txt').read_text() == 'new\\n'\n"
            "    assert Path('new.txt').read_text() == 'created\\n'\n"
            "else:\n    assert Path('existing.txt').read_text() == 'keep\\n'\n"
        )
        command = [sys.executable, str(adapter)]
        config = root / "config.json"
        config.write_text(json.dumps({
            "repository": str(repo),
            "adapters": {"single": command, "pipeline": command},
            "cases": [{
                "id": "fixture", "base": "HEAD", "ticket": "Change the fixture",
                "acceptance": [sys.executable, str(checker), "acceptance"],
                "regression": [sys.executable, str(checker), "regression"],
            }],
        }))
        output = root / "results"
        subprocess.run(
            [sys.executable, str(SCRIPT), str(config), "--output", str(output),
             "--repetitions", "2"], check=True,
        )
        report = json.loads((output / "report.json").read_text())
        assert [row["mode"] for row in report["runs"]] == [
            "single", "pipeline", "pipeline", "single",
        ]
        assert len({row["base"] for row in report["runs"]}) == 1
        assert report["summary"]["single"]["regression_failures"] == 2
        assert report["summary"]["pipeline"]["successful_runs"] == 2
        assert report["summary"]["pipeline"]["median_cost_usd"] == 0.1
        assert (repo / "feature.txt").read_text() == "old\n"
        print("Harness self-test passed.")


if __name__ == "__main__":
    main()
