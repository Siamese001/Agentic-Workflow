"""
Skill Similarity Tool - Skill similarity computation
Refactored from compute_skill_similarity.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class SkillSimilarityTool(BaseRGEngine):
    """
    Computes similarity between skill sets.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="TOOLS.SKILL_SIMILARITY")

    async def execute(self, skills_a: list[str], skills_b: list[str]) -> float:
        """
        Calculate Jaccard similarity between skill sets.
        """
        set_a = {s.lower() for s in skills_a}
        set_b = {s.lower() for s in skills_b}

        if not set_a or not set_b:
            return 0.0

        intersection = len(set_a & set_b)
        union = len(set_a | set_b)

        similarity = intersection / union if union > 0 else 0.0

        self.record_pass(f"Skill similarity: {similarity:.2f}")
        return similarity
