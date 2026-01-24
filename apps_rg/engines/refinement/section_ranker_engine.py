"""
Section Ranker Engine - Dynamic section ordering based on Role Archetype
Refactored from RankResumeSections.py
Following Batch 5 specifications
"""

from __future__ import annotations
from typing import Any, Dict, List
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class SectionRankerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reorders high-level resume sections based on Role Archetype.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.RANKER")
        # Default ranking strategies moved to Knowledge Base config
        self.strategies = {
            "technical": ["contact", "skills", "experience", "projects", "education"],
            "executive": ["contact", "summary", "experience", "education", "skills"],
            "entry": ["contact", "education", "skills", "projects", "experience"],
            "default": ["contact", "summary", "experience", "education", "skills"]
        }
        
        # Try to load from config if available
        if self.config and hasattr(self.config, 'config'):
            config_strategies = self.config.config.qa_thresholds.get("ranking_strategies")
            if config_strategies:
                self.strategies = config_strategies

    async def execute(self, resume_data: Dict[str, Any], role_type: str = "default") -> Dict[str, Any]:
        """
        Reconstruct the resume dictionary with sections in optimal order.
        """
        self._mcp_audit("section_ranking_start", {"role_type": role_type})

        # 1. Determine Strategy
        target_order = self.strategies.get(role_type, self.strategies["default"])
        
        # 2. Identify Missing Sections (Gap Analysis)
        present_keys = set(resume_data.keys())
        missing_required = [k for k in target_order if k not in present_keys]
        
        if missing_required:
            self.record_pass(
                f"Resume missing standard sections for {role_type}", 
                data={"missing": missing_required}
            )
            # We do not fail here; we rank what we have.

        # 3. Construct Ordered Output
        ordered_resume = {}
        
        # First: Append sections in the target order
        for section in target_order:
            if section in resume_data:
                ordered_resume[section] = resume_data[section]
        
        # Second: Append any remaining sections (orphans) at the bottom
        for section in resume_data:
            if section not in ordered_resume:
                ordered_resume[section] = resume_data[section]

        # 4. Telemetry
        rank_change = list(ordered_resume.keys()) != list(resume_data.keys())
        if rank_change:
            self.record_pass(
                "Sections reordered for impact", 
                data={"new_order": list(ordered_resume.keys())}
            )
        else:
            self.record_pass("Existing section order retained")

        return ordered_resume
