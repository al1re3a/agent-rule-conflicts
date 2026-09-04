import json
from pathlib import Path
import unittest

from agent_rule_conflicts.analyzer import analyze
from agent_rule_conflicts.discovery import discover
from agent_rule_conflicts.reporters import render_json, render_sarif, render_text

FIXTURES = Path(__file__).parent / "fixtures"


class ReporterTests(unittest.TestCase):
    def result(self):
        root = (FIXTURES / "conflict").resolve()
        return analyze(root, discover(root))

    def test_text_contains_both_locations(self) -> None:
        output = render_text(self.result())
        self.assertIn("CLAUDE.md:1", output)
        self.assertIn("AGENTS.md:1", output)
        self.assertIn("ARC001", output)

    def test_json_is_machine_readable(self) -> None:
        payload = json.loads(render_json(self.result()))
        self.assertEqual(payload["summary"]["findings"], 1)
        self.assertEqual(payload["findings"][0]["rule_id"], "ARC001")

    def test_sarif_has_locations_and_rule_metadata(self) -> None:
        payload = json.loads(render_sarif(self.result()))
        run = payload["runs"][0]
        self.assertEqual(run["tool"]["driver"]["name"], "agent-rule-conflicts")
        self.assertEqual(run["results"][0]["ruleId"], "ARC001")
        self.assertEqual(len(run["results"][0]["relatedLocations"]), 1)

    def test_clean_text_is_explicit(self) -> None:
        root = (FIXTURES / "clean").resolve()
        output = render_text(analyze(root, discover(root)))
        self.assertIn("No conflicting agent instructions found", output)


if __name__ == "__main__":
    unittest.main()
