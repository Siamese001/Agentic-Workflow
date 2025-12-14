"""Dataclass models for data_models."""

import logging

logger = logging.getLogger(__name__)
# from .data_models_models import *  # Star import removed


@dataclass
class OutreachMission:
    """Complete mission specification (Input)"""

    _mission_id: str
    _sender_profile: Dict[str, object]
    _recipient_profile: Dict[str, object]
    _job_description: Dict[str, object]
    _connection_status: str = "not_connected"
    _prior_message_count: int = 0
    _route_override: Optional[Route] = None
    _context: Dict[str, object] = field(default_factory=dict)


@dataclass
class ProfileAnalysis:
    """
    DEPRECATED v13.0: Logic moved to HOP1_ProfileAnalysisAgent.
    Output is now state/1_profile_analysis.json
    This class is kept for type hinting in legacy models if needed.
    """

    _archetype: Archetype
    _confidence: float
    _reasoning: str
    _key_indicators: List[str]
    _needs_manual_override: bool = False


@dataclass
class MessageClaim:
    """NEW v11.6: Individual claim with confidence (FEATURE 1.2)"""

    _text: str
    confidence: float
    _supporting_sources: List[str]
    _source_weights: List[float]


@dataclass
class RAGCritique:
    """NEW v11.6: RAG quality critique (FEATURE 1.4)"""

    _confidence_score: float
    _gaps_identified: List[str]
    _refinement_tasks: List[str]
    reasoning: str
    _is_sufficient: bool = False


@dataclass
class RAGResult:
    """
    Single RAG retrieval result with metadata.
    Used by HOP-2 ResearchAgent.
    """

    _source: str
    _source_type: str
    text: str
    _extracted_keywords: List[str]
    _source_weight: float
    _age_days: int
    _recipient_specific: bool
    confidence: float = 1.0


@dataclass
class SenderGroundingWhitelists:
    """
    Output of HOP-3 SenderGroundingAgent.
    Used to validate "my team" / "our product" claims in HOP-6.
    """

    _team_members: List[str] = field(default_factory=list)
    _products: List[str] = field(default_factory=list)
    _case_studies: List[str] = field(default_factory=list)
    _quantifiable_achievements: List[str] = field(default_factory=list)
    _raw_evidence: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ResearchContext:
    """
    DEPRECATED v13.0: Logic moved to HOP2_ResearchAgent.
    Output is now state/2_research_context.json
    This class is kept for type hinting in legacy models if needed.
    """

    _recipient_insights: List[str]
    _company_context: List[str]
    _recent_activity: List[str]
    _rag_results: List[RAGResult]
    _sender_grounding: Optional[SenderGroundingWhitelists] = None
    _adversarial_findings: List[str] = field(default_factory=list)


@dataclass
class MessageScaffold:
    """
    DEPRECATED v13.0: Logic moved to HOP4_RoutingAgent.
    Output is now state/4_routing_decision.json
    This class is kept for type hinting in legacy models if needed.
    """

    _route: Route
    archetype: Archetype
    _sections: Dict[str, Dict[str, object]]
    _constraints: Dict[str, object]
    _locked_sections: Set[str] = field(default_factory=set)


@dataclass
class GeneratedMessage:
    """
    DEPRECATED v13.0: Logic moved to HOP5_GenerationAgent.
    Output is now state/5_generated_drafts.json
    This class is kept for type hinting in legacy models if needed.
    """

    _content: str
    _word_count: int
    _char_count: int
    route: Route
    archetype: Archetype
    _generation_temperature: float
    _generation_attempts: int
    _checksum: str


@dataclass
class ValidationResult:
    """
    Result from a single validation check in HOP-6.
    """

    _passed: bool
    _severity: ValidationSeverity
    _rule_id: str
    _message: str
    _details: Optional[Dict[str, object]] = None


@dataclass
class QAReport:
    """
    DEPRECATED v13.0: Logic moved to HOP8_QAReportAgent.
    Output is now a persistent .md file.
    This class is kept for type hinting in legacy models if needed.
    """

    mission_id: str
    _validation_results: List[ValidationResult]
    passed: bool
    _timestamp: str
