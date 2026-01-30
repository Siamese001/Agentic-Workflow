"""
RgStrategicPlannerAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
from apps_rg.shared.core.agent_base import RGAgentBase


@dataclass
class RgStrategicPlannerAgent(SubatomicTestingMixin, RGAgentBase):
    """
    Plans execution strategy based on signals and state.

    Analyzes:
    - Current signals
    - Failed agents
    - Modified sections
    - Blast radius
    """

    def __post_init__(self) -> None:
        """Initialize strategic planner agent."""
        super().__post_init__()

    async def execute(self) -> None:
        self.log("Formulating strategic plan...")

        # Analyze current state
        signals = list(self.ctx.signals)
        list(self.ctx.get_failed_results().keys())
        list(self.ctx.modified_sections)
        impact = list(self.ctx.impact_zone)

        plan = {
            "priority_signals": [],
            "recommended_agents": [],
            "sections_to_review": [],
            "strategy": "standard",
        }

        # Prioritize signals
        if "QUALITY_FAILURE" in signals:
            plan["priority_signals"].append("QUALITY_FAILURE")
            plan["recommended_agents"].extend(["ContentQualityAgent", "FactCheckAgent"])
            plan["strategy"] = "quality_focus"

        if "HALLUCINATION_DETECTED" in signals:
            plan["priority_signals"].append("HALLUCINATION_DETECTED")
            plan["recommended_agents"].append("FactCheckAgent")
            plan["strategy"] = "fact_check_focus"

        if "ATS_FAILURE" in signals:
            plan["priority_signals"].append("ATS_FAILURE")
            plan["recommended_agents"].append("ATSCompatibilityAgent")

        if "BRAND_VIOLATION" in signals:
            plan["priority_signals"].append("BRAND_VIOLATION")
            plan["recommended_agents"].append("BrandComplianceAgent")

        # Add sections to review based on blast radius
        if impact:
            plan["sections_to_review"] = impact
            self.log(f"☢️ Blast radius: {len(impact)} sections may need review")

        # Store plan
        self.ctx.results["strategic_plan"] = plan

        self.record_pass(f"Strategy: {plan['strategy']}", data=plan)

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by RgStrategicPlannerAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"RgStrategicPlannerAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"RgStrategicPlannerAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
