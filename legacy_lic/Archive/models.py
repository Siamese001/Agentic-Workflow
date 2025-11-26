# File: models.py
# Description: Data models, enumerations, and custom exceptions for the LIC workflow.

__version__ = "11.10"

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Callable

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class Route(Enum):
    """Message delivery routes"""
    INMAIL = "INMAIL"
    CONNECTION_REQ = "CONNECTION_REQ"
    EMAIL = "EMAIL"
    FOLLOW_UP = "FOLLOW_UP"

class Archetype(Enum):
    """Recipient archetypes for personalization - v11.6 4-archetype standard"""
    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    SENIOR_TA = "SENIOR_TA"  # NEW v11.6: Technical Authority/Staff Engineer
    RECRUITER = "RECRUITER"

class EventType(Enum):
    """Event types for message bus"""
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    PROFILE_ANALYSIS_COMPLETED = "PROFILE_ANALYSIS_COMPLETED"
    RESEARCH_COMPLETED = "RESEARCH_COMPLETED"
    SCAFFOLD_COMPLETED = "SCAFFOLD_COMPLETED"
    GENERATION_COMPLETED = "GENERATION_COMPLETED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
    GATE_APPROVED = "GATE_APPROVED"
    GATE_REJECTED = "GATE_REJECTED"
    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"
    CHECKPOINT_VERIFIED = "CHECKPOINT_VERIFIED"
    FAILURE_CLASSIFIED = "FAILURE_CLASSIFIED"
    SECTION_LOCKED = "SECTION_LOCKED"
    CONTAMINATION_DETECTED = "CONTAMINATION_DETECTED"
    REFLEXION_TRIGGERED = "REFLEXION_TRIGGERED"
    CIRCUIT_BREAKER_TRIGGERED = "CIRCUIT_BREAKER_TRIGGERED"
    MANUAL_OVERRIDE_REQUESTED = "MANUAL_OVERRIDE_REQUESTED"

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class ValidationSeverity(Enum):
    """Validation result severity levels - v10.22 standard"""
    CRITICAL = "CRITICAL"  # Halt immediately
    HIGH = "HIGH"          # Halt immediately
    MEDIUM = "MEDIUM"      # Regenerate, no halt
    INFO = "INFO"          # Log only

class ConstraintFailureType(Enum):
    """Types of constraint failures for adaptive retry"""
    MECHANICAL = "MECHANICAL"      # Word count, char count, structural
    CREATIVE = "CREATIVE"          # Placeholders, generic content
    SEMANTIC = "SEMANTIC"          # Forbidden words, tone violations
    CONFLICT = "CONFLICT"          # Impossible constraint combinations

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Blocking requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery

class FailureClassifier(Enum):
    """
    NEW v11.10: Classifies S6 validation failures to determine retry strategy.
    - CREATIVE_FAILURE: Retried by S5 (e.g., temp escalation).
    - FACTUAL_FAILURE: Throws FactualGapError, triggering S6->S2 meta-loop.
    """
    CREATIVE_FAILURE = "CREATIVE_FAILURE"  # e.g., tone, forbidden verbs
    FACTUAL_FAILURE = "FACTUAL_FAILURE"    # e.g., missing metric context, hallucination

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class FactualGapError(Exception):
    """
    NEW v11.10: Custom exception raised by S5 when a FACTUAL failure (not
    creative) is detected by S6. This signals the S6->S2 "Meta-Loop"
    in the WorkflowOrchestrator to trigger a full re-planning cycle.
    """
    pass

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is OPEN"""
    pass

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class OutreachMission:
    """Complete mission specification"""
    mission_id: str
    sender_profile: Dict[str, Any]
    recipient_profile: Dict[str, Any]
    job_description: Dict[str, Any]
    connection_status: str = "not_connected"
    prior_message_count: int = 0
    route_override: Optional[Route] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProfileAnalysis:
    """Analysis of recipient profile for archetype classification"""
    archetype: Archetype
    confidence: float
    reasoning: str
    key_indicators: List[str]
    needs_manual_override: bool = False
    critique_history: List[str] = field(default_factory=list)

@dataclass
class RAGResult:
    """Single RAG retrieval result with metadata"""
    source: str
    source_type: str
    text: str
    extracted_keywords: List[str]
    source_weight: float
    age_days: int
    recipient_specific: bool
    confidence: float = 1.0

@dataclass
class SenderGroundingWhitelists:
    """
    NEW v11.9: Extracted sender grounding facts from RAG
    Used to validate "my team" / "our product" claims in generation
    """
    team_members: List[str] = field(default_factory=list)  # Names extracted from RAG
    products: List[str] = field(default_factory=list)      # Product names from RAG
    case_studies: List[str] = field(default_factory=list)  # Client/case study names
    raw_evidence: Dict[str, List[str]] = field(default_factory=dict)  # Category → source snippets

@dataclass
class ResearchContext:
    """Aggregated research findings"""
    recipient_insights: List[str]
    company_context: List[str]
    recent_activity: List[str]
    rag_results: List[RAGResult]
    signal_score: float = 0.0
    reflexion_iterations: int = 0
    prior_applications: List[Dict[str, Any]] = field(default_factory=list)
    mission_context: Dict[str, Any] = field(default_factory=dict)
    sender_context: List[str] = field(default_factory=list)
    sender_grounding: Optional[SenderGroundingWhitelists] = None
    adversarial_findings: List[str] = field(default_factory=list) # NEW v11.10

@dataclass
class MessageScaffold:
    """Structural scaffold for message generation"""
    route: Route
    archetype: Archetype
    sections: Dict[str, Dict[str, Any]]
    constraints: Dict[str, Any]
    locked_sections: Set[str] = field(default_factory=set)
    context_aware_cta: bool = False

@dataclass
class GeneratedMessage:
    """Generated message with metadata"""
    content: str
    word_count: int
    char_count: int
    route: Route
    archetype: Archetype
    generation_temperature: float
    generation_attempts: int
    locked_sections: Set[str]
    checksum: str

@dataclass
class ValidationResult:
    """Result from validation check"""
    passed: bool
    severity: ValidationSeverity
    rule_id: str
    message: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class QAReport:
    """Comprehensive QA report"""
    mission_id: str
    validation_results: List[ValidationResult]
    critical_issues: int
    high_issues: int
    errors: int
    warnings: int
    passed: bool
    timestamp: str

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
    is_sufficient: bool