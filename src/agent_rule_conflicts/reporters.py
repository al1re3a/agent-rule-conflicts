from __future__ import annotations

import json
from pathlib import Path

from .models import ScanResult


def render_text(result: ScanResult, color: bool = False) -> str:
    lines: list[str] = []
    for finding in result.findings:
        primary = finding.primary
        location = f"{primary.path.relative_to(result.root).as_posix()}:{primary.line}"
        lines.append(
            f"{location}: {finding.severity} {finding.rule_id} "
            f"({finding.confidence} confidence) {finding.message}"
        )
        lines.append(f"  deny: {primary.text}")
        if finding.related is not None:
            related = finding.related
            related_location = f"{related.path.relative_to(result.root).as_posix()}:{related.line}"
            lines.append(f"  require: {related.text} [{related_location}]")
    if not lines:
        lines.append("No conflicting agent instructions found.")
    lines.append(
        f"Scanned {len(result.files)} file(s), extracted {len(result.directives)} directive(s), "
        f"found {len(result.findings)} conflict(s)."
    )
    return "\n".join(lines) + "\n"


def render_json(result: ScanResult) -> str:
    return json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n"


def render_sarif(result: ScanResult) -> str:
    sarif_results: list[dict[str, object]] = []
    for finding in result.findings:
        primary = finding.primary
        item: dict[str, object] = {
            "ruleId": finding.rule_id,
            "level": "error" if finding.severity == "error" else "warning",
            "message": {"text": finding.message},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": primary.path.relative_to(result.root).as_posix()},
                    "region": {"startLine": primary.line},
                }
            }],
            "properties": {"confidence": finding.confidence},
        }
        if finding.related is not None:
            related = finding.related
            item["relatedLocations"] = [{
                "id": 1,
                "message": {"text": "Conflicting instruction"},
                "physicalLocation": {
                    "artifactLocation": {"uri": related.path.relative_to(result.root).as_posix()},
                    "region": {"startLine": related.line},
                },
            }]
        sarif_results.append(item)

    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "agent-rule-conflicts",
                    "informationUri": "https://github.com/al1re3a/agent-rule-conflicts",
                    "rules": [{
                        "id": "ARC001",
                        "shortDescription": {"text": "Conflicting agent instructions"},
                        "help": {"text": "Keep one authoritative instruction or clarify non-overlapping scope."},
                        "defaultConfiguration": {"level": "error"},
                    }],
                }
            },
            "results": sarif_results,
        }],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render(result: ScanResult, output_format: str) -> str:
    if output_format == "json":
        return render_json(result)
    if output_format == "sarif":
        return render_sarif(result)
    return render_text(result)
