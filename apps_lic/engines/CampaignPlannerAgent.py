"""
CampaignPlannerAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


@dataclass
class CampaignPlannerAgent(HealerMixin, SubatomicTestingMixin, OutreachAgent, MCPHardenedMixin):
    """
    Strategic campaign planning agent.

    Provides:
    - Campaign structure recommendations
    - Lead segmentation suggestions
    - Follow-up sequence planning
    - LLM-powered strategic insights
    """

    async def execute(self) -> None:
        """
        Execute campaign planning and generate strategic recommendations.

        Analyzes:
        - Campaign schedule and follow-up sequences
        - Lead segmentation needs
        - Tracking requirements
        - Uses LLM for advanced planning insights
        """
        print(f"   [{self.name}] Planning campaign strategy...")

        campaign = self.ctx.current_campaign
        leads = self.ctx.leads

        # Analyze campaign needs
        recommendations = []

        if not campaign.get("schedule"):
            recommendations.append("Add send schedule")

        if not campaign.get("follow_up_sequence"):
            recommendations.append("Add follow-up sequence")

        if len(leads) > 100 and not campaign.get("segmentation"):
            recommendations.append("Add lead segmentation")

        if not campaign.get("tracking"):
            recommendations.append("Enable tracking")

        # Use LLM for advanced planning if available
        if self.ctx.intelligence_enabled and leads:
            prompt = f"""
Analyze this outreach campaign and provide strategic recommendations:

Campaign: {campaign.get("name", "Unnamed")}
Goal: {campaign.get("goal", "Not specified")}
Target Company: {self.ctx.target_company}
Lead Count: {len(leads)}

Provide 3 specific recommendations to improve campaign effectiveness.
"""
            llm_response = await self.call_llm(prompt)
            if llm_response:
                recommendations.append(f"LLM Insight: {llm_response[:200]}")

        if recommendations:
            self.ctx.current_campaign["recommendations"] = recommendations

        self.record_result(True, f"Generated {len(recommendations)} recommendations")
        print(f"   [{self.name}] ✅ Strategy planned ({len(recommendations)} recommendations)")

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, int]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters

        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository(dry_run, execute, **kwargs)
