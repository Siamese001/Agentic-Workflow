"""README assembler — builds modular README from scan results.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W4.P1.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import DeltaReport, Pattern, PatternCollection

_log = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


def _load_template(name: str) -> str:
    tp = _TEMPLATE_DIR / name
    return tp.read_text(encoding="utf-8") if tp.exists() else ""


def _render(template: str, variables: dict[str, str]) -> str:
    result = template
    for key, value in variables.items():
        result = result.replace("{{ " + key + " }}", value)
        result = result.replace("{{" + key + "}}", value)
    return result


def _build_catalog(patterns: Tuple[Pattern, ...]) -> str:
    by_type: dict[str, list[Pattern]] = {}
    for p in patterns:
        by_type.setdefault(p.pattern_type.value, []).append(p)
    lines: list[str] = []
    for ptype, pats in sorted(by_type.items()):
        lines.append(f"### {ptype} ({len(pats)})")
        for p in pats[:10]:
            lines.append(f"- **{p.summary[:80]}** — `{p.source_ref}`")
        if len(pats) > 10:
            lines.append(f"- ... and {len(pats) - 10} more")
        lines.append("")
    return "\n".join(lines)


def _build_delta(report: DeltaReport) -> str:
    return (
        f"| Metric | Count |\n"
        f"|--------|-------|\n"
        f"| Total patterns | {report.total_patterns} |\n"
        f"| New patterns | {report.new_count} |\n"
        f"| Stale patterns | {report.stale_count} |\n"
        f"| Missing patterns | {report.missing_count} |\n"
        f"| Drift detected | {report.drift_count} |"
    )


def _build_backlog(report: DeltaReport) -> str:
    actionable = [e for e in report.entries if e.delta_type.value != "NEW_PATTERN" or "No action" not in e.recommendation]
    if not actionable:
        return "No outstanding hardening recommendations."
    lines: list[str] = []
    for e in actionable[:15]:
        lines.append(f"- [{e.severity.value}] {e.recommendation[:100]}")
    if len(actionable) > 15:
        lines.append(f"- ... and {len(actionable) - 15} more")
    return "\n".join(lines)


def _build_changelog(collection: PatternCollection) -> str:
    return (
        f"- **{collection.scan_timestamp.isoformat()}**: "
        f"Scanned {len(collection.patterns)} patterns "
        f"(digest: `{collection.collection_digest}`)"
    )


class ReadmeAssembler:
    """Assembles a modular README from scan + delta results."""

    def __init__(self) -> None:
        self._template = _load_template("readme_template.md")

    def assemble(
        self,
        collection: PatternCollection,
        report: DeltaReport,
        executive_summary: str = "",
    ) -> str:
        now = datetime.now(timezone.utc).isoformat()
        variables = {
            "scan_timestamp": now,
            "executive_summary": executive_summary or (
                f"apps_architect scanned {len(collection.patterns)} patterns "
                f"across plans, rules, and core layers. "
                f"{report.new_count} new patterns, {report.drift_count} drift detected."
            ),
            "pattern_catalog": _build_catalog(collection.patterns),
            "delta_summary": _build_delta(report),
            "hardening_backlog": _build_backlog(report),
            "methodology_changelog": _build_changelog(collection),
        }
        return _render(self._template, variables)


__all__ = ["ReadmeAssembler"]
