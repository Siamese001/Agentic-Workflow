"""Dataclass models for data_models."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .data_models_models import *

@dataclass
class OutreachMission:
    """Complete mission specification (Input)"""
    mission_id: str
    sender_profile: Dict[str, object]
    recipient_profile: Dict[str, object]
    job_description: Dict[str, object]
    connection_status: str = 'not_connected'
    prior_message_count: int = 0
    route_override: Optional[Route] = None
    context: Dict[str, object] = field(default_factory=dict)

@dataclass
class ProfileAnalysis:
    """
    DEPRECATED v13.0: Logic moved to HOP1_ProfileAnalysisAgent.
    Output is now state/1_profile_analysis.json
    This class is kept for type hinting in legacy models if needed.
    """
    archetype: Archetype
    confidence: float
    reasoning: str
    key_indicators: List[str]
    needs_manual_override: bool = False

@dataclass
class MessageClaim:
    """NEW v11.6: Individual claim with confidence (FEATURE 1.2)"""
    text: str
    confidence: float
    supporting_sources: List[str]
    source_weights: List[float]

@dataclass
class RAGCritique:
    """NEW v11.6: RAG quality critique (FEATURE 1.4)"""
    confidence_score: float
    gaps_identified: List[str]
    refinement_tasks: List[str]
    reasoning: str
    is_sufficient: bool = False

@dataclass
class RAGResult:
    """
    Single RAG retrieval result with metadata.
    Used by HOP-2 ResearchAgent.
    """
    source: str
    source_type: str
    text: str
    extracted_keywords: List[str]
    source_weight: float
    age_days: int
    recipient_specific: bool
    confidence: float = 1.0


# ============================================
# Merged from: apps_lic/L2_execution/data_models_models_2.py
# ============================================
"""Dataclass models for data_models."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .data_models_models_2 import *

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


# ============================================
# Merged from: apps_lic/L2_execution/data_models_models_3.py
# ============================================
"""Dataclass models for data_models."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .data_models_models_3 import *

@dataclass
class QAReport:
    """
    DEPRECATED v13.0: Logic moved to HOP8_QAReportAgent.
    Output is now a persistent .md file.
    This class is kept for type hinting in legacy models if needed.
    """
    mission_id: str
    validation_results: List[ValidationResult]
    passed: bool
    timestamp: str

