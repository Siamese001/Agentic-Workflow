#!/usr/bin/env python3
"""
Outreach Engine Core Models
Shared dataclasses and enums for all outreach capabilities
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class Route(Enum):
    """Message delivery routes - Lift & Shift from LIC"""
    CONNECTION_REQ = "CONNECTION_REQ"
    SHORT_NEW = "SHORT_NEW"
    LONG_NEW = "LONG_NEW"
    FOLLOW_UP = "FOLLOW_UP"
    INMAIL = "INMAIL"


class Archetype(Enum):
    """Recipient archetypes for personalization - Lift & Shift from LIC"""
    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    SENIOR_TA = "SENIOR_TA"
    RECRUITER = "RECRUITER"


class ValidationSeverity(Enum):
    """Validation result severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(Enum):
    """Event types for outreach workflow"""
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    ROUTING_COMPLETED = "ROUTING_COMPLETED"
    RAG_COMPLETED = "RAG_COMPLETED"
    GENERATION_COMPLETED = "GENERATION_COMPLETED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"


@dataclass
class ValidationResult:
    """Individual validation result"""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RouteConstraints:
    """Route-specific constraints from LIC routing rules"""
    char_limit: Optional[int]
    word_range: Optional[List[int]]
    signature_format: str
    subject_line_enabled: bool
    attachments_enabled: bool
    cta_format: str
    cta_max_words: Optional[int]
    greeting_format: str
    
    def validate_word_count(self, word_count: int) -> bool:
        """Validate word count against route constraints"""
        if self.word_range is None:
            return True
        return self.word_range[0] <= word_count <= self.word_range[1]
    
    def validate_char_limit(self, char_count: int) -> bool:
        """Validate character limit against route constraints"""
        if self.char_limit is None:
            return True
        return char_count <= self.char_limit


@dataclass
class MessageContext:
    """Complete context for message generation"""
    route: Route
    archetype: Archetype
    sender_profile: Dict
    recipient_profile: Dict
    job_description: Optional[Dict] = None
    rag_results: Optional[Dict] = None
    prior_messages: List[Dict] = field(default_factory=list)
    constraints: Optional[RouteConstraints] = None
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OutreachMission:
    """Outreach mission specification"""
    target_recipient: Dict
    sender_profile: Dict
    job_context: Optional[Dict] = None
    mission_id: str = field(default_factory=lambda: f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RAGEvidence:
    """RAG evidence tracking"""
    source_type: str
    content: str
    relevance_score: float
    authority_score: float
    recency_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RAGResult:
    """RAG pipeline result"""
    query: str
    evidence: List[RAGEvidence] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CTATemplate:
    """Call-to-action template specification"""
    template: str
    variables: Dict[str, str] = field(default_factory=dict)
    word_limit: Optional[int] = None
    examples: List[str] = field(default_factory=list)
    archetype_specific: bool = True


@dataclass
class GreetingTemplate:
    """Greeting template specification"""
    template: str
    format_notes: str
    validation_rules: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SignatureTemplate:
    """Signature template specification"""
    format_type: str
    template: str
    requires_full_name: bool = True
    requires_title: bool = False


@dataclass
class ToneProfile:
    """Archetype-specific tone profile"""
    message_tone: str
    verb_preference: List[str]
    jargon_level: str
    formality: str
    focus_area: str


@dataclass
class EntityConstraint:
    """Entity grounding constraint"""
    entity_type: str
    allowed_sources: List[str]
    validation_method: str
    enforcement_level: str  # SOFT, HARD, BLOCK


@dataclass
class ValidationRule:
    """Validation rule specification"""
    rule_id: str
    name: str
    phase: str  # PRE_GENERATION, POST_GENERATION, DURING_GENERATION
    description: str
    enforcement: str
    severity: ValidationSeverity


@dataclass
class MessageAssembly:
    """K-node assembly result"""
    k1_greeting: str
    k2_subject_line: Optional[str]
    k3_message_body: str
    k4_cta: str
    k5_signature: str
    assembly_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_full_message(self) -> str:
        """Get the complete assembled message"""
        parts = [self.k1_greeting]
        
        if self.k2_subject_line:
            parts.append(f"Subject: {self.k2_subject_line}")
        
        parts.append(self.k3_message_body)
        parts.append(self.k4_cta)
        parts.append(self.k5_signature)
        
        return "\n\n".join(parts)


@dataclass
class SeniorityClassification:
    """Seniority classification result"""
    recipient_type: str
    confidence: float
    classification_rules: List[str]
    title_analysis: Dict[str, Any] = field(default_factory=dict)


# Error classes
class OutreachEngineError(Exception):
    """Base exception for outreach engine"""
    pass


class RoutingError(OutreachEngineError):
    """Routing-related errors"""
    pass


class ValidationError(OutreachEngineError):
    """Validation-related errors"""
    pass


class RAGEngineError(OutreachEngineError):
    """RAG pipeline errors"""
    pass


class ConstraintViolationError(OutreachEngineError):
    """Constraint violation errors"""
    pass
