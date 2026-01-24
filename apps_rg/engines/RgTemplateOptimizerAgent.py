"""
RgTemplateOptimizerAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

from apps_rg.shared.core.agent_base import RGAgentBase


@dataclass
class RgTemplateOptimizerAgent(RGAgentBase):
    """
    Optimizes template selection based on job description.

    Analyzes:
    - Job requirements
    - Industry standards
    - Role level
    """

    TEMPLATE_RECOMMENDATIONS = {
        "technical": ["skills_first", "projects_prominent"],
        "executive": ["summary_prominent", "achievements_focused"],
        "creative": ["portfolio_linked", "visual_friendly"],
        "entry_level": ["education_first", "skills_prominent"],
    }

    def __post_init__(self) -> None:
        """Initialize template optimizer agent."""
        super().__post_init__()

    async def execute(self) -> None:
        self.log("Optimizing template selection...")

        job_desc = self.ctx.JobDescription
        if not job_desc:
            self.record_pass("No job description, using default template")
            return

        # Analyze job type
        job_type = self._detect_job_type(job_desc)
        recommendations = self.TEMPLATE_RECOMMENDATIONS.get(job_type, [])

        self.ctx.results["template_recommendations"] = {
            "job_type": job_type,
            "recommendations": recommendations,
        }

        self.record_pass(f"Template optimized for {job_type} role", data=recommendations)

    def _detect_job_type(self, job_desc: str) -> str:
        """Detect job type from description."""
        job_lower = job_desc.lower()

        technical_keywords = [
            "engineer",
            "developer",
            "programming",
            "software",
            "technical",
            "data",
            "cloud",
            "devops",
        ]
        executive_keywords = [
            "director",
            "vp",
            "vice president",
            "chief",
            "head of",
            "executive",
            "senior manager",
        ]
        creative_keywords = ["designer", "creative", "artist", "ux", "ui", "brand", "content"]
        entry_keywords = ["entry level", "junior", "associate", "intern", "graduate", "new grad"]

        if any(kw in job_lower for kw in executive_keywords):
            return "executive"
        elif any(kw in job_lower for kw in technical_keywords):
            return "technical"
        elif any(kw in job_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in job_lower for kw in entry_keywords):
            return "entry_level"

        return "technical"  # Default

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()
