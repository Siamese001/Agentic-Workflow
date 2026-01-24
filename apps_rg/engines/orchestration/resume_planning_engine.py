"""
Resume Planning Engine - L1 Planner
Refactored from resume_planner.py
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ResumePlanningEngine(BaseRGEngine):
    """
    L1 Planning - Role/Industry focus determination.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.PLANNING")

    async def execute(
        self, job_description: str, candidate_profile: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create initial resume generation plan.
        """
        self._mcp_audit("planning_start")

        plan = {
            "target_role": self._extract_role(job_description),
            "target_industry": self._extract_industry(job_description),
            "emphasis_areas": [],
            "k_nodes_required": ["K.1", "K.2", "K.3", "K.4", "K.5", "K.6", "K.7", "K.8", "K.9"],
        }

        # Determine emphasis based on JD keywords
        if "leadership" in job_description.lower():
            plan["emphasis_areas"].append("K.9")

        if "technical" in job_description.lower() or "engineer" in job_description.lower():
            plan["emphasis_areas"].extend(["K.6", "K.7"])

        self.record_pass("Resume plan created", data=plan)
        return plan

    def _extract_role(self, jd: str) -> str:
        """Extract primary role from JD."""
        # Simplified extraction
        role_keywords = ["engineer", "manager", "director", "analyst", "developer"]
        for keyword in role_keywords:
            if keyword in jd.lower():
                return keyword.title()
        return "Professional"

    def _extract_industry(self, jd: str) -> str:
        """Extract industry from JD."""
        industry_keywords = {
            "technology": ["software", "tech", "cloud", "data"],
            "finance": ["financial", "banking", "investment"],
            "healthcare": ["medical", "health", "clinical"],
        }

        jd_lower = jd.lower()
        for industry, keywords in industry_keywords.items():
            if any(kw in jd_lower for kw in keywords):
                return industry.title()

        return "Technology"
