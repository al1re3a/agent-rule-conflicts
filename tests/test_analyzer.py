from pathlib import Path
import unittest

from agent_rule_conflicts.analyzer import analyze
from agent_rule_conflicts.discovery import discover

FIXTURES = Path(__file__).parent / "fixtures"


def analyze_fixture(name: str):
    root = (FIXTURES / name).resolve()
    return analyze(root, discover(root))


class AnalyzerTests(unittest.TestCase):
    def test_detects_an_explicit_cross_file_conflict(self) -> None:
        result = analyze_fixture("conflict")
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].rule_id, "ARC001")
        self.assertEqual(result.findings[0].confidence, "high")

    def test_detects_conflicting_directives_inside_one_file(self) -> None:
        result = analyze_fixture("same_file")
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].primary.path, result.findings[0].related.path)

    def test_does_not_flag_different_tools(self) -> None:
        self.assertEqual(analyze_fixture("different_tools").findings, [])

    def test_does_not_flag_same_polarity(self) -> None:
        self.assertEqual(analyze_fixture("same_polarity").findings, [])

    def test_detects_contained_command_phrase(self) -> None:
        result = analyze_fixture("command_conflict")
        self.assertEqual(len(result.findings), 1)
        self.assertIn("python -m unittest", result.findings[0].message)


if __name__ == "__main__":
    unittest.main()
