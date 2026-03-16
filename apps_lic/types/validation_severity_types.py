"""
LIC Validator Rules - Error codes, content cleanliness, and signal quality scoring.

Ported from: archives/legacy_lic/Agentic LIC/validator_rules_LIC.json
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "validation_severity_types", "p0_governance")
_emit_reads_policy_state("p0", "validation_severity_types", "policy_binding")
_emit_snapshots_state("p0", "validation_severity_types", "state_snapshot")
emit_replay_key("p0", "validation_severity_types")
emit_determinism_digest("p0", "validation_severity_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validation_severity_types", "execution_auth")
_emit_validates_capability("p2", "validation_severity_types", "capability_check")
_emit_routes_to_capability("p2", "validation_severity_types", "capability_route")
_emit_writes_via_uwg("p2", "validation_severity_types", "uwg_write")
_emit_blocks_direct_write("p2", "validation_severity_types", "direct_write_block")
_emit_records_tool_invocation("p2", "validation_severity_types", "tool_invocation")
_emit_captures_execution_output("p2", "validation_severity_types", "exec_output")
_emit_dispatches_agent("p3", "validation_severity_types", "agent_dispatch")
_emit_coordinates_agents("p3", "validation_severity_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "validation_severity_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "validation_severity_types", "healing_outcome")
_emit_escalates_failure("p3", "validation_severity_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "validation_severity_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validation_severity_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "validation_severity_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "validation_severity_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validation_severity_types", "eval_metric")
_emit_stores_embedding("p4", "validation_severity_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "validation_severity_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validation_severity_types", "exec_snapshot_link")


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ErrorCode:
    """LIC error code definition."""

    code: str
    Severity: ValidationSeverity
    description: str
    remediation: str


@dataclass
class ContentCleanlinessRule:
    """Rule for content cleanliness validation."""

    rule_id: str
    Severity: ValidationSeverity
    ErrorCode: str
    patterns: list[str] = field(default_factory=list)
    max_violations: int = 0


@dataclass
class SignalQualityConfig:
    """configuration for signal quality scoring."""

    source_weights: dict[str, float]
    recency_factors: dict[str, float]
    min_signal_threshold: float = 0.7
    recency_decay_days: int = 90


@dataclass
class ClaimConfidenceConfig:
    """configuration for Claim confidence scoring."""

    min_claim_confidence: float = 0.7
    min_overlap_words: int = 2
    base_confidence_multiplier: float = 1.5
    source_boost_per_source: float = 0.1
    max_source_boost: float = 0.3
    no_source_penalty: float = 0.5
    min_claim_words: int = 3


# Error Code Registry
LIC_ERROR_CODES: dict[str, ErrorCode] = {
    "LIC-E001": ErrorCode(
        code="LIC-E001",
        Severity=ValidationSeverity.CRITICAL,
        description="implementation detected in generated message",
        remediation="Regenerate with explicit anti-implementation constraint",
    ),
    "LIC-E002": ErrorCode(
        code="LIC-E002",
        Severity=ValidationSeverity.CRITICAL,
        description="Per-Claim confidence below threshold (0.70)",
        remediation="Add more RAG sources or remove low-confidence Claim",
    ),
    "LIC-E003": ErrorCode(
        code="LIC-E003",
        Severity=ValidationSeverity.CRITICAL,
        description="Hallucinated Claim without supporting evidence",
        remediation="Remove Claim or add supporting RAG evidence",
    ),
    "LIC-E004": ErrorCode(
        code="LIC-E004",
        Severity=ValidationSeverity.HIGH,
        description="Message too similar to previous message (>0.85)",
        remediation="Increase temperature or add diversity constraint",
    ),
    "LIC-E005": ErrorCode(
        code="LIC-E005",
        Severity=ValidationSeverity.HIGH,
        description="Job title not in first 50 words",
        remediation="Regenerate with job title positioning constraint",
    ),
    "LIC-E006": ErrorCode(
        code="LIC-E006",
        Severity=ValidationSeverity.HIGH,
        description="Company name misspelled",
        remediation="Use exact company name from profile",
    ),
    "LIC-E007": ErrorCode(
        code="LIC-E007",
        Severity=ValidationSeverity.HIGH,
        description="Non-ASCII characters detected",
        remediation="Replace Unicode with ASCII equivalents",
    ),
    "LIC-E008": ErrorCode(
        code="LIC-E008",
        Severity=ValidationSeverity.MEDIUM,
        description="Forbidden corporate verbs detected",
        remediation="Regenerate avoiding: spearheaded, leveraged, etc.",
    ),
    "LIC-E009": ErrorCode(
        code="LIC-E009",
        Severity=ValidationSeverity.MEDIUM,
        description="Weak filler phrases detected",
        remediation="Remove: 'I hope', 'I wanted to', 'just reaching out'",
    ),
    "LIC-E010": ErrorCode(
        code="LIC-E010",
        Severity=ValidationSeverity.HIGH,
        description="Metric lacks supporting keyword context from RAG",
        remediation="Add RAG evidence keywords around Metric or remove Metric",
    ),
    "LIC-E011": ErrorCode(
        code="LIC-E011",
        Severity=ValidationSeverity.HIGH,
        description="Signal quality score below threshold (0.70)",
        remediation="Trigger RAG reflexion for more research",
    ),
    "LIC-E012": ErrorCode(
        code="LIC-E012",
        Severity=ValidationSeverity.CRITICAL,
        description="Circuit breaker OPEN - API unavailable",
        remediation="Wait for circuit breaker timeout or check API",
    ),
    "LIC-E013": ErrorCode(
        code="LIC-E013",
        Severity=ValidationSeverity.CRITICAL,
        description="Constraint pre-flight check failed",
        remediation="Adjust constraints or change Route",
    ),
    "LIC-E014": ErrorCode(
        code="LIC-E014",
        Severity=ValidationSeverity.CRITICAL,
        description="Forbidden voice phrase detected",
        remediation="Regenerate avoiding sender_voice_profile forbidden phrases",
    ),
    "LIC-E015": ErrorCode(
        code="LIC-E015",
        Severity=ValidationSeverity.CRITICAL,
        description="Strategic alignment failure - no keyword overlap with strategic brief",
        remediation="Trigger S6->S2 meta-loop to re-research strategic brief alignment",
    ),
}

# Forbidden verbs list
FORBIDDEN_VERBS: list[str] = [
    "spearheaded",
    "leveraged",
    "utilized",
    "facilitated",
    "orchestrated",
    "championed",
    "pioneered",
    "revolutionized",
    "transformed",
    "optimized",
    "enhanced",
    "streamlined",
    "synergized",
    "enabled",
    "empowered",
    "drove",
    "drive",
]

# Filler patterns
FILLER_PATTERNS: list[str] = [
    r"(?i)\bi hope\b",
    r"(?i)\bhope (this|you) (finds|are|don't)",
    r"(?i)\bi (wanted|would like) to (reach|connect|discuss|share)",
    r"(?i)\bi was wondering if",
    r"(?i)\bperhaps (we|you) could",
    r"(?i)\bif you('re| are) interested",
    r"(?i)\bjust (wanted|reaching|following)",
]

implementation_PATTERNS: list[str] = [
    r"\[.*?\]",
    r"\{.*?\}",
    r"<.*?>",
    r"implementation",
    r"TODO",
    r"XXX",
]

# Unicode replacements for ASCII enforcement
UNICODE_REPLACEMENTS: dict[str, str] = {
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2026": "...",
    "\u00a0": " ",
    "\u2022": "-",
}

# Signal quality source weights
SIGNAL_SOURCE_WEIGHTS: dict[str, float] = {
    "RECIPIENT_LINKEDIN_ABOUT": 1.0,
    "RECIPIENT_RECENT_POST": 0.95,
    "RECIPIENT_COMMENT": 0.85,
    "COMPANY_BLOG_ANNOUNCEMENT": 0.9,
    "COMPANY_PRESS_RELEASE": 0.85,
    "NEWS_ARTICLE": 0.75,
    "NEWS_ARTICLE_COMPANY": 0.75,
    "INDUSTRY_REPORT": 0.7,
    "CONFERENCE_TALK": 0.8,
    "GITHUB_ACTIVITY": 0.75,
    "TWITTER_POST": 0.6,
    "GENERIC_SEARCH": 0.4,
    "STRATEGIC_BRIEF": 1.0,
    "MASTER_RESUME": 1.0,
    "SENDER_KNOWLEDGE_BASE": 1.0,
}

# Recency factors
RECENCY_FACTORS: dict[str, float] = {
    "0-7_days": 1.0,
    "8-30_days": 0.95,
    "31-90_days": 0.85,
    "91-180_days": 0.7,
    "180+_days": 0.5,
}


class LICValidator:
    """Validator for LIC message content."""

    def __init__(self) -> None:
        """Initialize the LIC validator."""
        pass

    def check_forbidden_verbs(self, text: str) -> list:
        """Check for forbidden corporate verbs in text."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LICValidator.check_forbidden_verbs")

        found = []
        text_lower = text.lower()
        for verb in FORBIDDEN_VERBS:
            if verb.lower() in text_lower:
                found.append(verb)
        return found

    def check_filler_phrases(self, text: str) -> list[str]:
        """Check for weak filler phrases in text."""
        found = []
        for pattern in FILLER_PATTERNS:
            if re.search(pattern, text):
                found.append(pattern)
        return found

    def check_implementations(self, text: str) -> list[str]:
        """Check for implementation patterns in text."""
        found = []
        for pattern in implementation_PATTERNS:
            if re.search(pattern, text):
                found.append(pattern)
        return found

    def enforce_ascii(self, text: str) -> str:
        """Replace Unicode characters with ASCII equivalents."""
        result = text
        for unicode_char, ascii_char in UNICODE_REPLACEMENTS.items():
            result = result.replace(unicode_char, ascii_char)
        return result

    def _get_recency_factor(self, recency_days: int) -> float:
        """Get recency factor based on days."""
        if recency_days <= 7:
            return RECENCY_FACTORS["0-7_days"]
        elif recency_days <= 30:
            return RECENCY_FACTORS["8-30_days"]
        elif recency_days <= 90:
            return RECENCY_FACTORS["31-90_days"]
        elif recency_days <= 180:
            return RECENCY_FACTORS["91-180_days"]
        else:
            return RECENCY_FACTORS["180+_days"]

    def _calculate_source_weight(self, source: dict[str, object], recency_days: int | None) -> float:
        """Calculate weight for a single source."""
        SourceType = source.get("SourceType", "GENERIC_SEARCH")
        base_weight = SIGNAL_SOURCE_WEIGHTS.get(SourceType, 0.4)

        if recency_days is not None:
            base_weight *= self._get_recency_factor(recency_days)

        return base_weight

    def calculate_signal_score(
        self,
        sources: list[dict[str, object]],
        recency_days: int | None = None,
    ) -> float:
        """Calculate signal quality score from sources."""
        if not sources:
            return 0.0

        total_weight = sum(self._calculate_source_weight(source, recency_days) for source in sources)
        return min(1.0, total_weight / len(sources))

    def validate_message(self, text: str) -> dict[str, object]:
        """Perform full validation on a message."""
        results: dict[str, object] = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "cleaned_text": self.enforce_ascii(text),
        }

        implementations = self.check_implementations(text)
        if implementations:
            results["is_valid"] = False
            results["errors"].append(
                {
                    "code": "LIC-E001",
                    "message": f"implementations found: {implementations}",
                    "Severity": "CRITICAL",
                },
            )

        # Check forbidden verbs (MEDIUM)
        forbidden = self.check_forbidden_verbs(text)
        if forbidden:
            results["warnings"].append(
                {
                    "code": "LIC-E008",
                    "message": f"Forbidden verbs found: {forbidden}",
                    "Severity": "MEDIUM",
                },
            )

        # Check filler phrases (MEDIUM)
        fillers = self.check_filler_phrases(text)
        if fillers:
            results["warnings"].append(
                {
                    "code": "LIC-E009",
                    "message": f"Filler phrases found: {fillers}",
                    "Severity": "MEDIUM",
                },
            )

        return results


def create_lic_validator() -> LICValidator:
    """builder function to create an LIC validator."""
    return LICValidator()


def get_error_code(code: str) -> ErrorCode | None:
    """Get error code definition by code."""
    return LIC_ERROR_CODES.get(code)


def get_signal_config() -> SignalQualityConfig:
    """Get default signal quality configuration."""
    return SignalQualityConfig(
        source_weights=SIGNAL_SOURCE_WEIGHTS,
        recency_factors=RECENCY_FACTORS,
    )


def get_claim_config() -> ClaimConfidenceConfig:
    """Get default Claim confidence configuration."""
    return ClaimConfidenceConfig()
