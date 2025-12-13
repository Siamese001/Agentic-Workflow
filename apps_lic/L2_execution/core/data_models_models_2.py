"""Dataclass models for data_models."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .data_models_enums import *

@dataclass
class SenderGroundingWhitelists:
    """
    Output of HOP-3 SenderGroundingAgent.
    Used to validate "my team" / "our product" claims in HOP-6.
    """
    team_members: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    case_studies: List[str] = field(default_factory=list)
    quantifiable_achievements: List[str] = field(default_factory=list)
    raw_evidence: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class ResearchContext:
    """
    DEPRECATED v13.0: Logic moved to HOP2_ResearchAgent.
    Output is now state/2_research_context.json
    This class is kept for type hinting in legacy models if needed.
    """
    recipient_insights: List[str]
    company_context: List[str]
    recent_activity: List[str]
    rag_results: List[RAGResult]
    sender_grounding: Optional[SenderGroundingWhitelists] = None
    adversarial_findings: List[str] = field(default_factory=list)

@dataclass
class MessageScaffold:
    """
    DEPRECATED v13.0: Logic moved to HOP4_RoutingAgent.
    Output is now state/4_routing_decision.json
    This class is kept for type hinting in legacy models if needed.
    """
    route: Route
    archetype: Archetype
    sections: Dict[str, Dict[str, object]]
    constraints: Dict[str, object]
    locked_sections: Set[str] = field(default_factory=set)

@dataclass
class GeneratedMessage:
    """
    DEPRECATED v13.0: Logic moved to HOP5_GenerationAgent.
    Output is now state/5_generated_drafts.json
    This class is kept for type hinting in legacy models if needed.
    """
    content: str
    word_count: int
    char_count: int
    route: Route
    archetype: Archetype
    generation_temperature: float
    generation_attempts: int
    checksum: str

@dataclass
class ValidationResult:
    """
    Result from a single validation check in HOP-6.
    """
    passed: bool
    severity: ValidationSeverity
    rule_id: str
    message: str
    details: Optional[Dict[str, object]] = None

