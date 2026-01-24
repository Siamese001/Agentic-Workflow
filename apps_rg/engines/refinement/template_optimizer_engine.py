"""
Template Optimizer Engine - Selects optimal presentation template
Refactored from RgTemplateOptimizerAgent.py
Following Batch 5 specifications
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class TemplateOptimizerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Selects the optimal presentation template based on Job/Candidate fit.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.TEMPLATE")
        # Heuristics moved to class constants or KB
        self.KEYWORDS = {
            "executive": ["director", "vp", "chief", "head of", "principal"],
            "technical": ["engineer", "developer", "architect", "data", "cloud"],
            "creative": ["designer", "ux", "ui", "artist", "brand"],
            "entry_level": ["junior", "intern", "associate", "graduate"],
        }

    async def execute(self, job_description: str) -> dict[str, Any]:
        """
        Recommend a template strategy based on JD analysis.
        """
        self._mcp_audit("template_optimization_start")

        if not job_description:
            self.record_fail("Empty JD provided for template optimization")
            return {"job_type": "default", "template": "standard_modern"}

        # 1. Detect Job Archetype
        job_type = self._detect_job_type(job_description)

        # 2. Retrieve Strategy from Config (No Magic Strings)
        # In legacy, this was hardcoded. Now we try to pull from config, else fallback.
        try:
            recs = self.config.config.qa_thresholds.get("template_map", {})
            strategy = recs.get(job_type, ["standard_modern"])
        except (AttributeError, KeyError):
            # Fallback for migration safety
            strategy = self._get_legacy_fallback(job_type)

        result = {
            "job_type": job_type,
            "recommended_templates": strategy,
            "rationale": f"Detected {job_type} keywords in JD",
        }

        self.record_pass(f"Selected template strategy: {job_type}", data=result)
        return result

    def _detect_job_type(self, text: str) -> str:
        """Score JD against archetype keywords."""
        text = text.lower()
        scores = {k: 0 for k in self.KEYWORDS}

        for category, keywords in self.KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    scores[category] += 1

        # Return category with max hits, default to 'technical' if tie/zero
        best_match = max(scores, key=scores.get)
        return best_match if scores[best_match] > 0 else "technical"

    def _get_legacy_fallback(self, job_type: str) -> list[str]:
        """Ported legacy recommendations for failsafe."""
        defaults = {
            "technical": ["skills_first", "projects_prominent"],
            "executive": ["summary_prominent", "achievements_focused"],
            "creative": ["portfolio_linked", "visual_friendly"],
            "entry_level": ["education_first", "skills_prominent"],
        }
        return defaults.get(job_type, ["standard"])
