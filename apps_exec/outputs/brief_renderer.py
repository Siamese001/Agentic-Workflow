"""
Brief Renderer — Renders ExecBriefResult as JSON/Markdown.

SVP Standards:
- Deterministic output
- Full provenance
- Multiple format support
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import json
import logging
from typing import Any

from apps_exec.types import ExecBriefResult, RunSummary

_log = logging.getLogger(__name__)


class BriefRenderer:
    """Renderer for executive briefs."""

    @traces_execute(layer="L1_COGNITION")
    def render_json(self, result: ExecBriefResult) -> str:
        """Render result as formatted JSON."""
        return json.dumps(result.model_dump(), indent=2, default=str)

    def render_markdown(self, result: ExecBriefResult) -> str:
        """Render result as Markdown brief."""
        status = "✅ PASSED" if result.passed_gate else "❌ FAILED"
        lines = [
            "# Executive Brief",
            "",
            f"**Audience:** {result.audience}",
            f"**Tone:** {result.tone}",
            f"**Status:** {result.status}",
            f"**Quality Score:** {result.quality_score:.0%}",
            f"**Gate Status:** {status}",
            "",
        ]

        if result.sections:
            lines.extend(["## Sections", ""])
            for section in result.sections:
                lines.extend([f"### {section.heading}", "", section.body, ""])
                if section.why_this_matters:
                    lines.extend([f"**Why this matters:** {section.why_this_matters}", ""])
                lines.append(
                    f"*Word count: {section.word_count} | Evidence: {len(section.evidence_anchors)}*"
                )
                lines.append("")

        if result.capabilities_extracted:
            lines.extend(["## Platform Capabilities", ""])
            for cap in result.capabilities_extracted:
                lines.extend(
                    [
                        f"### {cap.label}",
                        "",
                        f"**Description:** {cap.description}",
                        f"**Layer:** {cap.layer}",
                        "",
                    ]
                )

        if result.gate_violations:
            lines.extend(["## Gate Violations", ""])
            for violation in result.gate_violations:
                lines.append(f"- ⚠️ {violation}")
            lines.append("")

        if result.error:
            lines.extend(["## Error", "", f"```\n{result.error}\n```", ""])

        return "\n".join(lines)

    def render_compact(self, result: ExecBriefResult) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": result.trace_id,
            "audience": result.audience,
            "tone": result.tone,
            "status": result.status,
            "score": result.quality_score,
            "passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "sections": len(result.sections),
            "capabilities": len(result.capabilities_extracted),
        }


class BriefSummaryRenderer:
    """Renderer for brief run summaries."""

    def render_json(self, summary: RunSummary) -> str:
        """Render summary as formatted JSON."""
        return json.dumps(summary.to_dict(), indent=2, default=str)

    def render_markdown(self, summary: RunSummary) -> str:
        """Render summary as Markdown report."""
        status = "✅ PASSED" if not summary.gate_violations and not summary.error else "❌ FAILED"
        lines = [
            "# Brief Generation Summary",
            "",
            f"**Trace ID:** {summary.trace_id}",
            f"**Application:** {summary.app} v{summary.version}",
            f"**Status:** {summary.status}",
            f"**Quality Score:** {summary.quality_score:.0%}",
            f"**Overall:** {status}",
            "",
            "## Results",
            "",
            f"- Sections Generated: {summary.sections_generated}",
            f"- Capabilities Extracted: {summary.capabilities_extracted}",
            "",
        ]

        if summary.gate_violations:
            lines.extend(["## Gate Violations", ""])
            for violation in summary.gate_violations:
                lines.append(f"- ⚠️ {violation}")
            lines.append("")

        if summary.artifacts:
            lines.extend(["## Artifacts", ""])
            for artifact in summary.artifacts:
                lines.append(f"- {artifact}")
            lines.append("")

        if summary.error:
            lines.extend(["## Error", "", f"```\n{summary.error}\n```", ""])

        lines.extend(
            [
                "## Provenance",
                "",
                f"```json\n{json.dumps(summary.provenance, indent=2, default=str)}\n```",
                "",
            ]
        )

        return "\n".join(lines)

    def render_compact(self, summary: RunSummary) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": summary.trace_id,
            "status": summary.status,
            "score": summary.quality_score,
            "passed": len(summary.gate_violations) == 0 and not summary.error,
            "violations": len(summary.gate_violations),
        }


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_exec.outputs.brief_renderer', "module_loaded")
