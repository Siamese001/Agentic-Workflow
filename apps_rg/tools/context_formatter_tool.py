"""
Context Formatter Tool - Context formatting utility
Refactored from information_prepare_resume_context.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ContextFormatterTool(BaseRGEngine):
    """
    Formats context data for resume generation.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="TOOLS.CONTEXT_FORMATTER")

    async def execute(self, raw_context: dict[str, Any]) -> str:
        """
        Format context into structured string.
        """
        formatted_sections = []

        # Format job description
        if raw_context.get("job_description"):
            formatted_sections.append(f"JOB DESCRIPTION:\n{raw_context['job_description']}\n")

        # Format candidate profile
        if raw_context.get("candidate_profile"):
            profile = raw_context["candidate_profile"]
            formatted_sections.append("CANDIDATE PROFILE:")
            formatted_sections.append(f"  Role: {profile.get('role', 'N/A')}")
            formatted_sections.append(f"  Industry: {profile.get('industry', 'N/A')}")
            formatted_sections.append(f"  Years: {profile.get('years_experience', 'N/A')}\n")

        # Format requirements
        if raw_context.get("requirements"):
            formatted_sections.append(f"REQUIREMENTS:\n{raw_context['requirements']}\n")

        formatted_text = "\n".join(formatted_sections)

        self.record_pass(f"Formatted context: {len(formatted_text)} chars")
        return formatted_text
