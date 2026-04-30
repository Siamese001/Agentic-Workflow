"""
Draft Renderer — Renders DraftPackage as JSON/Markdown.

SVP Standards:
- Deterministic output
- Full provenance
- Multiple format support
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_lic.types import DraftPackage, ValidationResult

_log = logging.getLogger(__name__)


class DraftRenderer:
    """Renderer for LIC drafts."""

    def render_json(self, draft_package: DraftPackage) -> str:
        """Render draft as formatted JSON."""
        return json.dumps(draft_package.model_dump(), indent=2, default=str)

    def render_markdown(self, draft_package: DraftPackage) -> str:
        """Render draft as Markdown report."""
        lines = [
            "# LIC Campaign Draft",
            "",
            "## Draft Content",
            "",
            "```",
            draft_package.draft,
            "```",
            "",
            "## Metadata",
            "",
            f"- **Version:** {draft_package.draft_version}",
            f"- **Trace ID:** {draft_package.trace_id}",
            f"- **Total Latency:** {draft_package.total_latency_ms}ms",
            f"- **Artifacts:** {len(draft_package.artifacts)}",
            "",
        ]

        if draft_package.artifacts:
            lines.extend(["## Artifacts", ""])
            for name, content in draft_package.artifacts.items():
                lines.extend([f"### {name}", "", f"```\n{content}\n```", ""])

        return "\n".join(lines)

    def render_compact(self, draft_package: DraftPackage) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "draft_preview": draft_package.draft[:100] + "..."
            if len(draft_package.draft) > 100
            else draft_package.draft,
            "artifacts_count": len(draft_package.artifacts),
            "total_latency_ms": draft_package.total_latency_ms,
            "version": draft_package.draft_version,
        }


class ValidationReportRenderer:
    """Renderer for validation reports."""

    def render_json(self, result: ValidationResult) -> str:
        """Render validation as formatted JSON."""
        return json.dumps(result.model_dump(), indent=2, default=str)

    def render_markdown(self, result: ValidationResult) -> str:
        """Render validation as Markdown report."""
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        lines = [
            "# Validation Report",
            "",
            f"**Status:** {status}",
            f"**Attempts:** {result.attempts}",
            f"**Latency:** {result.latency_ms}ms",
            f"**Version:** {result.validator_version}",
            "",
        ]

        if result.reasons:
            lines.extend(["## Issues", ""])
            for reason in result.reasons:
                lines.append(f"- {reason}")
            lines.append("")

        if result.qa_result:
            lines.extend(
                [
                    "## QA Result",
                    "",
                    f"```json\n{json.dumps(result.qa_result, indent=2, default=str)}\n```",
                    "",
                ],
            )

        return "\n".join(lines)

    def render_compact(self, result: ValidationResult) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "passed": result.passed,
            "issues_count": len(result.reasons),
            "attempts": result.attempts,
            "latency_ms": result.latency_ms,
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

_emit_records_telemetry_event("p4", 'apps_lic.outputs.draft_renderer', "module_loaded")
