from pathlib import Path
import unittest

from agent_rule_conflicts.discovery import discover

FIXTURES = Path(__file__).parent / "fixtures"


class DiscoveryTests(unittest.TestCase):
    def test_finds_supported_files_and_ignores_dependencies(self) -> None:
        root = FIXTURES / "discovery"
        relative = {path.relative_to(root.resolve()).as_posix() for path in discover(root)}
        self.assertEqual(relative, {
            ".claude/rules/quality.md",
            ".cursor/rules/testing.mdc",
            ".github/copilot-instructions.md",
            ".github/instructions/python.instructions.md",
            "AGENTS.md",
            "nested/CLAUDE.md",
        })

    def test_accepts_a_supported_single_file(self) -> None:
        path = (FIXTURES / "conflict" / "AGENTS.md").resolve()
        self.assertEqual(discover(path), [path])

    def test_returns_empty_for_unsupported_single_file(self) -> None:
        path = FIXTURES / "discovery" / "README.md"
        self.assertEqual(discover(path), [])

    def test_missing_path_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            discover(Path("definitely-missing-rule-directory"))


if __name__ == "__main__":
    unittest.main()
