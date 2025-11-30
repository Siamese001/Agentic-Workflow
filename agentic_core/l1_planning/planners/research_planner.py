"""
Research Planner Module
LEVEL 5 - Research planning and information gathering strategy for agentic operations
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ResearchPlan:
    """Represents a research plan with sources and methodology"""
    plan_id: str
    research_objective: str
    data_sources: List[str]
    methodology: Dict[str, Any]
    quality_criteria: List[str]

class ResearchPlanner:
    """Handles research planning and information gathering strategy"""

    def __init__(self):
        self.research_sources = [
            "professional_networks",
            "company_databases",
            "industry_reports",
            "public_records",
            "web_sources"
        ]

    async def create_research_plan(
        self,
        research_target: str,
        constraints: List[str],
        context: Dict[str, Any]
    ) -> ResearchPlan:
        """Create a research plan with sources and methodology"""
        try:
            plan_id = f"research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Select appropriate data sources
            data_sources = self._select_data_sources(research_target, constraints)

            # Define research methodology
            methodology = self._define_methodology(research_target, data_sources)

            # Set quality criteria
            quality_criteria = self._set_quality_criteria(research_target)

            return ResearchPlan(
                plan_id=plan_id,
                research_objective=research_target,
                data_sources=data_sources,
                methodology=methodology,
                quality_criteria=quality_criteria
            )

        except Exception as e:
            raise Exception(f"Research planning failed: {str(e)}")

    def _select_data_sources(
        self, research_target: str, constraints: List[str]
    ) -> List[str]:
        """Select appropriate data sources based on target and constraints"""
        target_lower = research_target.lower()

        sources = []
        if "company" in target_lower or "organization" in target_lower:
            sources.extend(["company_databases", "professional_networks"])
        if "person" in target_lower or "contact" in target_lower:
            sources.extend(["professional_networks", "public_records"])
        if "industry" in target_lower or "market" in target_lower:
            sources.extend(["industry_reports", "web_sources"])

        # Add web sources as fallback
        if not sources or "web" in constraints:
            sources.append("web_sources")

        return list(set(sources))  # Remove duplicates

    def _define_methodology(
        self, research_target: str, data_sources: List[str]
    ) -> Dict[str, Any]:
        """Define research methodology based on target and sources"""
        return {
            "approach": "multi_source_validation",
            "data_collection": {
                "primary_sources": data_sources[:2],
                "secondary_sources": data_sources[2:],
                "validation_required": True
            },
            "processing_steps": [
                "data_extraction",
                "quality_assessment",
                "cross_reference_validation",
                "synthesis"
            ],
            "estimated_duration": len(data_sources) * 2  # hours
        }

    def _set_quality_criteria(self, research_target: str) -> List[str]:
        """Set quality criteria for research results"""
        base_criteria = [
            "data_freshness",
            "source_reliability",
            "information_completeness"
        ]

        target_lower = research_target.lower()
        if "company" in target_lower:
            base_criteria.extend(["financial_accuracy", "legal_compliance"])
        if "person" in target_lower:
            base_criteria.extend(["contact_verification", "professional_authenticity"])

        return base_criteria

__all__ = ["ResearchPlanner", "ResearchPlan"]
