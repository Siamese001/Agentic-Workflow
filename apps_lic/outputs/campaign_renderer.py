"""
Campaign Renderer — Renders CampaignResult as JSON/Markdown.

SVP Standards:
- Deterministic output
- Full provenance
- Multiple format support
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_lic.types import CampaignResult, CampaignRunSummary

_log = logging.getLogger(__name__)


class CampaignRenderer:
    """Renderer for campaign results."""

    def render_json(self, result: CampaignResult) -> str:
        """Render result as formatted JSON."""
        return json.dumps(result.model_dump(), indent=2, default=str)

    def render_markdown(self, result: CampaignResult) -> str:
        """Render result as Markdown report."""
        status = "✅ PASSED" if result.passed_gate else "❌ FAILED"
        lines = [
            "# LIC Campaign Report",
            "",
            f"**Campaign ID:** {result.campaign_id}",
            f"**Status:** {result.status}",
            f"**Gate Status:** {status}",
            f"**Overall Score:** {result.overall_score}/10",
            "",
            "## Drafts",
            f"- Generated: {len(result.drafts)}",
            f"- Validated: {len(result.validations)}",
            "",
        ]

        for i, draft in enumerate(result.drafts, 1):
            lines.extend([f"### Draft {i}", "", "```", draft.draft[:500], "```", ""])

        if result.gate_violations:
            lines.extend(["## Gate Violations", ""])
            for violation in result.gate_violations:
                lines.append(f"- ⚠️ {violation}")
            lines.append("")

        if result.error:
            lines.extend(["## Error", "", f"```\n{result.error}\n```", ""])

        return "\n".join(lines)

    def render_compact(self, result: CampaignResult) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "campaign_id": result.campaign_id,
            "status": result.status,
            "score": result.overall_score,
            "passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "drafts": len(result.drafts),
        }


class CampaignSummaryRenderer:
    """Renderer for campaign run summaries."""

    def render_json(self, summary: CampaignRunSummary) -> str:
        """Render summary as formatted JSON."""
        return json.dumps(summary.to_dict(), indent=2, default=str)

    def render_markdown(self, summary: CampaignRunSummary) -> str:
        """Render summary as Markdown report."""
        lines = [
            "# Campaign Run Summary",
            "",
            f"**Trace ID:** {summary.trace_id}",
            f"**Application:** {summary.app} v{summary.version}",
            f"**Status:** {summary.status}",
            "",
            "## Results",
            "",
            f"- Drafts Generated: {summary.drafts_generated}",
            f"- Drafts Validated: {summary.drafts_validated}",
            f"- Overall Score: {summary.overall_score}/10",
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

    def render_compact(self, summary: CampaignRunSummary) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": summary.trace_id,
            "status": summary.status,
            "score": summary.overall_score,
            "passed": len(summary.gate_violations) == 0 and not summary.error,
            "violations": len(summary.gate_violations),
        }
