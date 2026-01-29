"""
Ranking Refiner Engine - Adjusts rankings based on JD
Refactored from RefineResumeRanking.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class RankingRefinerEngine(BaseRGEngine):
    """
    Refines section rankings based on JD analysis.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.RANKING_REFINER")

    async def execute(self, initial_ranking: list[str], jd_analysis: dict[str, Any]) -> list[str]:
        """
        Refine section ranking based on JD priorities.
        """
        self._mcp_audit("ranking_refinement")

        refined_ranking = initial_ranking.copy()

        # Boost sections based on JD emphasis
        if jd_analysis.get("technical_heavy"):
            if "skills" in refined_ranking:
                refined_ranking.remove("skills")
                refined_ranking.insert(0, "skills")

        if jd_analysis.get("leadership_heavy"):
            if "summary" in refined_ranking:
                refined_ranking.remove("summary")
                refined_ranking.insert(0, "summary")

        self.record_pass("Ranking refined based on JD analysis")
        return refined_ranking
