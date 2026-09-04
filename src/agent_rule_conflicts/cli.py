from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .analyzer import analyze
from .discovery import discover
from .reporters import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-rule-conflicts",
        description="Find contradictory instructions across AI coding-agent rule files.",
    )
    parser.add_argument("path", nargs="?", default=".", help="repository or instruction file")
    parser.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    parser.add_argument("--output", type=Path, help="write the report to a file")
    parser.add_argument(
        "--fail-on",
        choices=("any", "high", "never"),
        default="high",
        help="finding threshold that returns exit code 1 (default: high)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _should_fail(confidences: list[str], threshold: str) -> bool:
    if threshold == "never":
        return False
    if threshold == "any":
        return bool(confidences)
    return "high" in confidences


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    target = Path(args.path).resolve()
    root = target.parent if target.is_file() else target
    try:
        files = discover(target)
        result = analyze(root, files)
        report = render(result, args.format)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
        else:
            sys.stdout.write(report)
        return 1 if _should_fail([item.confidence for item in result.findings], args.fail_on) else 0
    except (FileNotFoundError, OSError, UnicodeError) as error:
        print(f"agent-rule-conflicts: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
