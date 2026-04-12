"""
Section Renderer — Renders brief sections.

SVP Standards:
- Deterministic output
- Full provenance
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_exec.types import BriefSection

_log = logging.getLogger(__name__)


class SectionRenderer:
    """Renderer for individual brief sections."""

    def render_json(self, section: BriefSection) -> str:
        """Render section as formatted JSON."""
        return json.dumps(section.model_dump(), indent=2, default=str)

    def render_markdown(self, section: BriefSection) -> str:
        """Render section as Markdown."""
        lines = [
            f"# {section.heading}",
            "",
            section.body,
            "",
        ]

        if section.why_this_matters:
            lines.extend([f"**Why this matters:** {section.why_this_matters}", ""])

        if section.evidence_anchors:
            lines.extend(["## Evidence", ""])
            for anchor in section.evidence_anchors:
                lines.append(f"- {anchor}")
            lines.append("")

        lines.extend([f"*Word count: {section.word_count} | Deterministic: {section.is_deterministic}*", ""])

        return "\n".join(lines)

    def render_compact(self, section: BriefSection) -> dict[str, Any]:
        """Render as compact dict."""
        return {
            "section_id": section.section_id,
            "heading": section.heading,
            "word_count": section.word_count,
            "is_deterministic": section.is_deterministic,
            "evidence_count": len(section.evidence_anchors),
            "has_significance": bool(section.why_this_matters),
        }

    def render_html(self, section: BriefSection) -> str:
        """Render section as HTML."""
        lines = [
            f"<h1>{section.heading}</h1>",
            "",
            f"<p>{section.body.replace(chr(10), '</p><p>')}</p>",
            "",
        ]

        if section.why_this_matters:
            lines.extend([f"<p><strong>Why this matters:</strong> {section.why_this_matters}</p>", ""])

        if section.evidence_anchors:
            lines.extend(["<h2>Evidence</h2>", "<ul>"])
            for anchor in section.evidence_anchors:
                lines.append(f"<li>{anchor}</li>")
            lines.extend(["</ul>", ""])

        lines.append(
            f"<p><em>Word count: {section.word_count} | Deterministic: {section.is_deterministic}</em></p>"
        )

        return "\n".join(lines)
