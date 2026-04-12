"""
Section Renderer — Renders proposal sections.

SVP Standards:
- Deterministic output
- Full provenance
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_rfp.types import ProposalSection

_log = logging.getLogger(__name__)


class SectionRenderer:
    """Renderer for individual proposal sections."""

    def render_json(self, section: ProposalSection) -> str:
        """Render section as formatted JSON."""
        return json.dumps(section.model_dump(), indent=2, default=str)

    def render_markdown(self, section: ProposalSection) -> str:
        """Render section as Markdown."""
        lines = [
            f"# {section.heading}",
            "",
            section.body,
            "",
        ]

        if section.assumptions:
            lines.extend(["## Assumptions", ""])
            for assumption in section.assumptions:
                lines.append(f"- **{assumption.assumption_id}:** {assumption.statement}")
            lines.append("")

        if section.evidence:
            lines.extend(["## Evidence", ""])
            for item in section.evidence:
                lines.append(f"- {item}")
            lines.append("")

        lines.extend([f"*Word count: {section.word_count} | Deterministic: {section.is_deterministic}*", ""])

        return "\n".join(lines)

    def render_compact(self, section: ProposalSection) -> dict[str, Any]:
        """Render as compact dict."""
        return {
            "section_id": section.section_id,
            "heading": section.heading,
            "word_count": section.word_count,
            "is_deterministic": section.is_deterministic,
            "assumptions_count": len(section.assumptions),
            "evidence_count": len(section.evidence),
        }

    def render_html(self, section: ProposalSection) -> str:
        """Render section as HTML."""
        lines = [
            f"<h1>{section.heading}</h1>",
            "",
            f"<p>{section.body.replace(chr(10), '</p><p>')}</p>",
            "",
        ]

        if section.assumptions:
            lines.extend(["<h2>Assumptions</h2>", "<ul>"])
            for assumption in section.assumptions:
                lines.append(f"<li><strong>{assumption.assumption_id}:</strong> {assumption.statement}</li>")
            lines.extend(["</ul>", ""])

        lines.append(
            f"<p><em>Word count: {section.word_count} | Deterministic: {section.is_deterministic}</em></p>"
        )

        return "\n".join(lines)
