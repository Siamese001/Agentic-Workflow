"""
Effectiveness Scorer Engine - Impact scoring
Refactored from EvaluateResumeEffectiveness.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class EffectivenessScorer(BaseRGEngine):
    """
    Scores resume effectiveness based on impact metrics.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.EFFECTIVENESS")

    async def execute(self, resume_data: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate effectiveness score.
        """
        self._mcp_audit("effectiveness_scoring")
        score = 0.0
        metrics = {"quantified_achievements": 0, "leadership_indicators": 0, "technical_depth": 0}
        for section in resume_data.get("experience_sections", []):
            for bullet in section.get("bullets", []):
                text = bullet.get("bullet_text", "")
                if bullet.get("quantified_metrics"):
                    metrics["quantified_achievements"] += 1
                    score += 0.2
                if any(word in text.lower() for word in ["led", "managed", "directed"]):
                    metrics["leadership_indicators"] += 1
                    score += 0.15
                if any(word in text.lower() for word in ["architected", "engineered", "designed"]):
                    metrics["technical_depth"] += 1
                    score += 0.1
        result = {
            "effectiveness_score": min(score, 1.0),
            "metrics": metrics,
            "rating": "high" if score >= 0.8 else "medium" if score >= 0.5 else "low",
        }
        self.record_pass(f"Effectiveness score: {result['effectiveness_score']:.2f}", data=result)
        return result
