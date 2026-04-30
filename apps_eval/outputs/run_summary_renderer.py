"""
Run Summary Renderer — Renders EvalRunSummary as JSON/Markdown.

SVP Standards:
- Deterministic output
- Full provenance
- Multiple format support
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_eval.types import EvalRunSummary

_log = logging.getLogger(__name__)


class RunSummaryRenderer:
    """Renderer for evaluation run summaries."""

    def render_json(self, summary: EvalRunSummary) -> str:
        """Render summary as formatted JSON."""
        return json.dumps(summary.to_dict(), indent=2, default=str)

    def render_markdown(self, summary: EvalRunSummary) -> str:
        """Render summary as Markdown report."""
        lines = [
            "# Evaluation Run Summary",
            "",
            f"**Trace ID:** {summary.trace_id}",
            f"**Application:** {summary.app} v{summary.version}",
            f"**Status:** {summary.status}",
            "",
            "## Results",
            "",
            f"- Suites Run: {summary.suites_run}",
            f"- Scenarios Run: {summary.scenarios_run}",
            f"- Scenarios Passed: {summary.scenarios_passed}",
            f"- Overall Score: {summary.overall_score:.2%}",
            f"- Regressions Detected: {summary.regressions_detected}",
            "",
        ]

        if summary.gate_violations:
            lines.extend(
                [
                    "## Gate Violations",
                    "",
                ]
            )
            for violation in summary.gate_violations:
                lines.append(f"- ⚠️ {violation}")
            lines.append("")

        if summary.artifacts:
            lines.extend(
                [
                    "## Artifacts",
                    "",
                ]
            )
            for artifact in summary.artifacts:
                lines.append(f"- {artifact}")
            lines.append("")

        if summary.error:
            lines.extend(
                [
                    "## Error",
                    "",
                    f"```\n{summary.error}\n```",
                    "",
                ]
            )

        lines.extend(
            [
                "## Provenance",
                "",
                f"```json\n{json.dumps(summary.provenance, indent=2, default=str)}\n```",
                "",
            ]
        )

        return "\n".join(lines)

    def render_compact(self, summary: EvalRunSummary) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": summary.trace_id,
            "status": summary.status,
            "score": summary.overall_score,
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

_emit_records_telemetry_event("p4", 'apps_eval.outputs.run_summary_renderer', "module_loaded")
