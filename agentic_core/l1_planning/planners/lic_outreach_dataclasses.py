"""
Dataclasses for LIC outreach planning and execution.

Contains core data structures for outreach missions, archetypes, and
recipient profiles used across the L1-L5 layers.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any


class ArchetypeType(Enum):
    """The 4 correct outreach archetypes."""
    RECRUITER = "recruiter"
    SENIOR_TA = "senior_ta"
    EXECUTIVE = "executive"
    C_LEVEL = "c_level"


@dataclass
class ArchetypeDefinition:
    """Complete archetype definition with all required parameters."""
    tone_params: Dict[str, Any] = field(default_factory=dict)
    cta_params: Dict[str, Any] = field(default_factory=dict)
    signal_params: Dict[str, Any] = field(default_factory=dict)
    rag_params: Dict[str, Any] = field(default_factory=dict)
    reasoning_params: Dict[str, Any] = field(default_factory=dict)
    constraint_params: Dict[str, Any] = field(default_factory=dict)
    temperature_schedule: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_style: str = "professional"
    focus_areas: List[str] = field(default_factory=list)
    tone: str = "balanced"
    priority_weight: float = 1.0


# ARCHETYPE_REGISTRY with complete definitions for all 4 archetypes
ARCHETYPE_REGISTRY = {
    ArchetypeType.RECRUITER: ArchetypeDefinition(
        tone_params={"formality": "medium", "enthusiasm": "high"},
        cta_params={"directness": "medium", "urgency": "medium"},
        signal_params={"expertise": "technical", "value_prop": "growth"},
        rag_params={"company_research": "detailed", "role_analysis": "comprehensive"},
        reasoning_params={"depth": "medium", "creativity": "medium"},
        constraint_params={"length": "medium", "personalization": "high"},
        temperature_schedule={"initial": 0.7, "refinement": 0.5},
        metadata={"target_persona": "recruiter", "industry": "tech"},
        message_style="professional",
        focus_areas=["technical_skills", "growth_opportunity", "team_fit"],
        tone="approachable",
        priority_weight=1.0
    ),
    ArchetypeType.SENIOR_TA: ArchetypeDefinition(
        tone_params={"formality": "high", "enthusiasm": "medium"},
        cta_params={"directness": "low", "urgency": "low"},
        signal_params={"expertise": "deep_technical", "value_prop": "innovation"},
        rag_params={"company_research": "technical", "role_analysis": "strategic"},
        reasoning_params={"depth": "high", "creativity": "medium"},
        constraint_params={"length": "detailed", "personalization": "medium"},
        temperature_schedule={"initial": 0.6, "refinement": 0.4},
        metadata={"target_persona": "senior_technical_authority", "industry": "tech"},
        message_style="formal",
        focus_areas=["technical_leadership", "innovation", "strategic_impact"],
        tone="respectful",
        priority_weight=0.9
    ),
    ArchetypeType.EXECUTIVE: ArchetypeDefinition(
        tone_params={"formality": "high", "enthusiasm": "low"},
        cta_params={"directness": "low", "urgency": "low"},
        signal_params={"expertise": "business", "value_prop": "roi"},
        rag_params={"company_research": "strategic", "role_analysis": "business_impact"},
        reasoning_params={"depth": "medium", "creativity": "low"},
        constraint_params={"length": "concise", "personalization": "low"},
        temperature_schedule={"initial": 0.5, "refinement": 0.3},
        metadata={"target_persona": "executive", "industry": "business"},
        message_style="executive",
        focus_areas=["business_impact", "strategic_value", "leadership"],
        tone="formal",
        priority_weight=0.8
    ),
    ArchetypeType.C_LEVEL: ArchetypeDefinition(
        tone_params={"formality": "highest", "enthusiasm": "lowest"},
        cta_params={"directness": "lowest", "urgency": "lowest"},
        signal_params={"expertise": "c_suite", "value_prop": "transformation"},
        rag_params={"company_research": "comprehensive", "role_analysis": "transformational"},
        reasoning_params={"depth": "highest", "creativity": "lowest"},
        constraint_params={"length": "minimal", "personalization": "minimal"},
        temperature_schedule={"initial": 0.4, "refinement": 0.2},
        metadata={"target_persona": "c_level_executive", "industry": "enterprise"},
        message_style="c_suite",
        focus_areas=["transformation", "market_leadership", "visionary_impact"],
        tone="deferential",
        priority_weight=0.7
    )
}
