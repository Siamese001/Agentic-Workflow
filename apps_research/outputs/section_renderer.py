"""
Section Renderer — Renders research sections.

SVP Standards:
- Deterministic output
- Full provenance
"""

from __future__ import annotations

import html
import json
import logging
from typing import Any

from apps_research.types import ResearchSection

_log = logging.getLogger(__name__)


class SectionRenderer:
    """Renderer for individual research sections."""

    @staticmethod
    def _safe_markdown(value: str) -> str:
        return value.replace("\x00", "").replace("\r\n", "\n").replace("```", "``\u200b`").strip()

    def render_json(self, section: ResearchSection) -> str:
        """Render section as formatted JSON."""
        return json.dumps(section.model_dump(), indent=2, sort_keys=True, ensure_ascii=False, default=str)

    def render_markdown(self, section: ResearchSection) -> str:
        """Render section as Markdown."""
        lines = [
            f"# {html.escape(section.heading)}",
            "",
            self._safe_markdown(section.body),
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
            f"<h1>{html.escape(section.heading)}</h1>",
            "",
            f"<p>{html.escape(self._safe_markdown(section.body)).replace(chr(10), '</p><p>')}</p>",
            "",
        ]

        if section.sources:
            lines.extend(["<h2>Sources</h2>", "<ul>"])
            for source in section.sources:
                lines.append(f"<li>{html.escape(str(source))}</li>")
            lines.extend(["</ul>", ""])

        lines.append(
            f"<p><em>Word count: {section.word_count} | Deterministic: {section.is_deterministic} | Claim: {section.claim_type}</em></p>"
        )

        return "\n".join(lines)
