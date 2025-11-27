"""
L1 outreach planning dataclasses for pure computation.

Defines pure data structures for outreach workflow planning without
infrastructure dependencies or execution logic.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal
from enum import Enum


class AgentType(str, Enum):
    """Types of agents responsible for refinement tasks."""
    CONTACT = "contact"
    COMPANY = "company"


class ArchetypeType(str, Enum):
    """The FOUR AND ONLY FOUR correct outreach archetypes."""
    RECRUITER = "recruiter"
    SENIOR_TA = "senior_ta"
    EXECUTIVE = "executive"
    C_LEVEL = "c_level"


class ReasoningMode(str, Enum):
    """Reasoning modes for L1 planning."""
    COT = "cot"      # Chain of Thought
    TOT = "tot"      # Tree of Thought
    REACT = "react"  # ReAct reasoning
    REFLEXION = "reflexion"  # Reflexion reasoning
    SC_K = "sc_k"    # Self-Consistency with K samples


@dataclass
class ToneParameters:
    """Parameters for tone generation in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "ToneParameters"
    formality_level: str = "professional"
    enthusiasm_level: str = "moderate"
    confidence_level: str = "high"
    personalization_level: str = "medium"
    industry_specific: bool = True


@dataclass
class CtaParameters:
    """Parameters for call-to-action generation in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "CtaParameters"
    cta_type: str = "collaboration_discussion"
    urgency_level: str = "medium"
    value_proposition_focus: str = "mutual_benefit"
    friction_reduction: bool = True
    follow_up_enabled: bool = True


@dataclass
class SignalParameters:
    """Parameters for signal processing in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "SignalParameters"
    signal_threshold: float = 0.7
    min_signal_score: float = 0.7
    signal_types: List[str] = field(default_factory=lambda: ["quantitative", "strategic", "recent_activity"])
    weight_distribution: Dict[str, float] = field(default_factory=dict)
    max_age_days: int = 365
    weight_recent: float = 1.2
    weight_quantitative: float = 1.5
    enable_temporal: bool = False


@dataclass
class RagParameters:
    """Parameters for RAG operations in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "RagParameters"
    top_k: int = 10
    similarity_threshold: float = 0.65
    score_threshold: float = 0.7
    include_metadata: bool = True
    source_weights: Dict[str, float] = field(default_factory=dict)
    temporal_filter: Optional[Dict[str, Any]] = None


@dataclass
class ReasoningParameters:
    """Parameters for reasoning operations in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "ReasoningParameters"
    reasoning_mode: str = "analytical"
    reasoning_style: str = "analytical"
    reasoning_mode_enum: ReasoningMode = ReasoningMode.COT
    confidence_threshold: float = 0.8
    max_reasoning_depth: int = 3
    enable_chain_of_thought: bool = True
    use_analogical: bool = True
    use_causal: bool = True


@dataclass
class ConstraintParameters:
    """Parameters for constraint enforcement in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "ConstraintParameters"
    strict_constraints: List[str] = field(default_factory=list)
    soft_constraints: List[str] = field(default_factory=list)
    constraint_weights: Dict[str, float] = field(default_factory=dict)
    allow_violations: bool = False


@dataclass
class ExecutiveReasoningProfile:
    """Executive reasoning profile for extreme reasoning intensity."""
    schema_version: str = "v1"
    model_name: str = "ExecutiveReasoningProfile"
    
    # Required fields for Phase 2 compatibility
    max_reasoning_depth: int = 3
    reasoning_mode: str = "analytical"
    reasoning_style: str = "analytical"
    
    # Explicit backward compatibility fields for test expectations
    cot_depth: int = 2
    tot_branches: int = 2
    tot_recursion_depth: int = 1
    reflexion_passes: int = 0
    sc_k: int = 2
    
    # Reasoning intensity and cognitive axes
    reasoning_intensity: Literal["low", "medium", "high", "extreme"] = "low"
    cognitive_axes: List[str] = field(default_factory=list)
    require_deep_research: bool = False
    
    # Available reasoning modes
    available_reasoning_modes: List[ReasoningMode] = field(default_factory=lambda: [ReasoningMode.COT])


@dataclass
class ArchetypeDefinition:
    """Definition for a specific outreach archetype with parameters."""
    schema_version: str = "v1"
    model_name: str = "ArchetypeDefinition"
    archetype: ArchetypeType = ArchetypeType.RECRUITER
    description: str = ""
    tone_params: ToneParameters = field(default_factory=ToneParameters)
    cta_params: CtaParameters = field(default_factory=CtaParameters)
    signal_params: SignalParameters = field(default_factory=SignalParameters)
    rag_params: RagParameters = field(default_factory=RagParameters)
    reasoning_params: ReasoningParameters = field(default_factory=ReasoningParameters)
    constraint_params: ConstraintParameters = field(default_factory=ConstraintParameters)
    executive_reasoning_profile: ExecutiveReasoningProfile = field(default_factory=ExecutiveReasoningProfile)
    temperature_schedule: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)






@dataclass
class ArchetypeContext:
    """Complete archetype context for outreach planning."""
    schema_version: str = "v1"
    model_name: str = "ArchetypeContext"
    archetype: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    
    # Cross-cutting parameter sets
    rag_params: RagParameters = field(default_factory=RagParameters)
    reasoning_params: ReasoningParameters = field(default_factory=ReasoningParameters)
    signal_params: SignalParameters = field(default_factory=SignalParameters)
    constraint_params: ConstraintParameters = field(default_factory=ConstraintParameters)
    tone_params: ToneParameters = field(default_factory=ToneParameters)
    cta_params: CtaParameters = field(default_factory=CtaParameters)
    
    # Executive reasoning profile for extreme reasoning intensity
    executive_reasoning_profile: ExecutiveReasoningProfile = field(default_factory=ExecutiveReasoningProfile)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutreachMission:
    """Mission definition for outreach workflow planning."""
    schema_version: str = "v1"
    model_name: str = "OutreachMission"
    objective: str = ""
    target_role: str = ""
    target_company: str = ""
    value_proposition: str = ""
    urgency: str = "low"
    personalization_points: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefinementPlan:
    """Plan for research refinement in outreach workflow."""
    schema_version: str = "v1"
    model_name: str = "RefinementPlan"
    needs_refinement: bool = False
    refinement_tasks: List[str] = field(default_factory=list)
    target_agent: Optional[AgentType] = None
    confidence: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiAxisReasoningPlan:
    """Multi-axis research planning for cognitive axes expansion."""
    schema_version: str = "v1"
    model_name: str = "MultiAxisReasoningPlan"
    
    # Multi-axis query expansion
    base_query: str = ""
    cognitive_axes_queries: Dict[str, List[str]] = field(default_factory=dict)
    total_query_count: int = 0
    
    # Reasoning depth multipliers
    cot_depth_multiplier: int = 1
    tot_recursion_multiplier: int = 1
    expanded_subqueries: List[str] = field(default_factory=list)
    
    # Research parameters
    require_deep_research: bool = False
    sc_k: int = 2
    target_sources: List[str] = field(default_factory=list)
    
    # Planning metadata
    cognitive_axes: List[str] = field(default_factory=list)
    reasoning_intensity: str = "low"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReflexionPlan:
    """Reflexion planning for critique and refinement cycles."""
    schema_version: str = "v1"
    model_name: str = "ReflexionPlan"
    
    # Reflexion parameters
    reflexion_passes: int = 0
    critique_questions: List[str] = field(default_factory=list)
    refinement_strategies: List[str] = field(default_factory=list)
    
    # Quality gates
    confidence_threshold: float = 0.7
    completion_criteria: List[str] = field(default_factory=list)
    
    # Planning metadata
    current_pass: int = 0
    max_passes: int = 0
    reasoning_intensity: str = "low"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutreachArchetypePlan:
    """Archetype planning result for outreach workflow."""
    schema_version: str = "v1"
    model_name: str = "OutreachArchetypePlan"
    archetype_context: ArchetypeContext = field(default_factory=ArchetypeContext)
    reasoning_mode: ReasoningMode = ReasoningMode.COT
    confidence: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutreachResearchPlan:
    """Research planning result for outreach workflow."""
    schema_version: str = "v1"
    model_name: str = "OutreachResearchPlan"
    refinement_plan: RefinementPlan = field(default_factory=RefinementPlan)
    research_queries: List[str] = field(default_factory=list)
    target_sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessagePlan:
    """Structured plan for message generation in outreach workflow."""
    schema_version: str = "v1"
    model_name: str = "MessagePlan"
    
    # Section-specific plans
    subject_plan: str = ""
    hook_plan: str = ""
    value_plan: str = ""
    cta_plan: str = ""
    signature_plan: str = ""
    
    # Legacy sections dict for backward compatibility
    sections: Dict[str, str] = field(default_factory=dict)
    temperature_schedule: Dict[str, float] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Planning metadata
    estimated_tokens: int = 0
    generation_strategy: str = "sequential"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutreachMessagePlan:
    """Complete message planning result for outreach workflow."""
    schema_version: str = "v1"
    model_name: str = "OutreachMessagePlan"
    message_plan: MessagePlan = field(default_factory=MessagePlan)
    archetype_context: ArchetypeContext = field(default_factory=ArchetypeContext)
    confidence: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# Temperature schedule constants for message planning
SECTION_TEMPERATURE_SCHEDULE = {
    "subject": 0.65,
    "hook": 0.80,
    "value": 0.55,
    "cta": 0.70,
    "signature": 0.45
}


# Executive reasoning profiles for each archetype
EXECUTIVE_REASONING_PROFILES = {
    ArchetypeType.RECRUITER: ExecutiveReasoningProfile(
        max_reasoning_depth=2,
        reasoning_mode="analytical",
        reasoning_style="direct",
        cot_depth=2,
        tot_branches=2,
        tot_recursion_depth=1,
        reflexion_passes=0,
        sc_k=2,
        reasoning_intensity="low",
        cognitive_axes=["role_fit"],
        require_deep_research=False,
        available_reasoning_modes=[ReasoningMode.COT]
    ),
    
    ArchetypeType.SENIOR_TA: ExecutiveReasoningProfile(
        max_reasoning_depth=4,
        reasoning_mode="technical",
        reasoning_style="detailed",
        cot_depth=4,
        tot_branches=3,
        tot_recursion_depth=2,
        reflexion_passes=1,
        sc_k=3,
        reasoning_intensity="medium",
        cognitive_axes=["technical", "product", "competitive"],
        require_deep_research=False,
        available_reasoning_modes=[ReasoningMode.COT, ReasoningMode.TOT, ReasoningMode.REFLEXION]
    ),
    
    ArchetypeType.EXECUTIVE: ExecutiveReasoningProfile(
        max_reasoning_depth=8,
        reasoning_mode="strategic",
        reasoning_style="executive",
        cot_depth=8,
        tot_branches=6,
        tot_recursion_depth=3,
        reflexion_passes=2,
        sc_k=6,
        reasoning_intensity="high",
        cognitive_axes=["strategic", "financial", "technical", "competitive", "product", "operational", "risk", "psychographic"],
        require_deep_research=True,
        available_reasoning_modes=[ReasoningMode.COT, ReasoningMode.TOT, ReasoningMode.REFLEXION, ReasoningMode.SC_K]
    ),
    
    ArchetypeType.C_LEVEL: ExecutiveReasoningProfile(
        max_reasoning_depth=12,
        reasoning_mode="strategic",
        reasoning_style="board_level",
        cot_depth=12,
        tot_branches=10,
        tot_recursion_depth=4,
        reflexion_passes=3,
        sc_k=10,
        reasoning_intensity="extreme",
        cognitive_axes=["strategic", "financial", "technical", "competitive", "product", "operational", "risk", "psychographic"],
        require_deep_research=True,
        available_reasoning_modes=[ReasoningMode.COT, ReasoningMode.TOT, ReasoningMode.REFLEXION, ReasoningMode.SC_K]
    )
}


# Archetype registry with correct 4 archetypes and realistic parameters
ARCHETYPE_REGISTRY = {
    ArchetypeType.RECRUITER: ArchetypeDefinition(
        archetype=ArchetypeType.RECRUITER,
        description="Screening gateway - focuses on job fit and brevity",
        tone_params=ToneParameters(
            formality_level="professional",
            enthusiasm_level="moderate",
            confidence_level="moderate",
            personalization_level="low",
            industry_specific=True
        ),
        cta_params=CtaParameters(
            cta_type="meeting_request",
            urgency_level="medium",
            value_proposition_focus="job_fit",
            friction_reduction=True,
            follow_up_enabled=True
        ),
        signal_params=SignalParameters(
            min_signal_score=0.6,
            signal_types=["quantitative", "recent_activity"],
            max_age_days=180,
            weight_recent=1.1,
            weight_quantitative=1.3
        ),
        rag_params=RagParameters(
            top_k=8,
            score_threshold=0.65,
            include_metadata=True,
            source_weights={"job_posting": 1.5, "company_career": 1.2}
        ),
        reasoning_params=ReasoningParameters(
            reasoning_style="analytical",
            reasoning_mode=ReasoningMode.COT,
            confidence_threshold=0.7,
            max_reasoning_depth=2,
            use_analogical=False,
            use_causal=True
        ),
        constraint_params=ConstraintParameters(
            strict_constraints=["brevity_required", "no_unverified_claims", "job_fit_focus"],
            soft_constraints=["tone_professional_and_short"],
            constraint_weights={"brevity_required": 2.0, "job_fit_focus": 1.5}
        ),
        executive_reasoning_profile=EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER],
        temperature_schedule=SECTION_TEMPERATURE_SCHEDULE
    ),
    
    ArchetypeType.SENIOR_TA: ArchetypeDefinition(
        archetype=ArchetypeType.SENIOR_TA,
        description="Narrative shaper - focuses on technical depth and company specificity",
        tone_params=ToneParameters(
            formality_level="professional",
            enthusiasm_level="high",
            confidence_level="high",
            personalization_level="medium",
            industry_specific=True
        ),
        cta_params=CtaParameters(
            cta_type="technical_discussion",
            urgency_level="low",
            value_proposition_focus="technical_excellence",
            friction_reduction=True,
            follow_up_enabled=True
        ),
        signal_params=SignalParameters(
            min_signal_score=0.7,
            signal_types=["quantitative", "strategic"],
            max_age_days=365,
            weight_recent=1.0,
            weight_quantitative=1.8
        ),
        rag_params=RagParameters(
            top_k=12,
            score_threshold=0.7,
            include_metadata=True,
            source_weights={"technical_blog": 1.8, "github": 1.5, "stackoverflow": 1.3}
        ),
        reasoning_params=ReasoningParameters(
            reasoning_style="analytical",
            reasoning_mode=ReasoningMode.TOT,
            confidence_threshold=0.8,
            max_reasoning_depth=3,
            use_analogical=True,
            use_causal=True
        ),
        constraint_params=ConstraintParameters(
            strict_constraints=["role_alignment_required", "avoid_strategic_language"],
            soft_constraints=["must_include_company_specificity"],
            constraint_weights={"role_alignment_required": 2.0, "technical_depth": 1.5}
        ),
        executive_reasoning_profile=EXECUTIVE_REASONING_PROFILES[ArchetypeType.SENIOR_TA],
        temperature_schedule=SECTION_TEMPERATURE_SCHEDULE
    ),
    
    ArchetypeType.EXECUTIVE: ArchetypeDefinition(
        archetype=ArchetypeType.EXECUTIVE,
        description="Business stakeholder - focuses on strategic impact and business outcomes",
        tone_params=ToneParameters(
            formality_level="executive",
            enthusiasm_level="high",
            confidence_level="very_high",
            personalization_level="high",
            industry_specific=True
        ),
        cta_params=CtaParameters(
            cta_type="strategic_discussion",
            urgency_level="medium",
            value_proposition_focus="business_outcome",
            friction_reduction=True,
            follow_up_enabled=True
        ),
        signal_params=SignalParameters(
            min_signal_score=0.75,
            signal_types=["strategic", "quantitative"],
            max_age_days=180,
            weight_recent=1.3,
            weight_quantitative=1.8
        ),
        rag_params=RagParameters(
            top_k=15,
            score_threshold=0.75,
            include_metadata=True,
            source_weights={"executive_insights": 1.8, "market_analysis": 1.6, "business_news": 1.4}
        ),
        reasoning_params=ReasoningParameters(
            reasoning_style="strategic",
            reasoning_mode=ReasoningMode.TOT,
            confidence_threshold=0.8,
            max_reasoning_depth=5,
            use_analogical=True,
            use_causal=True
        ),
        constraint_params=ConstraintParameters(
            strict_constraints=["strategic_alignment_required", "business_impact_required", "no_filler_language"],
            soft_constraints=["executive_summary_required"],
            constraint_weights={"strategic_alignment_required": 2.0, "business_impact": 1.8}
        ),
        executive_reasoning_profile=EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE],
        temperature_schedule=SECTION_TEMPERATURE_SCHEDULE
    ),
    
    ArchetypeType.C_LEVEL: ArchetypeDefinition(
        archetype=ArchetypeType.C_LEVEL,
        description="Strategic peer - focuses on business outcomes and high signal density",
        tone_params=ToneParameters(
            formality_level="executive",
            enthusiasm_level="high",
            confidence_level="very_high",
            personalization_level="high",
            industry_specific=True
        ),
        cta_params=CtaParameters(
            cta_type="strategic_partnership",
            urgency_level="low",
            value_proposition_focus="business_outcome",
            friction_reduction=True,
            follow_up_enabled=False
        ),
        signal_params=SignalParameters(
            min_signal_score=0.8,
            signal_types=["strategic", "quantitative"],
            max_age_days=90,
            weight_recent=1.5,
            weight_quantitative=2.0
        ),
        rag_params=RagParameters(
            top_k=15,
            score_threshold=0.75,
            include_metadata=True,
            source_weights={"earnings_calls": 2.0, "executive_insights": 1.8, "market_analysis": 1.6}
        ),
        reasoning_params=ReasoningParameters(
            reasoning_style="strategic",
            reasoning_mode=ReasoningMode.TOT,
            confidence_threshold=0.85,
            max_reasoning_depth=6,
            use_analogical=True,
            use_causal=True
        ),
        constraint_params=ConstraintParameters(
            strict_constraints=["strategic_alignment_required", "quantifiable_outcomes_required", "no_filler_language"],
            soft_constraints=["high_signal_density_required"],
            constraint_weights={"strategic_alignment_required": 2.5, "quantifiable_outcomes": 2.0}
        ),
        executive_reasoning_profile=EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL],
        temperature_schedule=SECTION_TEMPERATURE_SCHEDULE
    )
}


# ============================================================================
# UNIFIED REASONING-INTENSITY HELPER FUNCTIONS
# ============================================================================

def compute_reasoning_multiplier(profile: ExecutiveReasoningProfile) -> int:
    """
    Compute unified reasoning multiplier from executive profile.
    
    Uses cot_depth * tot_branches for consistency across all planners.
    This multiplier determines query expansion, section depth, and richness.
    """
    return profile.cot_depth * profile.tot_branches


def adjust_temperature_by_intensity(
    base_temp: float, 
    profile: ExecutiveReasoningProfile, 
    section_name: str
) -> float:
    """
    Adjust temperature based on reasoning intensity and section type.
    
    Higher intensity increases creativity in engaging sections (hook, value)
    while maintaining formality in structured sections (subject, signature).
    """
    intensity = profile.reasoning_intensity
    adjusted_temp = base_temp
    
    # Intensity-based adjustments
    if intensity == "extreme":
        if section_name in ["hook", "value"]:
            adjusted_temp += 0.15
        elif section_name in ["subject", "signature"]:
            adjusted_temp -= 0.05
        else:  # cta
            adjusted_temp += 0.05
    elif intensity == "high":
        if section_name in ["hook", "value"]:
            adjusted_temp += 0.10
        elif section_name in ["subject", "signature"]:
            adjusted_temp -= 0.05
        else:  # cta
            adjusted_temp += 0.05
    elif intensity == "medium":
        if section_name in ["hook", "value"]:
            adjusted_temp += 0.05
    
    # Clamp between 0.1 and 1.5
    return max(0.1, min(1.5, adjusted_temp))


def expand_section_by_intensity(
    base_content: str, 
    profile: ExecutiveReasoningProfile, 
    section_name: str
) -> str:
    """
    Expand section content based on reasoning intensity multiplier.
    
    Higher intensity archetypes (EXECUTIVE, C_LEVEL) get richer, more detailed
    content with expanded arguments and increased sentence density.
    """
    multiplier = compute_reasoning_multiplier(profile)
    intensity = profile.reasoning_intensity
    
    if intensity in ["low", "medium"]:
        return base_content
    
    # Expand content for high/extreme intensity archetypes
    expansions = []
    
    if section_name == "hook" and intensity in ["high", "extreme"]:
        expansions.extend([
            f"Given {profile.cognitive_axes[0] if profile.cognitive_axes else 'strategic'} priorities,",
            "With deep consideration of your organizational context,"
        ])
    
    elif section_name == "value" and intensity == "extreme":
        expansions.extend([
            f"Across {len(profile.cognitive_axes)} key dimensions including:",
            "Strategic business impact with quantifiable outcomes,",
            "Technical innovation aligned with market needs,",
            "Operational excellence and scalability considerations,"
        ])
    elif section_name == "value" and intensity == "high":
        expansions.extend([
            "Key business value propositions:",
            "Strategic alignment with your objectives,"
        ])
    
    elif section_name == "cta" and intensity == "extreme":
        expansions.extend([
            "For comprehensive discussion of strategic implications,",
            "To explore detailed integration pathways,"
        ])
    elif section_name == "cta" and intensity == "high":
        expansions.extend([
            "For detailed business value discussion,",
            "To explore specific collaboration opportunities,"
        ])
    
    elif section_name == "subject" and intensity == "extreme":
        expansions.extend([
            "Strategic Partnership Discussion",
            "High-Value Executive Collaboration",
        ])
    elif section_name == "subject" and intensity == "high":
        expansions.extend([
            "Strategic Business Opportunity",
            "Executive Leadership Discussion",
        ])
    
    elif section_name == "signature" and intensity == "extreme":
        expansions.extend([
            "Strategic Partnership Partner",
            "Executive Collaboration Specialist",
        ])
    elif section_name == "signature" and intensity == "high":
        expansions.extend([
            "Strategic Business Partner",
            "Executive Collaboration Advisor",
        ])
    
    # Combine base content with expansions
    if expansions:
        return f"{base_content} {' '.join(expansions)}"
    
    return base_content


def reasoning_intensity_metadata(profile: ExecutiveReasoningProfile) -> Dict[str, Any]:
    """
    Generate complete reasoning-intensity metadata for L1->L2 propagation.
    
    Returns all fields needed by L2 executors to respect reasoning intensity.
    """
    return {
        "reasoning_intensity": profile.reasoning_intensity,
        "cot_depth": profile.cot_depth,
        "tot_branches": profile.tot_branches,
        "reasoning_multiplier": compute_reasoning_multiplier(profile),
        "reflexion_passes": profile.reflexion_passes,
        "sc_k": profile.sc_k,
        "cognitive_axes": profile.cognitive_axes,
        "require_deep_research": profile.require_deep_research,
        "executive_profile": profile  # Full dataclass for advanced L2 processing
    }
