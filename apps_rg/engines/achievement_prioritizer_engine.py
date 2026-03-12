"""
Achievement Prioritizer Engine - Impact sorting
Refactored from prioritize_achievements.py
"""
from __future__ import annotations
import logging
from typing import Any
from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class AchievementPrioritizerEngine(BaseRGEngine):
    """
    Prioritizes achievements by impact and relevance.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id='REFINE.ACHIEVEMENT_PRIORITIZER')

    async def execute(self, achievements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Sort achievements by impact score.
        """
        self._mcp_audit('achievement_prioritization')
        scored = []
        for achievement in achievements:
            score = self._calculate_impact(achievement)
            scored.append((achievement, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        prioritized = [item for item, _ in scored]
        self.record_pass(f'Prioritized {len(prioritized)} achievements')
        return prioritized

    def _calculate_impact(self, achievement: dict[str, Any]) -> float:
        """Calculate impact score for achievement."""
        score = 0.0
        if achievement.get('quantified_metrics'):
            score += 0.5
        text = achievement.get('bullet_text', '').lower()
        if any((word in text for word in ['led', 'managed', 'directed'])):
            score += 0.3
        if any((word in text for word in ['team', 'organization', 'department'])):
            score += 0.2
        return score
