"""
Section Renderer — Renders research sections.

SVP Standards:
- Deterministic output
- Full provenance
"""

from __future__ import annotations

import json
import logging
from typing import Any

from apps_research.types import ResearchSection

_log = logging.getLogger(__name__)


class SectionRenderer:
    """Renderer for individual research sections."""

    def render_json(self, section: ResearchSection) -> str:
        """Render section as formatted JSON."""
        return json.dumps(section.model_dump(), indent=2, default=str)

    def render_markdown(self, section: ResearchSection) -> str:
        """Render section as Markdown."""
        lines = [
            f"# {section.heading}",
            "",
            section.body,
            "",
        ]

        if section.sources:
            lines.extend(["## Sources", ""])
            for source in section.sources:
                lines.append(f"- {source}")
            lines.append("")

        lines.extend(
            [
                f"*Word count: {section.word_count} | Deterministic: {section.is_deterministic} | Claim: {section.claim_type}*",
                "",
            ]
        )

        return "\n".join(lines)

    def render_compact(self, section: ResearchSection) -> dict[str, Any]:
        """Render as compact dict."""
        return {
            "section_id": section.section_id,
            "heading": section.heading,
            "word_count": section.word_count,
            "is_deterministic": section.is_deterministic,
            "claim_type": section.claim_type,
            "source_count": len(section.sources),
        }

    def render_html(self, section: ResearchSection) -> str:
        """Render section as HTML."""
        lines = [
            f"<h1>{section.heading}</h1>",
            "",
            f"<p>{section.body.replace(chr(10), '</p><p>')}</p>",
            "",
        ]

        if section.sources:
            lines.extend(["<h2>Sources</h2>", "<ul>"])
            for source in section.sources:
                lines.append(f"<li>{source}</li>")
            lines.extend(["</ul>", ""])

        lines.append(
            f"<p><em>Word count: {section.word_count} | Deterministic: {section.is_deterministic} | Claim: {section.claim_type}</em></p>"
        )

        return "\n".join(lines)
