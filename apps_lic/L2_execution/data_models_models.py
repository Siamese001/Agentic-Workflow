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

