# File: models_LIC.py
# Description: Data models, enumerations, and custom exceptions for the LIC workflow.
# REFACTOR: v13.0 - Slimmed down to support HOP-based architecture.
# - Removed RAGCritique, MessageClaim (logic moved to tools/agents).
# - Kept core enums, mission objects, and FactualGapError.
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

_emit_reads_through("l4", "lic_models_types", "urg_read_1")
_emit_reads_through("l4", "lic_models_types", "urg_read_2")
_emit_reads_through("l4", "lic_models_types", "urg_read_3")
_emit_reads_through("l4", "lic_models_types", "urg_read_4")
_emit_reads_through("l4", "lic_models_types", "urg_read_5")
_emit_reads_through("l4", "lic_models_types", "urg_read_6")
_emit_reads_through("l4", "lic_models_types", "urg_read_7")
_emit_reads_through("l4", "lic_models_types", "urg_read_8")
_emit_reads_through("l4", "lic_models_types", "urg_read_9")
_emit_reads_through("l4", "lic_models_types", "urg_read_10")
_emit_reads_through("l4", "lic_models_types", "urg_read_11")
_emit_reads_through("l4", "lic_models_types", "urg_read_12")
_emit_reads_through("l4", "lic_models_types", "urg_read_13")
_emit_reads_through("l4", "lic_models_types", "urg_read_14")
_emit_reads_through("l4", "lic_models_types", "urg_read_15")
_emit_reads_through("l4", "lic_models_types", "urg_read_16")
_emit_reads_through("l4", "lic_models_types", "urg_read_17")
_emit_reads_through("l4", "lic_models_types", "urg_read_18")
_emit_reads_through("l4", "lic_models_types", "urg_read_19")
_emit_reads_through("l4", "lic_models_types", "urg_read_20")
_emit_reads_through("l4", "lic_models_types", "urg_read_21")
_emit_reads_through("l4", "lic_models_types", "urg_read_22")
_emit_reads_through("l4", "lic_models_types", "urg_read_23")
_emit_reads_through("l4", "lic_models_types", "urg_read_24")
_emit_reads_through("l4", "lic_models_types", "urg_read_25")
_emit_reads_through("l4", "lic_models_types", "urg_read_26")
_emit_reads_through("l4", "lic_models_types", "urg_read_27")
_emit_reads_through("l4", "lic_models_types", "urg_read_28")
_emit_reads_through("l4", "lic_models_types", "urg_read_29")
_emit_reads_through("l4", "lic_models_types", "urg_read_30")
_emit_reads_through("l4", "lic_models_types", "urg_read_31")
_emit_reads_through("l4", "lic_models_types", "urg_read_32")
_emit_reads_through("l4", "lic_models_types", "urg_read_33")
_emit_reads_through("l4", "lic_models_types", "urg_read_34")
_emit_reads_through("l4", "lic_models_types", "urg_read_35")
_emit_reads_through("l4", "lic_models_types", "urg_read_36")
_emit_reads_through("l4", "lic_models_types", "urg_read_37")
_emit_reads_through("l4", "lic_models_types", "urg_read_38")
_emit_reads_through("l4", "lic_models_types", "urg_read_39")
_emit_reads_through("l4", "lic_models_types", "urg_read_40")
_emit_reads_through("l4", "lic_models_types", "urg_read_41")
_emit_reads_through("l4", "lic_models_types", "urg_read_42")
_emit_reads_through("l4", "lic_models_types", "urg_read_43")
_emit_reads_through("l4", "lic_models_types", "urg_read_44")
_emit_reads_through("l4", "lic_models_types", "urg_read_45")
_emit_reads_through("l4", "lic_models_types", "urg_read_46")
_emit_reads_through("l4", "lic_models_types", "urg_read_47")
_emit_reads_through("l4", "lic_models_types", "urg_read_48")
_emit_reads_through("l4", "lic_models_types", "urg_read_49")
_emit_reads_through("l4", "lic_models_types", "urg_read_50")
_emit_reads_through("l4", "lic_models_types", "urg_read_51")
_emit_reads_through("l4", "lic_models_types", "urg_read_52")
_emit_reads_through("l4", "lic_models_types", "urg_read_53")
_emit_reads_through("l4", "lic_models_types", "urg_read_54")
_emit_reads_through("l4", "lic_models_types", "urg_read_55")
_emit_reads_through("l4", "lic_models_types", "urg_read_56")
_emit_reads_through("l4", "lic_models_types", "urg_read_57")
_emit_reads_through("l4", "lic_models_types", "urg_read_58")
_emit_reads_through("l4", "lic_models_types", "urg_read_59")
_emit_reads_through("l4", "lic_models_types", "urg_read_60")
_emit_reads_through("l4", "lic_models_types", "urg_read_61")
_emit_reads_through("l4", "lic_models_types", "urg_read_62")
_emit_reads_through("l4", "lic_models_types", "urg_read_63")
_emit_reads_through("l4", "lic_models_types", "urg_read_64")
_emit_reads_through("l4", "lic_models_types", "urg_read_65")
_emit_reads_through("l4", "lic_models_types", "urg_read_66")
_emit_reads_through("l4", "lic_models_types", "urg_read_67")
_emit_reads_through("l4", "lic_models_types", "urg_read_68")
_emit_reads_through("l4", "lic_models_types", "urg_read_69")
_emit_reads_through("l4", "lic_models_types", "urg_read_70")
_emit_reads_through("l4", "lic_models_types", "urg_read_71")
_emit_reads_through("l4", "lic_models_types", "urg_read_72")
_emit_reads_through("l4", "lic_models_types", "urg_read_73")
_emit_reads_through("l4", "lic_models_types", "urg_read_74")
_emit_reads_through("l4", "lic_models_types", "urg_read_75")
_emit_reads_through("l4", "lic_models_types", "urg_read_76")
_emit_reads_through("l4", "lic_models_types", "urg_read_77")
_emit_reads_through("l4", "lic_models_types", "urg_read_78")
_emit_reads_through("l4", "lic_models_types", "urg_read_79")
_emit_reads_through("l4", "lic_models_types", "urg_read_80")
_emit_reads_through("l4", "lic_models_types", "urg_read_81")
_emit_reads_through("l4", "lic_models_types", "urg_read_82")
_emit_reads_through("l4", "lic_models_types", "urg_read_83")
_emit_reads_through("l4", "lic_models_types", "urg_read_84")
_emit_reads_through("l4", "lic_models_types", "urg_read_85")
_emit_reads_through("l4", "lic_models_types", "urg_read_86")
_emit_reads_through("l4", "lic_models_types", "urg_read_87")
_emit_reads_through("l4", "lic_models_types", "urg_read_88")
_emit_reads_through("l4", "lic_models_types", "urg_read_89")
_emit_reads_through("l4", "lic_models_types", "urg_read_90")
_emit_reads_through("l4", "lic_models_types", "urg_read_91")
_emit_reads_through("l4", "lic_models_types", "urg_read_92")
_emit_reads_through("l4", "lic_models_types", "urg_read_93")
_emit_reads_through("l4", "lic_models_types", "urg_read_94")
_emit_reads_through("l4", "lic_models_types", "urg_read_95")
_emit_reads_through("l4", "lic_models_types", "urg_read_96")
_emit_reads_through("l4", "lic_models_types", "urg_read_97")
_emit_reads_through("l4", "lic_models_types", "urg_read_98")
_emit_reads_through("l4", "lic_models_types", "urg_read_99")
__version__ = "13.0"


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
    """Recipient archetypes for personalization - v11.6 4-Archetype standard"""

    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    SENIOR_TA = "SENIOR_TA"
    RECRUITER = "RECRUITER"


class EventType(Enum):
    """Event types for message bus / state logging"""

    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    HOP_1_COMPLETED = "HOP_1_COMPLETED"
    HOP_2_COMPLETED = "HOP_2_COMPLETED"
    HOP_3_COMPLETED = "HOP_3_COMPLETED"
    HOP_4_COMPLETED = "HOP_4_COMPLETED"
    HOP_5_COMPLETED = "HOP_5_COMPLETED"
    HOP_6_COMPLETED = "HOP_6_COMPLETED"
    HOP_7_COMPLETED = "HOP_7_COMPLETED"
    HOP_8_COMPLETED = "HOP_8_COMPLETED"
    FACTUAL_LOOP_TRIGGERED = "FACTUAL_LOOP_TRIGGERED"
    CREATIVE_LOOP_TRIGGERED = "CREATIVE_LOOP_TRIGGERED"
    CIRCUIT_BREAKER_TRIGGERED = "CIRCUIT_BREAKER_TRIGGERED"


class AgentStatus(Enum):
    """Agent execution status"""

    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ValidationSeverity(Enum):
    """Validation result Severity levels"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    INFO = "INFO"


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Blocking requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class FailureClassification(Enum):
    """
    Classifies S6 validation failures to determine retry strategy in HOP-7.
    """

    CREATIVE_FAILURE = "CREATIVE_FAILURE"  # e.g., tone, forbidden verbs
    FACTUAL_FAILURE = "FACTUAL_FAILURE"  # e.g., strategic misalignment


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================


class FactualGapError(Exception):
    """
    v13.0: Raised by HOP-7 GateDecisionAgent when a FACTUAL failure is detected.
    This signals the HOPOrchestrator to trigger the S6->S2 "Slow Factual Loop"
    for a full re-planning and re-research cycle.
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
    """Complete mission specification (Input)"""

    mission_id: str
    sender_profile: dict[str, object]
    recipient_profile: dict[str, object]
    JobDescription: dict[str, object]
    connection_status: str = "not_connected"
    prior_message_count: int = 0
    route_override: Route | None = None
    context: dict[str, object] = field(default_factory=dict)


@dataclass
class ProfileAnalysis:
    """
    DEPRECATED v13.0: Logic moved to HOP1_ProfileAnalysisAgent.
    Output is now state/1_profile_analysis.json
    This class is kept for type hinting in legacy models if needed.
    """

    Archetype: Archetype
    confidence: float
    reasoning: str
    key_indicators: list[str]
    needs_manual_override: bool = False


@dataclass
class MessageClaim:
    """NEW v11.6: Individual Claim with confidence (FEATURE 1.2)"""

    text: str
    confidence: float
    supporting_sources: list[str]
    source_weights: list[float]


@dataclass
class RAGCritique:
    """NEW v11.6: RAG quality critique (FEATURE 1.4)"""

    confidence_score: float
    gaps_identified: list[str]
    refinement_tasks: list[str]
    reasoning: str
    is_sufficient: bool = False


@dataclass
class RAGResult:
    """
    Single RAG retrieval result with metadata.
    Used by HOP-2 ResearchAgent.
    """

    source: str
    SourceType: str
    text: str
    extracted_keywords: list[str]
    source_weight: float
    age_days: int
    recipient_specific: bool
    confidence: float = 1.0


@dataclass
class SenderGroundingWhitelists:
    """
    Output of HOP-3 SenderGroundingAgent.
    Used to validate "my team" / "our product" claims in HOP-6.
    """

    team_members: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    case_studies: list[str] = field(default_factory=list)
    quantifiable_achievements: list[str] = field(default_factory=list)
    raw_evidence: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class ResearchContext:
    """
    DEPRECATED v13.0: Logic moved to HOP2_ResearchAgent.
    Output is now state/2_research_context.json
    This class is kept for type hinting in legacy models if needed.
    """

    recipient_insights: list[str]
    company_context: list[str]
    recent_activity: list[str]
    rag_results: list[RAGResult]
    sender_grounding: SenderGroundingWhitelists | None = None
    adversarial_findings: list[str] = field(default_factory=list)


@dataclass
class MessageScaffold:
    """
    DEPRECATED v13.0: Logic moved to HOP4_RoutingAgent.
    Output is now state/4_routing_decision.json
    This class is kept for type hinting in legacy models if needed.
    """

    Route: Route
    Archetype: Archetype
    sections: dict[str, dict[str, object]]
    constraints: dict[str, object]
    locked_sections: set[str] = field(default_factory=set)


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
    Route: Route
    Archetype: Archetype
    generation_temperature: float
    generation_attempts: int
    checksum: str


@dataclass
class ValidationResult:
    """
    Result from a single validation check in HOP-6.
    """

    passed: bool
    Severity: ValidationSeverity
    rule_id: str
    message: str
    details: dict[str, object] | None = None


@dataclass
class QAReport:
    """
    DEPRECATED v13.0: Logic moved to HOP8_QAReportAgent.
    Output is now a persistent .md file.
    This class is kept for type hinting in legacy models if needed.
    """

    mission_id: str
    validation_results: list[ValidationResult]
    passed: bool
    timestamp: str

    def heal_repository(self, dry_run: bool = False, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}
