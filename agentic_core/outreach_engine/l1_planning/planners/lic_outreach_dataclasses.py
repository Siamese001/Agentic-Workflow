"""
Dataclasses for LIC outreach planning and execution.

Contains core data structures for outreach missions, archetypes, and
recipient profiles used across the L1-L5 layers.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


class ArchetypeType(Enum):
    """The 4 correct outreach archetypes."""
    RECRUITER = "recruiter"
    SENIOR_TA = "senior_ta"
    EXECUTIVE = "executive"
    C_LEVEL = "c_level"


class ReasoningMode(Enum):
    """Reasoning modes for outreach planning."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    COT = "cot"  # Chain of Thought
    TOT = "tot"  # Tree of Thoughts
    REACT = "react"  # ReAct (Reasoning + Acting)

# Constants for temperature and reasoning profiles
SECTION_TEMPERATURE_SCHEDULE = {
    "intro": 0.7,
    "body": 0.8,
    "conclusion": 0.6
}

@dataclass
class ExecutiveReasoningProfile:
    """Profile for executive-level reasoning intensity and cognitive parameters."""
    reasoning_intensity: str
    cot_depth: int
    tot_branches: int
    reflexion_passes: int
    sc_k: int
    require_deep_research: bool
    cognitive_axes: list

def compute_reasoning_multiplier(profile: ExecutiveReasoningProfile) -> int:
    """Compute reasoning multiplier from profile parameters."""
    return profile.cot_depth * profile.tot_branches

@dataclass
class AgentType(Enum):
    """Agent types for planning delegation."""
    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYZER = "analyzer"

@dataclass
class ArchetypeContext:
    """Context for archetype-based planning."""
    archetype: str
    target_role: str
    target_company: str
    value_proposition: str
    executive_reasoning_profile: Optional[ExecutiveReasoningProfile] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RefinementPlan:
    """Plan for refining research results."""
    needs_refinement: bool
    refinement_type: str
    priority: str
    additional_queries: list
    confidence_threshold: float

@dataclass
class ResearchResult:
    """Results from research operations."""
    results: Dict[str, Any]
    confidence: float
    sources: List[str]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class FailureContext:
    """Context for failure analysis and recovery."""
    violation_type: str
    severity: str
    description: str
    recovery_options: List[str] = None

    def __post_init__(self):
        if self.recovery_options is None:
            self.recovery_options = []

@dataclass
class MessageContent:
    """Content structure for message planning."""
    recipient_name: str
    subject: str
    hook: str
    value_proposition: str
    cta: str
    signature: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# Remove duplicate ArchetypeContextFlat definition
# ArchetypeContextFlat is already defined at line 83

# Initialize EXECUTIVE_REASONING_PROFILES after all enum definitions are complete
EXECUTIVE_REASONING_PROFILES = {
    ArchetypeType.C_LEVEL: ExecutiveReasoningProfile(
        reasoning_intensity="extreme",
        cot_depth=12,
        tot_branches=10,
        reflexion_passes=3,
        sc_k=10,
        require_deep_research=True,
        cognitive_axes=["analysis", "synthesis", "evaluation", "creativity", "critical_thinking", "strategic_planning", "decision_making", "problem_solving"]
    ),
    ArchetypeType.EXECUTIVE: ExecutiveReasoningProfile(
        reasoning_intensity="high",
        cot_depth=8,
        tot_branches=6,
        reflexion_passes=2,
        sc_k=6,
        require_deep_research=True,
        cognitive_axes=["analysis", "synthesis", "evaluation", "creativity", "critical_thinking", "strategic_planning", "decision_making", "problem_solving"]
    ),
    ArchetypeType.SENIOR_TA: ExecutiveReasoningProfile(
        reasoning_intensity="medium",
        cot_depth=6,
        tot_branches=4,
        reflexion_passes=1,
        sc_k=4,
        require_deep_research=False,
        cognitive_axes=["analysis", "synthesis", "evaluation", "critical_thinking"]
    ),
    ArchetypeType.RECRUITER: ExecutiveReasoningProfile(
        reasoning_intensity="low",
        cot_depth=4,
        tot_branches=2,
        reflexion_passes=1,
        sc_k=2,
        require_deep_research=False,
        cognitive_axes=["analysis", "evaluation"]
    )
}

def adjust_temperature_by_intensity(base_temp: float, intensity: str) -> float:
    """Adjust temperature based on reasoning intensity."""
    adjustments = {"low": -0.1, "medium": 0.0, "high": 0.2}
    return base_temp + adjustments.get(intensity, 0.0)

def expand_section_by_intensity(base_content: str, intensity: str) -> str:
    """Expand content based on reasoning intensity."""
    multipliers = {"low": 1.0, "medium": 1.2, "high": 1.5}
    multiplier = multipliers.get(intensity, 1.0)
    return base_content * int(multiplier) if multiplier > 1 else base_content


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


@dataclass
class OutreachMission:
    """Core mission configuration for outreach campaigns."""
    mission_id: str = ""
    target_company: str = ""
    target_role: str = ""
    archetype: ArchetypeType = ArchetypeType.RECRUITER
    objective: str = ""
    value_proposition: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)
    personalization_points: List[str] = field(default_factory=list)
    urgency: str = "medium"
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecipientProfile:
    """Profile information for outreach recipients."""
    name: str = ""
    title: str = ""
    company: str = ""
    industry: str = ""
    department: str = ""
    seniority: str = ""
    skills: List[str] = field(default_factory=list)
    recent_activity: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    contact_info: Dict[str, str] = field(default_factory=dict)
    research_data: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ReasoningParams:
    """Reasoning parameters with required attributes."""
    max_reasoning_depth: int = 5
    enable_chain_of_thought: bool = True
    depth: str = "medium"
    creativity: str = "medium"


@dataclass
class RagParams:
    """RAG parameters with required attributes."""
    source_weights: Dict[str, float] = field(default_factory=lambda: {"company": 0.7, "individual": 0.3})
    company_research: str = "technical"
    role_analysis: str = "strategic"


@dataclass
class SignalParams:
    """Signal parameters with required attributes."""
    signal_types: List[str] = field(default_factory=lambda: ["technical", "strategic"])
    expertise: str = "deep_technical"
    value_prop: str = "innovation"


@dataclass
class MessagePlan:
    """Message planning configuration."""
    content: str = ""
    tone: str = "professional"
    length: str = "medium"
    personalization_level: str = "medium"
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchetypeContextFlat:
    """Context for archetype-based planning and execution - flattened interface."""
    archetype: str  # String value, not ArchetypeType enum
    reasoning_mode: str = "balanced"
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)

    # Parameter objects for direct attribute access
    reasoning_params: ReasoningParams = field(default_factory=ReasoningParams)
    rag_params: RagParams = field(default_factory=RagParams)
    signal_params: SignalParams = field(default_factory=SignalParams)

    # Keep other parameters as dicts for now
    tone_params: Dict[str, Any] = field(default_factory=dict)
    cta_params: Dict[str, Any] = field(default_factory=dict)
    constraint_params: Dict[str, Any] = field(default_factory=dict)
    temperature_schedule: Dict[str, float] = field(default_factory=dict)
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

# RECRUITER_REASONING_PROFILES - kept for backward compatibility
RECRUITER_REASONING_PROFILES = {
    "technical": {
        "depth": "medium",
        "creativity": "medium",
        "focus": ["skills", "growth", "team_fit"],
        "tone": "approachable"
    },
    "general": {
        "depth": "low",
        "creativity": "high",
        "focus": ["culture", "opportunity", "benefits"],
        "tone": "friendly"
    }
}

def compute_reasoning_multiplier(profile_name: str, archetype: ArchetypeType) -> float:
    """Compute reasoning multiplier based on profile and archetype."""
    base_multipliers = {
        ArchetypeType.RECRUITER: 1.0,
        ArchetypeType.SENIOR_TA: 1.2,
        ArchetypeType.EXECUTIVE: 1.5,
        ArchetypeType.C_LEVEL: 2.0
    }

    profile_adjustments = {
        "strategic": 1.2,
        "operational": 1.0,
        "technical": 1.1,
        "general": 0.9
    }

    base = base_multipliers.get(archetype, 1.0)
    adjustment = profile_adjustments.get(profile_name, 1.0)
    return base * adjustment

def reasoning_intensity_metadata(reasoning_mode: str, archetype: ArchetypeType) -> Dict[str, Any]:
    """Generate reasoning intensity metadata for given mode and archetype."""
    intensity_levels = {
        "conservative": {"depth": 3, "creativity": 0.2, "iterations": 1},
        "balanced": {"depth": 5, "creativity": 0.5, "iterations": 2},
        "aggressive": {"depth": 8, "creativity": 0.8, "iterations": 3},
        "cot": {"depth": 6, "creativity": 0.6, "iterations": 2},
        "tot": {"depth": 7, "creativity": 0.7, "iterations": 3},
        "react": {"depth": 4, "creativity": 0.4, "iterations": 2}
    }

    base_intensity = intensity_levels.get(reasoning_mode, intensity_levels["balanced"])

    # Adjust based on archetype
    archetype_multipliers = {
        ArchetypeType.RECRUITER: 1.0,
        ArchetypeType.SENIOR_TA: 1.3,
        ArchetypeType.EXECUTIVE: 1.5,
        ArchetypeType.C_LEVEL: 2.0
    }

    multiplier = archetype_multipliers.get(archetype, 1.0)

    return {
        "reasoning_mode": reasoning_mode,
        "archetype": archetype.value,
        "depth": int(base_intensity["depth"] * multiplier),
        "creativity": min(1.0, base_intensity["creativity"] * multiplier),
        "iterations": int(base_intensity["iterations"] * multiplier),
        "multiplier": multiplier,
        "metadata": {
            "base_intensity": base_intensity,
            "computed_at": datetime.now().isoformat()
        }
    }
