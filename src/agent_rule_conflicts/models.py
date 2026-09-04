from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Directive:
    path: Path
    line: int
    text: str
    polarity: str
    action: str
    tokens: frozenset[str]

    def as_dict(self, root: Path) -> dict[str, object]:
        return {
            "path": self.path.relative_to(root).as_posix(),
            "line": self.line,
            "text": self.text,
            "polarity": self.polarity,
            "action": self.action,
        }


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    confidence: str
    message: str
    primary: Directive
    related: Directive | None = None

    def as_dict(self, root: Path) -> dict[str, object]:
        value: dict[str, object] = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "confidence": self.confidence,
            "message": self.message,
            "primary": self.primary.as_dict(root),
        }
        if self.related is not None:
            value["related"] = self.related.as_dict(root)
        return value


@dataclass
class ScanResult:
    root: Path
    files: list[Path] = field(default_factory=list)
    directives: list[Directive] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "summary": {
                "files": len(self.files),
                "directives": len(self.directives),
                "findings": len(self.findings),
            },
            "findings": [finding.as_dict(self.root) for finding in self.findings],
        }
