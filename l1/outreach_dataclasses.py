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


class ReasoningMode(str, Enum):
    """Reasoning modes for L1 planning."""
    COT = "cot"      # Chain of Thought
    TOT = "tot"      # Tree of Thought
    REACT = "react"  # ReAct reasoning


@dataclass
class SignalParameters:
    """Parameters for signal processing in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "SignalParameters"
    min_signal_score: float = 0.7
    signal_types: List[str] = field(default_factory=lambda: ["quantitative", "strategic", "recent_activity"])
    max_age_days: int = 365
    weight_recent: float = 1.2
    weight_quantitative: float = 1.5


@dataclass
class RagParameters:
    """Parameters for RAG processing in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "RagParameters"
    top_k: int = 10
    score_threshold: float = 0.7
    include_metadata: bool = True
    source_weights: Dict[str, float] = field(default_factory=dict)
    temporal_filter: Optional[Dict[str, Any]] = None


@dataclass
class ReasoningParameters:
    """Parameters for reasoning strategies in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "ReasoningParameters"
    reasoning_style: str = "analytical"
    reasoning_mode: ReasoningMode = ReasoningMode.COT
    confidence_threshold: float = 0.8
    max_reasoning_depth: int = 3
    use_analogical: bool = True
    use_causal: bool = True


@dataclass
class ConstraintParameters:
    """Parameters for constraint handling in outreach planning."""
    schema_version: str = "v1"
    model_name: str = "ConstraintParameters"
    strict_constraints: List[str] = field(default_factory=list)
    soft_constraints: List[str] = field(default_factory=list)
    constraint_weights: Dict[str, float] = field(default_factory=dict)
    allow_violations: bool = False


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
    cta_type: str = "meeting_request"
    urgency_level: str = "low"
    value_proposition_focus: str = "mutual_benefit"
    friction_reduction: bool = True
    follow_up_enabled: bool = True


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
