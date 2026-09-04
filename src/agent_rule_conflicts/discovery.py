from __future__ import annotations

from pathlib import Path

EXACT_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "CODEX.md",
    "GEMINI.md",
    "SKILL.md",
}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "build",
    "dist",
    "examples",
    "node_modules",
    "test",
    "tests",
    "vendor",
}


def _is_instruction_file(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    parts = relative.parts
    posix = relative.as_posix()

    if path.name in EXACT_NAMES:
        return True
    if posix == ".github/copilot-instructions.md":
        return True
    if len(parts) >= 3 and parts[0:2] == (".github", "instructions"):
        return path.name.endswith(".instructions.md")
    if len(parts) >= 3 and parts[0:2] == (".cursor", "rules"):
        return path.suffix.lower() in {".md", ".mdc"}
    if len(parts) >= 3 and parts[0:2] == (".claude", "rules"):
        return path.suffix.lower() == ".md"
    return False


def discover(root: Path) -> list[Path]:
    """Return supported instruction files below *root* in stable order."""
    root = root.resolve()
    if root.is_file():
        return [root] if _is_instruction_file(root, root.parent) else []
    if not root.exists():
        raise FileNotFoundError(root)

    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts[:-1]):
            continue
        if _is_instruction_file(path, root):
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().lower())
