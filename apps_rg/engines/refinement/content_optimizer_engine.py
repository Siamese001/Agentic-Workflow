"""
Content Optimizer Engine - Reorders bullet points for maximum impact
Refactored from optimize_content_order.py
Following Batch 4 specifications
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ContentOptimizerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reorders bullet points to maximize impact (Quantification-First).
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.OPTIMIZER")

    async def execute(self, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Optimize bullet ordering across all experience sections.
        """
        self._mcp_audit("content_optimization_start")

        optimized_sections = []
        for section in sections:
            bullets = section.get("bullets", [])
            if not bullets:
                optimized_sections.append(section)
                continue

            # 1. Sort by Metric Presence (Ported from optimize_content_order.py)
            # Achievements with '$' or '%' take priority
            optimized_bullets = sorted(
                bullets, key=lambda b: self._calculate_impact_score(b), reverse=True
            )

            section["bullets"] = optimized_bullets
            optimized_sections.append(section)

        self.record_pass("Content order optimized for maximum impact")
        return optimized_sections

    def _calculate_impact_score(self, bullet: dict[str, Any]) -> float:
        """
        Heuristic scoring for bullet impact.
        Base: 0.0
        +0.5 if quantified metrics exist
        +0.3 if canonical power verbs are present
        """
        score = 0.0
        text = bullet.get("bullet_text", "").lower()

        # Check for metrics (extracted in HOP-1)
        if bullet.get("quantified_metrics"):
            score += 0.5

        # Check for Power Verbs (from knowledge_base.py)
        power_verbs = ["led", "managed", "developed", "achieved", "drove"]
        if any(v in text for v in power_verbs):
            score += 0.3

        return score
