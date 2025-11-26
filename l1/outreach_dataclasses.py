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


@dataclass
class SignalParameters:
    """Parameters for signal processing in outreach planning."""
    min_signal_score: float = 0.7
    signal_types: List[str] = field(default_factory=lambda: ["quantitative", "strategic", "recent_activity"])
    max_age_days: int = 365
    weight_recent: float = 1.2
    weight_quantitative: float = 1.5


@dataclass
class RagParameters:
    """Parameters for RAG processing in outreach planning."""
    top_k: int = 10
    score_threshold: float = 0.7
    include_metadata: bool = True
    source_weights: Dict[str, float] = field(default_factory=dict)
    temporal_filter: Optional[Dict[str, Any]] = None


@dataclass
class ReasoningParameters:
    """Parameters for reasoning strategies in outreach planning."""
    reasoning_style: str = "analytical"
    confidence_threshold: float = 0.8
    max_reasoning_depth: int = 3
    use_analogical: bool = True
    use_causal: bool = True


@dataclass
class ConstraintParameters:
    """Parameters for constraint handling in outreach planning."""
    strict_constraints: List[str] = field(default_factory=list)
    soft_constraints: List[str] = field(default_factory=list)
    constraint_weights: Dict[str, float] = field(default_factory=dict)
    allow_violations: bool = False


@dataclass
class ToneParameters:
    """Parameters for tone generation in outreach planning."""
    formality_level: str = "professional"
    enthusiasm_level: str = "moderate"
    confidence_level: str = "high"
    personalization_level: str = "medium"
    industry_specific: bool = True


@dataclass
class CtaParameters:
    """Parameters for call-to-action generation in outreach planning."""
    cta_type: str = "meeting_request"
    urgency_level: str = "low"
    value_proposition_focus: str = "mutual_benefit"
    friction_reduction: bool = True
    follow_up_enabled: bool = True


@dataclass
class ArchetypeContext:
    """Complete archetype context for outreach planning."""
    archetype: str
    confidence: float
    reasoning: str
    
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
class RefinementPlan:
    """Plan for research refinement in outreach workflow."""
    needs_refinement: bool
    refinement_tasks: List[str]
    target_agent: Optional[AgentType]
    confidence: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessagePlan:
    """Structured plan for message generation in outreach workflow."""
    sections: Dict[str, str]
    temperature_schedule: Dict[str, float]
    constraints: Dict[str, Any]
    
    # Planning metadata
    estimated_tokens: int = 0
    generation_strategy: str = "sequential"
    metadata: Dict[str, Any] = field(default_factory=dict)


# Temperature schedule constants for message planning
SECTION_TEMPERATURE_SCHEDULE = {
    "subject": 0.7,
    "hook": 0.9,
    "body": 0.8,
    "cta": 0.6,
    "signature": 0.3
}
