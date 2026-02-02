"""
Achievement Prioritizer Engine - Impact sorting
Refactored from prioritize_achievements.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base.BaseRGEngine import BaseRGEngine

Logger = logging.getLogger(__name__)


class AchievementPrioritizerEngine(BaseRGEngine):
    """
    Prioritizes achievements by impact and relevance.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.ACHIEVEMENT_PRIORITIZER")

    async def execute(self, achievements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Sort achievements by impact score.
        """
        self._mcp_audit("achievement_prioritization")

        # Score each achievement
        scored = []
        for achievement in achievements:
            score = self._calculate_impact(achievement)
            scored.append((achievement, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        prioritized = [item for item, _ in scored]

        self.record_pass(f"Prioritized {len(prioritized)} achievements")
        return prioritized

    def _calculate_impact(self, achievement: dict[str, Any]) -> float:
        """Calculate impact score for achievement."""
        score = 0.0

        # Quantified metrics add value
        if achievement.get("quantified_metrics"):
            score += 0.5

        # Leadership indicators
        text = achievement.get("bullet_text", "").lower()
        if any(word in text for word in ["led", "managed", "directed"]):
            score += 0.3

        # Scale indicators
        if any(word in text for word in ["team", "organization", "department"]):
            score += 0.2

        return score
