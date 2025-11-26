"""
L1 outreach planning dataclasses for pure computation.

Defines pure data structures for outreach workflow planning without
infrastructure dependencies or execution logic.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class AgentType(str, Enum):
    """Types of agents responsible for refinement tasks."""
    CONTACT = "contact"
    COMPANY = "company"


class ArchetypeType(str, Enum):
    """The FOUR AND ONLY FOUR correct outreach archetypes."""
    RECRUITER = "recruiter"
    SENIOR_TA = "senior_ta"
    HIRING_MANAGER = "hiring_manager"
    C_LEVEL = "c_level"


class ReasoningMode(str, Enum):
    """Reasoning modes for L1 planning."""
    COT = "cot"      # Chain of Thought
    TOT = "tot"      # Tree of Thought
    REACT = "react"  # ReAct reasoning


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
    "subject": 0.7,
    "hook": 0.9,
    "body": 0.8,
    "cta": 0.6,
    "signature": 0.3
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
        temperature_schedule={"subject": 0.6, "hook": 0.8, "body": 0.7, "cta": 0.5, "signature": 0.3}
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
        temperature_schedule={"subject": 0.7, "hook": 0.9, "body": 0.8, "cta": 0.6, "signature": 0.3}
    ),
    
    ArchetypeType.HIRING_MANAGER: ArchetypeDefinition(
        archetype=ArchetypeType.HIRING_MANAGER,
        description="Team pain point owner - focuses on business impact and team dynamics",
        tone_params=ToneParameters(
            formality_level="professional",
            enthusiasm_level="moderate",
            confidence_level="high",
            personalization_level="high",
            industry_specific=True
        ),
        cta_params=CtaParameters(
            cta_type="team_impact_discussion",
            urgency_level="medium",
            value_proposition_focus="team_benefit",
            friction_reduction=True,
            follow_up_enabled=True
        ),
        signal_params=SignalParameters(
            min_signal_score=0.75,
            signal_types=["strategic", "quantitative"],
            max_age_days=270,
            weight_recent=1.2,
            weight_quantitative=1.6
        ),
        rag_params=RagParameters(
            top_k=10,
            score_threshold=0.72,
            include_metadata=True,
            source_weights={"company_news": 1.4, "team_blog": 1.6, "management_insights": 1.3}
        ),
        reasoning_params=ReasoningParameters(
            reasoning_style="practical",
            reasoning_mode=ReasoningMode.REACT,
            confidence_threshold=0.75,
            max_reasoning_depth=3,
            use_analogical=True,
            use_causal=True
        ),
        constraint_params=ConstraintParameters(
            strict_constraints=["pain_point_relevance_required", "team_impact_required", "no_buzzwords"],
            soft_constraints=["specific_metrics_required"],
            constraint_weights={"pain_point_relevance_required": 2.0, "team_impact": 1.8}
        ),
        temperature_schedule={"subject": 0.7, "hook": 0.8, "body": 0.8, "cta": 0.6, "signature": 0.3}
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
            max_reasoning_depth=4,
            use_analogical=True,
            use_causal=True
        ),
        constraint_params=ConstraintParameters(
            strict_constraints=["strategic_alignment_required", "quantifiable_outcomes_required", "no_filler_language"],
            soft_constraints=["high_signal_density_required"],
            constraint_weights={"strategic_alignment_required": 2.5, "quantifiable_outcomes": 2.0}
        ),
        temperature_schedule={"subject": 0.8, "hook": 0.9, "body": 0.9, "cta": 0.7, "signature": 0.4}
    )
}
