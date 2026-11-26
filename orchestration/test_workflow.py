import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from workflow import build_workflow


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = str(Path(directory.name) / "checkpoints.sqlite")
        self.config = {"configurable": {"thread_id": "case"}, "recursion_limit": 100}
        self.input = {
            "ticket": "Staff directory", "workspace": directory.name,
            "thread_id": "case", "scope": "both", "api_scope": "changed",
        }
        self.roles = []

    def invoke(self, input_data, replies=None, budget=2):
        def runner(request, workspace):
            role = request["role"]
            self.roles.append(role)
            if replies and replies.get(role):
                return replies[role].pop(0)
            if role.endswith("-planner"):
                return {"status": "pass", "slices": ["1", "2"]}
            return {"status": "pass"}

        with SqliteSaver.from_conn_string(self.db) as saver:
            return build_workflow(runner, saver, budget).invoke(input_data, self.config)

    def test_human_approval_and_backend_integration_repair(self):
        first = self.invoke(self.input)
        self.assertIn("__interrupt__", first)
        self.assertEqual(self.roles, ["cto-intake"])
        result = self.invoke(Command(resume="approve"), {
            "cross-stack-verifier": [{"status": "fail", "owner": "backend"}],
        })
        self.assertEqual(result["status"], "completed")
        self.assertEqual(self.roles[-6:], [
            "be-developer", "be-tester", "be-reviewer", "cto-accept",
            "cross-stack-verifier", "cto-accept",
        ])
        self.assertLess(self.roles.index("be-reviewer"), self.roles.index("fe-designer"))
        self.assertEqual(self.roles.count("fe-developer"), 2)

    def test_blocked_stage_resumes_without_replaying_earlier_work(self):
        self.input.update(scope="frontend", api_scope="none")
        self.invoke(self.input)
        result = self.invoke(Command(resume="approve"), {
            "fe-tester": [{"status": "blocked", "reason": "Missing simulator"}],
        })
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(self.roles[-1], "fe-tester")
        result = self.invoke(Command(resume="retry"))
        self.assertEqual(result["status"], "completed")
        self.assertEqual(self.roles.count("fe-designer"), 1)
        self.assertNotIn("cross-stack-verifier", self.roles)

    def test_repair_budget_exhaustion(self):
        self.input.update(scope="frontend", api_scope="existing")
        self.invoke(self.input)
        result = self.invoke(Command(resume="approve"), {
            "cross-stack-verifier": [{"status": "fail", "owner": "frontend"}] * 3,
        }, budget=2)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["pause"]["repairs_used"], 2)
        self.assertEqual(self.roles.count("cross-stack-verifier"), 3)
        self.assertEqual(self.invoke(Command(resume="cancel"))["status"], "cancelled")


if __name__ == "__main__":
    unittest.main()
