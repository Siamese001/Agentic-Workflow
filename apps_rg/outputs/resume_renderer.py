"""
Resume Renderer — Renders ResumeResult as JSON/Markdown.

SVP Standards:
- Deterministic output
- Full provenance
- Multiple format support
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_rg.types import ResumeResult, ResumeRunSummary

_log = logging.getLogger(__name__)


class ResumeRenderer:
    """Renderer for resumes."""

    def render_json(self, result: ResumeResult) -> str:
        """Render result as formatted JSON."""
        return json.dumps(result.model_dump(), indent=2, default=str)

    def render_markdown(self, result: ResumeResult) -> str:
        """Render result as Markdown resume."""
        status = "✅ PASSED" if result.passed_gate else "❌ FAILED"
        lines = [
            f"# Resume: {result.candidate_name}",
            "",
            f"**Target Role:** {result.target_role}",
            f"**ATS Score:** {result.ats_score:.1f}/100",
            f"**Quality Score:** {result.quality_score:.0%}",
            f"**Gate Status:** {status}",
            "",
        ]

        if result.sections:
            lines.extend(["## Resume Sections", ""])
            for section in result.sections:
                if section.section_type == "summary":
                    lines.extend(["### Professional Summary", "", section.content, ""])
                elif section.section_type == "experience":
                    lines.extend(["### Experience", "", section.content, ""])
                elif section.section_type == "skills":
                    lines.extend(["### Skills", "", section.content, ""])
                elif section.section_type == "education":
                    lines.extend(["### Education", "", section.content, ""])
                else:
                    lines.extend([f"### {section.section_type.capitalize()}", "", section.content, ""])
                lines.append(f"*Word count: {section.word_count}*")
                lines.append("")

        if result.skill_matches:
            lines.extend(["## Skill Matches", ""])
            for match in result.skill_matches:
                score = match.match_score * 100
                lines.append(f"- **{match.skill_name}**: {score:.0f}% match")
            lines.append("")

        if result.gate_violations:
            lines.extend(["## Gate Violations", ""])
            for violation in result.gate_violations:
                lines.append(f"- ⚠️ {violation}")
            lines.append("")

        if result.error:
            lines.extend(["## Error", "", f"```\n{result.error}\n```", ""])

        return "\n".join(lines)

    def render_compact(self, result: ResumeResult) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": result.trace_id,
            "candidate_name": result.candidate_name,
            "target_role": result.target_role,
            "status": result.status,
            "ats_score": result.ats_score,
            "quality_score": result.quality_score,
            "passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "sections": len(result.sections),
            "skill_matches": len(result.skill_matches),
        }


class ResumeSummaryRenderer:
    """Renderer for resume run summaries."""

    def render_json(self, summary: ResumeRunSummary) -> str:
        """Render summary as formatted JSON."""
        return json.dumps(summary.to_dict(), indent=2, default=str)

    def render_markdown(self, summary: ResumeRunSummary) -> str:
        """Render summary as Markdown report."""
        status = "✅ PASSED" if not summary.gate_violations and not summary.error else "❌ FAILED"
        lines = [
            "# Resume Generation Summary",
            "",
            f"**Trace ID:** {summary.trace_id}",
            f"**Application:** {summary.app} v{summary.version}",
            f"**Candidate:** {summary.candidate_name}",
            f"**Target Role:** {summary.target_role}",
            f"**Status:** {summary.status}",
            f"**ATS Score:** {summary.ats_score:.1f}/100",
            f"**Quality Score:** {summary.quality_score:.0%}",
            f"**Overall:** {status}",
            "",
            "## Results",
            "",
            f"- Sections Generated: {summary.sections_generated}",
            f"- Skill Matches Found: {summary.skill_matches_found}",
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

        lines.extend(["## Provenance", "", f"```json\n{json.dumps(summary.provenance, indent=2, default=str)}\n```", ""])

        return "\n".join(lines)

    def render_compact(self, summary: ResumeRunSummary) -> dict[str, Any]:
        """Render as compact dict for embedding."""
        return {
            "trace_id": summary.trace_id,
            "candidate_name": summary.candidate_name,
            "target_role": summary.target_role,
            "status": summary.status,
            "ats_score": summary.ats_score,
            "quality_score": summary.quality_score,
            "passed": len(summary.gate_violations) == 0 and not summary.error,
            "violations": len(summary.gate_violations),
        }
