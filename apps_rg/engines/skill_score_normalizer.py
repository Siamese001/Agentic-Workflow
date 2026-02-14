"""
Skill Score Normalizer - Score normalization
Refactored from normalize_skill_scores.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class SkillScoreNormalizer(BaseRGEngine):
    """
    Normalizes skill match scores across different scales.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.SKILL_NORMALIZER")

    async def execute(self, raw_scores: dict[str, float]) -> dict[str, float]:
        """
        Normalize skill scores to 0-1 range.
        """
        self._mcp_audit("score_normalization")

        if not raw_scores:
            return {}

        # Find min and max
        values = list(raw_scores.values())
        min_val = min(values)
        max_val = max(values)

        # Normalize
        normalized = {}
        if max_val > min_val:
            for skill, score in raw_scores.items():
                normalized[skill] = (score - min_val) / (max_val - min_val)
        else:
            # All scores are the same
            normalized = dict.fromkeys(raw_scores, 1.0)

        self.record_pass(f"Normalized {len(normalized)} skill scores")
        return normalized
