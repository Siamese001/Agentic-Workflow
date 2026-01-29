"""
Experience Weighting Engine - Experience relevance weighting
Refactored from weight_experience_match.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ExperienceWeightingEngine(BaseRGEngine):
    """
    Weights experience sections by relevance to target role.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.EXPERIENCE_WEIGHTING")

    async def execute(
        self, experiences: list[dict[str, Any]], target_role: str
    ) -> list[dict[str, Any]]:
        """
        Calculate relevance weights for experience sections.
        """
        self._mcp_audit("experience_weighting")

        weighted_experiences = []

        for exp in experiences:
            weight = self._calculate_relevance(exp, target_role)
            exp["relevance_weight"] = weight
            weighted_experiences.append(exp)

        # Sort by weight
        weighted_experiences.sort(key=lambda x: x["relevance_weight"], reverse=True)

        self.record_pass(f"Weighted {len(weighted_experiences)} experiences")
        return weighted_experiences

    def _calculate_relevance(self, experience: dict[str, Any], target_role: str) -> float:
        """Calculate relevance score."""
        score = 0.5  # Base score

        title = experience.get("title", "").lower()
        target_lower = target_role.lower()

        # Exact role match
        if target_lower in title:
            score += 0.5

        # Related keywords
        related_keywords = ["senior", "lead", "principal", "staff"]
        if any(kw in title for kw in related_keywords):
            score += 0.2

        return min(score, 1.0)
