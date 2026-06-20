"""Hardening rule generator — emits actionable rules from delta analysis.

Plan: ``.codex/plans/apps-architect-pattern-hardening-d7e4f9.md`` W3.P3.

Consumes a DeltaReport and generates markdown hardening rules using the
template at ``templates/hardening_rule.md``.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import (
    DeltaEntry,
    DeltaReport,
    DeltaType,
    Severity,
)

_log = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


def _load_template() -> str:
    tp = _TEMPLATE_DIR / "hardening_rule.md"
    if tp.exists():
        return tp.read_text(encoding="utf-8")
    return ""


def _render_template(template: str, variables: dict[str, str]) -> str:
    result = template
    for key, value in variables.items():
        result = result.replace("{{ " + key + " }}", value)
        result = result.replace("{{" + key + "}}", value)
    return result


def _make_rule_id(pattern_hash: str) -> str:
    suffix = hashlib.sha256(
        f"{pattern_hash}:{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:6]
    return f"architect-{pattern_hash}-{suffix}"


def _format_applies_to(entry: DeltaEntry) -> str:
    ref = entry.pattern.source_ref
    if ref.startswith("adg:"):
        return "agentic_core/**/*.py"
    if ref.endswith(".md"):
        return ref
    if ref.endswith(".py"):
        return ref
    return "**/*.py"


def _severity_for_delta(delta_type: DeltaType) -> Severity:
    return {
        DeltaType.MISSING_PATTERN: Severity.RECOMMENDED,
        DeltaType.DRIFT_DETECTED: Severity.RECOMMENDED,
        DeltaType.STALE_PATTERN: Severity.ADVISORY,
        DeltaType.NEW_PATTERN: Severity.ADVISORY,
    }.get(delta_type, Severity.ADVISORY)


class RuleGenerator:
    """Generates hardening rules from a DeltaReport."""

    def __init__(self) -> None:
        self._template = _load_template()

    def generate(self, report: DeltaReport) -> Tuple[str, ...]:
        rules: list[str] = []
        for entry in report.entries:
            if entry.delta_type == DeltaType.NEW_PATTERN and "No action needed" in entry.recommendation:
                continue
            rule = self._generate_one(entry)
            rules.append(rule)
        return tuple(rules)

    def _generate_one(self, entry: DeltaEntry) -> str:
        severity = _severity_for_delta(entry.delta_type)
        variables = {
            "rule_id": _make_rule_id(entry.pattern.pattern_id),
            "pattern_source": entry.pattern.source_ref,
            "delta_type": entry.delta_type.value,
            "severity": severity.value,
            "applies_to": _format_applies_to(entry),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "detection": f"Pattern '{entry.pattern.summary}' detected via apps_architect scan.",
            "current_state": entry.current_state,
            "recommended_pattern": entry.recommendation,
            "migration_path": (
                f"1. Review pattern source: {entry.pattern.source_ref}\n"
                f"2. Compare current state against canonical pattern\n"
                f"3. Apply recommended changes\n"
                f"4. Verify with ADG health check"
            ),
        }
        return _render_template(self._template, variables)

    def generate_summary(self, report: DeltaReport) -> str:
        lines = [
            f"# Delta Summary",
            f"",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            f"",
            f"| Metric | Count |",
            f"|--------|-------|",
            f"| Total patterns | {report.total_patterns} |",
            f"| New patterns | {report.new_count} |",
            f"| Stale patterns | {report.stale_count} |",
            f"| Missing patterns | {report.missing_count} |",
            f"| Drift detected | {report.drift_count} |",
        ]
        return "\n".join(lines)


__all__ = ["RuleGenerator"]
