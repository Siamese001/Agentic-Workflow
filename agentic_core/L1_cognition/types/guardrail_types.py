"""Guardrail Types.

Defines the data structures for constitutional AI guardrails,
content filtering, and safety mechanisms in GraphRAG.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    emit_determinism_digest,  # noqa: E402
    )

_emit_emits_metric_event("guardrail_types", "p4obs", "metric_1")
_emit_emits_metric_event("guardrail_types", "p4obs", "metric_2")
_emit_emits_metric_event("guardrail_types", "p4obs", "metric_3")
_emit_emits_metric_event("guardrail_types", "p4obs", "metric_4")
_emit_emits_metric_event("guardrail_types", "p4obs", "metric_5")
_emit_emits_metric_event("guardrail_types", "p4obs", "metric_6")
_emit_records_incident_event("guardrail_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("guardrail_types", "p4obs", "anomaly")
_emit_writes_observability_log("guardrail_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("guardrail_types", "p4obs", "mon_state")
_emit_triggers_alert("guardrail_types", "p4obs", "alert")
_emit_links_incident_trace("guardrail_types", "p4obs", "trace_link")
_emit_captures_pattern("guardrail_types", "p3lm", "pattern")
_emit_records_learning_event("guardrail_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guardrail_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("guardrail_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guardrail_types", "p3lm", "routing")
_emit_improves_agent_policy("guardrail_types", "p3lm", "policy")
_emit_stores_learning_state("guardrail_types", "p3lm", "state")
_emit_records_execution_trace("guardrail_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guardrail_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guardrail_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guardrail_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guardrail_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guardrail_types", "env_read", "p2_env_1")
_emit_reads_environ("guardrail_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("guardrail_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guardrail_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guardrail_types", "context_pull")
_emit_pulls_context("p1", "guardrail_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "guardrail_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guardrail_types", "uwg_term_2")
_emit_writes_through("p1", "guardrail_types", "write_through")
_emit_writes_through("p1", "guardrail_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "guardrail_types", "safety_validation")
_emit_invokes_eval("p1", "guardrail_types", "eval_call")
_emit_proposal_commits_routing("p1", "guardrail_types", "routing_commit")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_dispatch_entry")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_dispatch_exit")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_tool_invoke")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_tool_complete")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_agent_entry")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_agent_exit")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_uwg_write")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_trace_sign")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_guardrail_check")
emit_determinism_digest("trace_guardrail_types", "guardrail_types_policy_verify")


class GuardrailAction(Enum):
    """Actions that can be taken when a guardrail is triggered."""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    MODIFY = "modify"
    ESCALATE = "escalate"


class GuardrailSeverity(Enum):
    """Severity levels for guardrail violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentType(Enum):
    """Types of content that can be filtered."""
    TEXT = "text"
    CODE = "code"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    PII = "pii"
    TOXICITY = "toxicity"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    SEXUAL_CONTENT = "sexual_content"
    SELF_HARM = "self_harm"
    ILLEGAL_CONTENT = "illegal_content"


@dataclass
class ConstitutionalRule:
    """Represents a constitutional AI rule."""

    rule_id: str
    name: str
    description: str

    # Rule content
    principle: str
    constitution: str

    # Rule configuration
    severity: GuardrailSeverity
    action: GuardrailAction

    # Applicability
    content_types: list[ContentType]
    contexts: list[str]  # "query", "context", "response", "generation"

    # Rule metadata
    category: str
    tags: list[str] = field(default_factory=list)
    version: str = "1.0"
    enabled: bool = True

    # Performance
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0

    # Usage statistics
    trigger_count: int = 0
    last_triggered: datetime | None = None

    def __post_init__(self) -> None:
        """Validate rule configuration."""
        if not self.principle:
            raise ValueError("Constitutional rule must have a principle")
        if not self.constitution:
            raise ValueError("Constitutional rule must have a constitution")


@dataclass
class ContentFilter:
    """Represents a content filter for specific content types."""

    filter_id: str
    name: str
    description: str
    content_type: ContentType
    action: GuardrailAction
    severity: GuardrailSeverity
    category: str

    # Optional fields with defaults
    pattern: str | None = None  # Regex pattern
    keywords: list[str] = field(default_factory=list)
    confidence_threshold: float = 0.7
    tags: list[str] = field(default_factory=list)
    enabled: bool = True

    # Statistics
    match_count: int = 0
    last_matched: datetime | None = None

    def matches(self, content: str) -> tuple[bool, float]:
        """Check if content matches the filter.

        Args:
            content: Content to check

        Returns:
            Tuple of (matches, confidence_score)
        """
        if not content:
            return False, 0.0

        content_lower = content.lower()
        confidence = 0.0

        # Check keywords
        if self.keywords:
            keyword_matches = sum(1 for kw in self.keywords if kw.lower() in content_lower)
            if keyword_matches > 0:
                confidence = min(1.0, keyword_matches / len(self.keywords))

        # Check pattern
        if self.pattern:
            import re
            if re.search(self.pattern, content, re.IGNORECASE):
                confidence = max(confidence, 0.8)

        matches = confidence >= self.confidence_threshold
        return matches, confidence


@dataclass
class GuardrailCheck:
    """Represents a single guardrail check result."""

    check_id: str
    rule_id: str | None  # None for content filters
    filter_id: str | None  # None for constitutional rules
    passed: bool
    confidence: float
    severity: GuardrailSeverity
    reason: str
    evidence: str
    action: GuardrailAction
    check_type: str  # "constitutional", "content_filter"

    # Optional fields with defaults
    matched_content: str | None = None
    modified_content: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailReport:
    """Comprehensive report of guardrail checks."""

    report_id: str
    content_id: str
    content_type: str  # "query", "context", "response", "generation"

    # Overall results
    passed: bool
    overall_score: float
    highest_severity: GuardrailSeverity | None

    # Individual checks
    checks: list[GuardrailCheck]

    # Summary statistics
    total_checks: int
    passed_checks: int
    failed_checks: int
    warnings: int

    # Actions taken
    actions_taken: list[GuardrailAction]
    content_modified: bool
    escalation_required: bool

    # Timing
    check_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_failed_rules(self) -> list[str]:
        """Get list of failed rule IDs."""
        return [check.rule_id for check in self.checks if not check.passed and check.rule_id]

    def get_triggered_filters(self) -> list[str]:
        """Get list of triggered filter IDs."""
        return [check.filter_id for check in self.checks if not check.passed and check.filter_id]


@dataclass
class GuardrailConfig:
    """Configuration for the guardrail system."""

    # General settings
    enabled: bool = True
    strict_mode: bool = False  # Block on any violation vs. warnings

    # Thresholds
    min_confidence_threshold: float = 0.5
    severity_threshold: GuardrailSeverity = GuardrailSeverity.MEDIUM

    # Performance
    max_check_time_ms: float = 1000.0
    enable_caching: bool = True
    cache_ttl_seconds: int = 300

    # Logging
    log_all_checks: bool = False
    log_failures_only: bool = True
    include_content_in_logs: bool = False

    # Escalation
    auto_escalate_critical: bool = True
    escalation_webhook: str | None = None

    # Learning
    enable_feedback_learning: bool = True
    feedback_decay_factor: float = 0.9


@dataclass
class GuardrailMetrics:
    """Metrics for guardrail system performance."""

    # Performance metrics
    avg_check_time_ms: float
    p95_check_time_ms: float
    p99_check_time_ms: float
    checks_per_second: float

    # Quality metrics
    false_positive_rate: float
    false_negative_rate: float
    precision: float
    recall: float

    # Usage metrics
    total_checks: int
    passed_checks: int
    failed_checks: int
    escalation_count: int

    # Rule statistics
    rule_trigger_rates: dict[str, float]
    filter_match_rates: dict[str, float]

    # Severity distribution
    severity_distribution: dict[str, int]

    # Content type distribution
    content_type_distribution: dict[str, int]

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SafetyEvaluation:
    """Result of a safety evaluation."""

    evaluation_id: str
    content_id: str
    overall_safety_score: float  # 0.0 (unsafe) to 1.0 (safe)
    category_scores: dict[str, float]  # Safety scores by category
    risk_level: GuardrailSeverity
    risk_factors: list[str]
    safe_to_proceed: bool
    recommended_actions: list[str]
    evaluation_time_ms: float
    evaluator_version: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_safe(self, threshold: float = 0.7) -> bool:
        """Check if content is safe above threshold."""
        return self.overall_safety_score >= threshold


@dataclass
class GuardrailFeedback:
    """Feedback for improving guardrail performance."""

    feedback_id: str
    check_id: str

    # Feedback content
    was_correct: bool
    actual_severity: GuardrailSeverity | None
    user_action: GuardrailAction | None

    # Context
    content_snippet: str | None
    user_comment: str | None

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    feedback_source: str = "user"  # "user", "automated", "reviewer"


# Export all types
__all__ = [
    "GuardrailAction",
    "GuardrailSeverity",
    "ContentType",
    "ConstitutionalRule",
    "ContentFilter",
    "GuardrailCheck",
    "GuardrailReport",
    "GuardrailConfig",
    "GuardrailMetrics",
    "SafetyEvaluation",
    "GuardrailFeedback",
]
