from __future__ import annotations

from itertools import combinations
from pathlib import Path

from .models import Directive, Finding, ScanResult
from .parser import parse_files


def _similarity(left: Directive, right: Directive) -> float:
    if not left.tokens or not right.tokens:
        return 0.0
    intersection = len(left.tokens & right.tokens)
    smaller = min(len(left.tokens), len(right.tokens))
    containment = intersection / smaller
    union = len(left.tokens | right.tokens)
    jaccard = intersection / union
    return max(containment, jaccard)


def _confidence(score: float) -> str:
    if score >= 0.9:
        return "high"
    if score >= 0.7:
        return "medium"
    return "low"


def analyze(root: Path, files: list[Path]) -> ScanResult:
    """Analyze discovered files and return deterministic cross-file findings."""
    root = root.resolve()
    directives = parse_files(files)
    findings: list[Finding] = []

    for left, right in combinations(directives, 2):
        if left.polarity == right.polarity:
            continue
        score = _similarity(left, right)
        if score < 0.62:
            continue
        require = left if left.polarity == "require" else right
        deny = right if left.polarity == "require" else left
        subject = require.action if require.action == deny.action else ", ".join(
            sorted(require.tokens & deny.tokens)
        )
        findings.append(
            Finding(
                rule_id="ARC001",
                severity="error",
                confidence=_confidence(score),
                message=f"Conflicting instructions for: {subject}",
                primary=deny,
                related=require,
            )
        )

    findings.sort(
        key=lambda finding: (
            finding.primary.path.relative_to(root).as_posix(),
            finding.primary.line,
            finding.related.path.relative_to(root).as_posix() if finding.related else "",
        )
    )
    return ScanResult(root=root, files=files, directives=directives, findings=findings)
