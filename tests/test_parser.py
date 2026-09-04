from pathlib import Path
import unittest

from agent_rule_conflicts.parser import parse_file

FIXTURES = Path(__file__).parent / "fixtures" / "parser"


class ParserTests(unittest.TestCase):
    def test_extracts_required_and_denied_directives(self) -> None:
        directives = parse_file(FIXTURES / "AGENTS.md")
        self.assertEqual([item.polarity for item in directives], ["require", "deny"])
        self.assertEqual(directives[0].tokens, frozenset({"pytest"}))
        self.assertEqual(directives[1].line, 8)

    def test_ignores_frontmatter_fences_headings_and_prose(self) -> None:
        directives = parse_file(FIXTURES / "AGENTS.md")
        self.assertEqual(len(directives), 2)

    def test_normalizes_curly_apostrophe(self) -> None:
        directives = parse_file(FIXTURES / "CLAUDE.md")
        self.assertEqual(directives[0].polarity, "deny")
        self.assertEqual(directives[0].tokens, frozenset({"pip"}))


if __name__ == "__main__":
    unittest.main()
