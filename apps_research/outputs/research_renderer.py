"""
Research Renderer — Renders ResearchResult as JSON/Markdown.

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

from apps_research.types import ResearchResult, ResearchRunSummary

_log = logging.getLogger(__name__)


class ResearchRenderer:
    """Renderer for research artifacts."""

    @staticmethod
    def _safe_markdown(value: str) -> str:
        return value.replace("\x00", "").replace("\r\n", "\n").replace("```", "``\u200b`").strip()

    @traces_execute(layer="L1_COGNITION")
    def render_json(self, result: ResearchResult) -> str:
        """Render result as formatted JSON."""
        return json.dumps(result.model_dump(), indent=2, sort_keys=True, ensure_ascii=False, default=str)

    def render_markdown(self, result: ResearchResult) -> str:
        """Render result as Markdown research report."""
        status = "✅ PASSED" if result.passed_gate else "❌ FAILED"
        lines = [
            f"# Research: {self._safe_markdown(result.topic)}",
            "",
            f"**Mode:** {self._safe_markdown(result.mode)}",
            f"**Status:** {self._safe_markdown(result.status)}",
            f"**Quality Score:** {result.quality_score:.0%}",
            f"**Gate Status:** {status}",
            "",
        ]

        if result.sections:
            lines.extend(["## Sections", ""])
            for section in result.sections:
                lines.extend(
                    [f"### {self._safe_markdown(section.heading)}", "", self._safe_markdown(section.body), ""]
                )
                lines.append(
                    f"*Word count: {section.word_count} | Sources: {len(section.sources)} | Claim: {section.claim_type}*"
                )
                lines.append("")

        if result.source_register:
            lines.extend(["## Source Register", ""])
            for source in result.source_register:
                lines.extend(
                    [
                        f"### {self._safe_markdown(source.title)}",
                        f"**Confidence:** {source.confidence:.0%}",
                        f"**Type:** {self._safe_markdown(source.claim_type)}",
                        f"**URL:** {self._safe_markdown(source.url)}",
                        "",
                    ]
                )

        if result.comparison_matrix:
            lines.extend(["## Comparison Matrix", ""])
            for row in result.comparison_matrix:
                lines.append(f"### {self._safe_markdown(row.subject)}")
                for dim, val in row.dimensions.items():
                    lines.append(f"- **{dim}:** {self._safe_markdown(val)}")
                lines.append("")

        if result.gate_violations:
            lines.extend(["## Gate Violations", ""])
            for violation in result.gate_violations:
                lines.append(f"- ⚠️ {self._safe_markdown(violation)}")
            lines.append("")

        if result.error:
            lines.extend(["## Error", "", f"```\n{self._safe_markdown(result.error)}\n```", ""])

        return "\n".join(lines)

    def render_compact(self, result: ResearchResult) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": result.trace_id,
            "topic": self._safe_markdown(result.topic),
            "mode": self._safe_markdown(result.mode),
            "status": self._safe_markdown(result.status),
            "score": result.quality_score,
            "passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "sections": len(result.sections),
            "sources": len(result.source_register),
        }


class ResearchSummaryRenderer:
    """Renderer for research run summaries."""

    @staticmethod
    def _safe_markdown(value: str) -> str:
        return value.replace("\x00", "").replace("\r\n", "\n").replace("```", "``\u200b`").strip()

    def render_json(self, summary: ResearchRunSummary) -> str:
        """Render summary as formatted JSON."""
        return json.dumps(summary.to_dict(), indent=2, sort_keys=True, ensure_ascii=False, default=str)

    def render_markdown(self, summary: ResearchRunSummary) -> str:
        """Render summary as Markdown report."""
        status = "✅ PASSED" if not summary.gate_violations and not summary.error else "❌ FAILED"
        lines = [
            "# Research Generation Summary",
            "",
            f"**Trace ID:** {summary.trace_id}",
            f"**Application:** {summary.app} v{summary.version}",
            f"**Topic:** {summary.topic}",
            f"**Mode:** {summary.mode}",
            f"**Status:** {summary.status}",
            f"**Quality Score:** {summary.quality_score:.0%}",
            f"**Overall:** {status}",
            "",
            "## Results",
            "",
            f"- Sections Generated: {summary.sections_generated}",
            f"- Sources Registered: {summary.sources_registered}",
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

    def render_compact(self, summary: ResearchRunSummary) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": summary.trace_id,
            "topic": summary.topic,
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

_emit_records_telemetry_event("p4", 'apps_research.outputs.research_renderer', "module_loaded")
