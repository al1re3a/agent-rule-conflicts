from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from agent_rule_conflicts.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_high_conflict_returns_one(self) -> None:
        with redirect_stdout(StringIO()):
            self.assertEqual(main([str(FIXTURES / "conflict")]), 1)

    def test_never_threshold_returns_zero(self) -> None:
        with redirect_stdout(StringIO()):
            self.assertEqual(main([str(FIXTURES / "conflict"), "--fail-on", "never"]), 0)

    def test_json_report_on_stdout(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main([str(FIXTURES / "conflict"), "--format", "json", "--fail-on", "never"]),
                0,
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["summary"]["files"], 2)

    def test_output_path_is_written(self) -> None:
        output = FIXTURES / "report.json"
        with patch.object(Path, "write_text") as write_text:
            self.assertEqual(main([str(FIXTURES / "clean"), "--output", str(output)]), 0)
        write_text.assert_called_once()

    def test_missing_path_returns_two(self) -> None:
        with redirect_stderr(StringIO()):
            self.assertEqual(main(["definitely-missing-rule-directory"]), 2)


if __name__ == "__main__":
    unittest.main()
