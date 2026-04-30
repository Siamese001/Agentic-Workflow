"""
Section Renderer — Renders resume sections.

SVP Standards:
- Deterministic output
- Full provenance
"""

from __future__ import annotations

import html
import json
import logging
from typing import Any

from apps_rg.types import ResumeSection

_log = logging.getLogger(__name__)


class SectionRenderer:
    """Renderer for individual resume sections."""

    def render_json(self, section: ResumeSection) -> str:
        """Render section as formatted JSON."""
        return json.dumps(section.model_dump(), indent=2, default=str)

    def render_markdown(self, section: ResumeSection) -> str:
        """Render section as Markdown."""
        heading_map = {
            "summary": "Professional Summary",
            "experience": "Experience",
            "skills": "Skills",
            "education": "Education",
            "certifications": "Certifications",
        }
        heading = heading_map.get(section.section_type, section.section_type.capitalize())
        lines = [
            f"## {heading}",
            "",
            section.content,
            "",
            f"*Word count: {section.word_count}*",
            "",
        ]
        return "\n".join(lines)

    def render_compact(self, section: ResumeSection) -> dict[str, Any]:
        """Render as compact dict."""
        return {
            "section_id": section.section_id,
            "section_type": section.section_type,
            "word_count": section.word_count,
            "preview": section.content[:100] + "..." if len(section.content) > 100 else section.content,
        }

    def render_html(self, section: ResumeSection) -> str:
        """Render section as HTML."""
        heading_map = {
            "summary": "Professional Summary",
            "experience": "Experience",
            "skills": "Skills",
            "education": "Education",
            "certifications": "Certifications",
        }
        heading = heading_map.get(section.section_type, section.section_type.capitalize())
        lines = [
            f"<h2>{heading}</h2>",
            "",
            f'<div class="section">{html.escape(section.content).replace(chr(10), "<br/>")}</div>',
            "",
            f"<p><em>Word count: {section.word_count}</em></p>",
        ]
        return "\n".join(lines)


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_rg.outputs.section_renderer', "module_loaded")
