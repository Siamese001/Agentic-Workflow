"""
Proposal Renderer — Renders RfpResult as JSON/Markdown.

SVP Standards:
- Deterministic output
- Full provenance
- Multiple format support
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_rfp.types import RfpResult, RfpRunSummary
from tqdm import tqdm

_log = logging.getLogger(__name__)


class ProposalRenderer:
    """Renderer for RFP proposals."""

    def render_json(self, result: RfpResult) -> str:
        """Render result as formatted JSON."""
        return json.dumps(
            result.model_dump() if hasattr(result, "model_dump") else result.dict(),
            indent=2,
            default=str,
        )

    def render_markdown(self, result: RfpResult) -> str:
        """Render result as Markdown proposal."""
        status = "✅ PASSED" if result.passed_gate else "❌ FAILED"
        lines = [
            "# AI-Generated RFP Proposal",
            "",
            f"**Industry:** {result.industry}",
            f"**Status:** {result.status}",
            f"**Quality Score:** {result.quality_score:.0%}",
            f"**Gate Status:** {status}",
            "",
        ]

        if result.sections:
            lines.extend(["## Proposal Sections", ""])
            for section in tqdm(result.sections, desc="Processing", unit="item"):
                lines.extend(
                    [
                        f"### {section.heading}",
                        "",
                        section.body,
                        "",
                        f"*Word count: {section.word_count}*",
                        "",
                    ]
                )

        if result.roadmap:
            lines.extend(["## Implementation Roadmap", ""])
            for phase in tqdm(result.roadmap, desc="Processing", unit="item"):
                lines.extend(
                    [
                        f"### Phase: {phase.name}",
                        "",
                        f"- Duration: {phase.duration_weeks} weeks",
                        "",
                        "#### Objectives",
                        "",
                    ]
                )
                for obj in phase.objectives:
                    lines.append(f"- {obj}")
                lines.append("")

        if result.risks:
            lines.extend(["## Risk Assessment", ""])
            for risk in tqdm(result.risks, desc="Processing", unit="item"):
                lines.extend(
                    [
                        f"### {risk.risk_id} ({risk.severity})",
                        "",
                        f"**Category:** {risk.category}",
                        f"**Description:** {risk.description}",
                        f"**Mitigation:** {risk.mitigation}",
                        f"**Owner:** {risk.owner}",
                        "",
                    ]
                )

        if result.assumptions:
            lines.extend(["## Assumptions", ""])
            for assumption in result.assumptions:
                lines.extend(
                    [
                        f"### {assumption.assumption_id}",
                        "",
                        f"**Statement:** {assumption.statement}",
                        f"**Basis:** {assumption.basis}",
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

    def render_compact(self, result: RfpResult) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": result.trace_id,
            "industry": result.industry,
            "status": result.status,
            "score": result.quality_score,
            "passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "sections": len(result.sections),
            "roadmap_phases": len(result.roadmap),
            "risks": len(result.risks),
        }


class ProposalSummaryRenderer:
    """Renderer for RFP run summaries."""

    def render_json(self, summary: RfpRunSummary) -> str:
        """Render summary as formatted JSON."""
        return json.dumps(summary.to_dict(), indent=2, default=str)

    def render_markdown(self, summary: RfpRunSummary) -> str:
        """Render summary as Markdown report."""
        status = "✅ PASSED" if not summary.gate_violations and not summary.error else "❌ FAILED"
        lines = [
            "# RFP Generation Summary",
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
            f"- Roadmap Phases: {summary.roadmap_phases}",
            f"- Risks Identified: {summary.risks_identified}",
            f"- Assumptions Declared: {summary.assumptions_declared}",
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

    def render_compact(self, summary: RfpRunSummary) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": summary.trace_id,
            "status": summary.status,
            "score": summary.quality_score,
            "passed": len(summary.gate_violations) == 0 and not summary.error,
            "violations": len(summary.gate_violations),
        }
