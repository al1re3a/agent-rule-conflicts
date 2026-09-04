from __future__ import annotations

import re
from pathlib import Path

from .models import Directive

DENY_PATTERNS = (
    r"\bnever\b",
    r"\bdo not\b",
    r"\bdon['’]t\b",
    r"\bmust not\b",
    r"\bmay not\b",
    r"\bcannot\b",
    r"\bcan['’]t\b",
    r"\bavoid\b",
    r"\bforbid(?:den)?\b",
)
REQUIRE_PATTERNS = (
    r"\balways\b",
    r"\bmust\b",
    r"\brequired\b",
    r"\brequire\b",
    r"\buse only\b",
    r"\bshould\b",
    r"\bprefer\b",
)
MARKER_RE = re.compile("|".join((*DENY_PATTERNS, *REQUIRE_PATTERNS)), re.IGNORECASE)
DENY_RE = re.compile("|".join(DENY_PATTERNS), re.IGNORECASE)
REQUIRE_RE = re.compile("|".join(REQUIRE_PATTERNS), re.IGNORECASE)
CODE_RE = re.compile(r"`([^`\n]+)`")
WORD_RE = re.compile(r"[a-z0-9][a-z0-9_.+/#:-]*", re.IGNORECASE)
STOP_WORDS = {
    "a", "an", "and", "any", "be", "by", "for", "from", "in", "is", "it",
    "of", "on", "or", "our", "please", "the", "this", "to", "when", "with",
    "you", "your", "always", "never", "must", "not", "do", "don't", "dont",
    "may", "cannot", "can't", "cant", "avoid", "required", "require", "should",
    "prefer", "only", "forbidden", "use", "using", "run", "execute",
}


def _clean_line(line: str) -> str:
    line = re.sub(r"^\s{0,3}(?:[-*+]\s+|\d+[.)]\s+|>\s*)", "", line)
    return re.sub(r"\s+", " ", line).strip()


def _action(text: str) -> tuple[str, frozenset[str]]:
    code = CODE_RE.findall(text)
    if code:
        candidate = " ".join(code)
    else:
        candidate = MARKER_RE.sub(" ", text)
    words = [word.lower().strip(".,;:()[]{}\"'") for word in WORD_RE.findall(candidate)]
    tokens = frozenset(word for word in words if word and word not in STOP_WORDS)
    action = re.sub(r"\s+", " ", candidate).strip().lower() if code else " ".join(sorted(tokens))
    return action, tokens


def parse_file(path: Path) -> list[Directive]:
    """Extract explicit English directives from one Markdown-like file."""
    directives: list[Directive] = []
    in_frontmatter = False
    in_fence = False

    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if number == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped or stripped.startswith("#"):
            continue

        text = _clean_line(raw)
        deny_match = DENY_RE.search(text)
        require_match = REQUIRE_RE.search(text)
        if not deny_match and not require_match:
            continue
        polarity = "deny" if deny_match else "require"
        action, tokens = _action(text)
        if not tokens:
            continue
        directives.append(Directive(path, number, text, polarity, action, tokens))

    return directives


def parse_files(paths: list[Path]) -> list[Directive]:
    directives: list[Directive] = []
    for path in paths:
        directives.extend(parse_file(path))
    return directives
