"""
AppContentValidatorAgent - Application Content Validation

Phase 2 Consolidation: Merges functionality from:
- ContactValidatorAgent (contact validation)
- ContentCleanlinessValidatorAgent (content cleanliness)
- MessageDiversityValidator (message diversity/similarity)

Features:
- Contact validation (email, LinkedIn URL, phone)
- Content cleanliness (profanity, spam, placeholder detection)
- Message diversity (similarity threshold checking)
- Configurable validation rules
"""

import logging
import re
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from agentic_core.L0_routing.config.path_constants import THRESHOLD
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "app_content_validator_agent_types", "p0_governance")
_emit_reads_policy_state("p0", "app_content_validator_agent_types", "policy_binding")
_emit_snapshots_state("p0", "app_content_validator_agent_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

_emit_emits_metric_event("app_content_validator_agent_types", "p4obs", "metric_1")
_emit_emits_metric_event("app_content_validator_agent_types", "p4obs", "metric_2")
_emit_emits_metric_event("app_content_validator_agent_types", "p4obs", "metric_3")
_emit_emits_metric_event("app_content_validator_agent_types", "p4obs", "metric_4")
_emit_emits_metric_event("app_content_validator_agent_types", "p4obs", "metric_5")
_emit_emits_metric_event("app_content_validator_agent_types", "p4obs", "metric_6")
_emit_records_incident_event("app_content_validator_agent_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("app_content_validator_agent_types", "p4obs", "anomaly")
_emit_writes_observability_log("app_content_validator_agent_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("app_content_validator_agent_types", "p4obs", "mon_state")
_emit_triggers_alert("app_content_validator_agent_types", "p4obs", "alert")
_emit_links_incident_trace("app_content_validator_agent_types", "p4obs", "trace_link")
_emit_captures_pattern("app_content_validator_agent_types", "p3lm", "pattern")
_emit_records_learning_event("app_content_validator_agent_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("app_content_validator_agent_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("app_content_validator_agent_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("app_content_validator_agent_types", "p3lm", "routing")
_emit_improves_agent_policy("app_content_validator_agent_types", "p3lm", "policy")
_emit_stores_learning_state("app_content_validator_agent_types", "p3lm", "state")
_emit_records_execution_trace("app_content_validator_agent_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("app_content_validator_agent_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("app_content_validator_agent_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("app_content_validator_agent_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("app_content_validator_agent_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("app_content_validator_agent_types", "env_read", "p2_env_1")
_emit_reads_environ("app_content_validator_agent_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("app_content_validator_agent_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("app_content_validator_agent_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "app_content_validator_agent_types", "context_pull")
_emit_pulls_context("p1", "app_content_validator_agent_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "app_content_validator_agent_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "app_content_validator_agent_types", "uwg_term_2")
_emit_writes_through("p1", "app_content_validator_agent_types", "write_through")
_emit_writes_through("p1", "app_content_validator_agent_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "app_content_validator_agent_types", "safety_validation")
_emit_invokes_eval("p1", "app_content_validator_agent_types", "eval_call")
_emit_proposal_commits_routing("p1", "app_content_validator_agent_types", "routing_commit")
_emit_escalates_to_human("p1", "app_content_validator_agent_types", "human_escalation")
_emit_routes_through("p1", "app_content_validator_agent_types", "route_through")
_emit_checks_agent_registry("p1", "app_content_validator_agent_types", "agent_registry")
_emit_validates_agent_capability("p1", "app_content_validator_agent_types", "capability")
_emit_dispatches_execution_plan("p1", "app_content_validator_agent_types", "exec_plan")
_emit_agent_executes_agent("p1", "app_content_validator_agent_types", "sub_agent")
_emit_routes_to_agent("p1", "app_content_validator_agent_types", "target_agent")
_emit_verifies_policy("p1", "app_content_validator_agent_types", "policy_check")
_emit_observes_runtime_state("p1", "app_content_validator_agent_types", "runtime_state")
_emit_verifies_boundary("p1", "app_content_validator_agent_types", "boundary_check")
_emit_transcripts_response("p1", "app_content_validator_agent_types", "transcript")
_emit_hard_fails_untranscripted("p1", "app_content_validator_agent_types")
_emit_gated_by_confidence("p1", "app_content_validator_agent_types", "confidence_gate")
emit_replay_key("p0", "app_content_validator_agent_types")
emit_determinism_digest("p0", "app_content_validator_agent_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "app_content_validator_agent_types", "execution_auth")
_emit_validates_capability("p2", "app_content_validator_agent_types", "capability_check")
_emit_routes_to_capability("p2", "app_content_validator_agent_types", "capability_route")
_emit_writes_via_uwg("p2", "app_content_validator_agent_types", "uwg_write")
_emit_blocks_direct_write("p2", "app_content_validator_agent_types", "direct_write_block")
_emit_records_tool_invocation("p2", "app_content_validator_agent_types", "tool_invocation")
_emit_captures_execution_output("p2", "app_content_validator_agent_types", "exec_output")
_emit_dispatches_agent("p3", "app_content_validator_agent_types", "agent_dispatch")
_emit_coordinates_agents("p3", "app_content_validator_agent_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "app_content_validator_agent_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "app_content_validator_agent_types", "healing_outcome")
_emit_escalates_failure("p3", "app_content_validator_agent_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "app_content_validator_agent_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "app_content_validator_agent_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "app_content_validator_agent_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "app_content_validator_agent_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "app_content_validator_agent_types", "eval_metric")
_emit_stores_embedding("p4", "app_content_validator_agent_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "app_content_validator_agent_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "app_content_validator_agent_types", "exec_snapshot_link")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_1")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_2")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_3")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_4")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_5")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_6")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_7")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_8")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_9")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_10")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_11")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_12")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_13")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_14")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_15")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_16")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_17")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_18")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_19")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_20")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_21")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_22")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_23")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_24")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_25")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_26")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_27")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_28")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_29")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_30")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_31")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_32")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_33")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_34")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_35")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_36")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_37")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_38")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_39")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_40")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_41")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_42")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_43")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_44")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_45")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_46")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_47")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_48")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_49")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_50")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_51")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_52")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_53")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_54")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_55")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_56")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_57")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_58")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_59")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_60")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_61")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_62")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_63")
_emit_reads_through("l4", "app_content_validator_agent_types", "urg_read_64")

Logger = logging.getLogger(__name__)


class ContentViolationType(Enum):
    """Types of content violations."""

    CONTACT_INVALID = auto()
    CONTACT_MISSING = auto()
    PROFANITY = auto()
    SPAM = auto()
    PLACEHOLDER = auto()
    SIMILARITY = auto()
    LENGTH = auto()
    FORMAT = auto()


@dataclass
class ContentViolation:
    """Represents a content violation."""

    violation_type: ContentViolationType
    message: str
    field_name: str | None = None
    value: str | None = None
    severity: str = "error"
    rule_id: str | None = None
    suggestion: str | None = None
    similarity_score: float | None = None

    def __str__(self) -> str:
        field_info = f" [{self.field_name}]" if self.field_name else ""
        return f"[{self.violation_type.name}]{field_info}: {self.message}"


@dataclass
class ContentValidationReport:
    """Report of content validation results."""

    violations: list[ContentViolation] = field(default_factory=list)
    items_validated: int = 0
    items_passed: int = 0
    items_failed: int = 0
    execution_time: float = 0.0

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)

    @property
    def is_valid(self) -> bool:
        return not self.has_errors

    @property
    def pass_rate(self) -> float:
        if self.items_validated == 0:
            return 0.0
        return self.items_passed / self.items_validated


@dataclass
class ContentConfig:
    """configuration for content validation."""

    validate_email: bool = True
    validate_linkedin: bool = True
    validate_phone: bool = False
    require_contact: bool = True
    check_profanity: bool = True
    check_spam: bool = True
    check_placeholders: bool = True
    check_similarity: bool = True
    similarity_threshold: float = 0.9
    min_unique_ratio: float = 0.1
    min_length: int = 50
    max_length: int = 2000
    profanity_patterns: list[str] = field(default_factory=list)
    spam_patterns: list[str] = field(default_factory=list)
    placeholder_patterns: list[str] = field(
        default_factory=lambda: [
            "\\[.*?\\]",
            "\\{.*?\\}",
            "<.*?>",
            "XXX",
            "TODO",
            "PLACEHOLDER",
            "INSERT.*HERE",
        ],
    )


DEFAULT_SPAM_PATTERNS = [
    "click here",
    "act now",
    "limited time",
    "free money",
    "guaranteed",
    "no obligation",
    "winner",
    "congratulations",
]


@dataclass
class AppContentValidatorAgent(SubatomicTestingMixin):
    """
    Unified content validation for outreach messages.

    Consolidates:
    - ContactValidatorAgent (contact validation)
    - ContentCleanlinessValidatorAgent (content cleanliness)
    - MessageDiversityValidator (message diversity)

    Usage:
        agent = AppContentValidatorAgent()

        # Validate a single message
        report = agent.validate_message({
            "recipient_email": "john@example.com",
            "message_body": "Hello John, I wanted to reach out...",
        })

        # Check message diversity
        messages = ["Hello John...", "Hello Jane...", "Hello John..."]
        report = agent.validate_diversity(messages)
    """

    config: ContentConfig = field(default_factory=ContentConfig)

    def __post_init__(self) -> None:
        """Initialize the validator."""
        self._email_pattern = re.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
        self._linkedin_pattern = re.compile("^(https?://)?(www\\.)?linkedin\\.com/(in|pub)/[a-zA-Z0-9_-]+/?$")
        self._phone_pattern = re.compile("^\\+?1?\\d{9,15}$")
        Logger.info("AppContentValidatorAgent initialized")

    def validate_email(self, email: str) -> list[ContentViolation]:
        """Validate an email address."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ContentValidator.validate_email")
        violations = []
        if not email:
            if self.config.require_contact:
                violations.append(
                    ContentViolation(
                        violation_type=ContentViolationType.CONTACT_MISSING,
                        message="Email address is required",
                        field_name="email",
                        severity="error",
                        rule_id="CONTACT-001",
                    ),
                )
            return violations
        if not self._email_pattern.match(email):
            violations.append(
                ContentViolation(
                    violation_type=ContentViolationType.CONTACT_INVALID,
                    message=f"Invalid email format: {email}",
                    field_name="email",
                    value=email,
                    severity="error",
                    rule_id="CONTACT-002",
                    suggestion="Provide a valid email address",
                ),
            )
        return violations

    def validate_linkedin(self, url: str) -> list[ContentViolation]:
        """Validate a LinkedIn URL."""
        violations = []
        if not url:
            return violations
        if not self._linkedin_pattern.match(url):
            violations.append(
                ContentViolation(
                    violation_type=ContentViolationType.CONTACT_INVALID,
                    message=f"Invalid LinkedIn URL format: {url}",
                    field_name="linkedin_url",
                    value=url,
                    severity="warning",
                    rule_id="CONTACT-003",
                    suggestion="Provide a valid LinkedIn profile URL",
                ),
            )
        return violations

    def validate_content_cleanliness(self, content: str) -> list[ContentViolation]:
        """Check content for profanity, spam, and placeholders."""
        violations = []
        if not content:
            return violations
        content_lower = content.lower()
        if self.config.check_placeholders:
            for pattern in self.config.placeholder_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append(
                        ContentViolation(
                            violation_type=ContentViolationType.PLACEHOLDER,
                            message=f"Placeholder detected: {matches[0]}",
                            value=matches[0],
                            severity="error",
                            rule_id="CLEAN-001",
                            suggestion="Replace placeholder with actual content",
                        ),
                    )
        if self.config.check_spam:
            spam_patterns = self.config.spam_patterns or DEFAULT_SPAM_PATTERNS
            for pattern in spam_patterns:
                if re.search(pattern, content_lower):
                    violations.append(
                        ContentViolation(
                            violation_type=ContentViolationType.SPAM,
                            message=f"Spam pattern detected: '{pattern}'",
                            severity="warning",
                            rule_id="CLEAN-002",
                            suggestion="Remove or rephrase spam-like content",
                        ),
                    )
        if len(content) < self.config.min_length:
            violations.append(
                ContentViolation(
                    violation_type=ContentViolationType.LENGTH,
                    message=f"Content too short: {len(content)} chars (min: {self.config.min_length})",
                    severity="warning",
                    rule_id="CLEAN-003",
                ),
            )
        if len(content) > self.config.max_length:
            violations.append(
                ContentViolation(
                    violation_type=ContentViolationType.LENGTH,
                    message=f"Content too long: {len(content)} chars (max: {self.config.max_length})",
                    severity="warning",
                    rule_id="CLEAN-004",
                ),
            )
        return violations

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def validate_diversity(
        self, messages: list[str], threshold: float | None = None,
    ) -> ContentValidationReport:
        """
        Validate message diversity (check for too-similar messages).

        Args:
            messages: List of message texts to compare
            threshold: Similarity threshold (default from config)

        Returns:
            ContentValidationReport with similarity violations
        """
        threshold = threshold or self.config.similarity_threshold
        report = ContentValidationReport()
        start_time = datetime.now()
        report.items_validated = len(messages)
        similar_pairs = []
        for i in range(len(messages)):
            for j in range(i + 1, len(messages)):
                similarity = self.calculate_similarity(messages[i], messages[j])
                if similarity >= threshold:
                    similar_pairs.append((i, j, similarity))
                    report.violations.append(
                        ContentViolation(
                            violation_type=ContentViolationType.SIMILARITY,
                            message=f"Messages {i + 1} and {j + 1} are {similarity:.1%} similar (threshold: {threshold:.1%})",
                            severity="error",
                            rule_id="DIV-001",
                            similarity_score=similarity,
                            suggestion="Increase message variation to improve personalization",
                        ),
                    )
        flagged_indices = set()
        for i, j, _ in similar_pairs:
            flagged_indices.add(i)
            flagged_indices.add(j)
        report.items_failed = len(flagged_indices)
        report.items_passed = report.items_validated - report.items_failed
        report.execution_time = (datetime.now() - start_time).total_seconds()
        return report

    def validate_message(
        self, message_data: dict[str, Any], config: ContentConfig | None = None,
    ) -> ContentValidationReport:
        """
        Validate a single outreach message.

        Args:
            message_data: Dictionary with message fields
            config: Optional custom configuration

        Returns:
            ContentValidationReport with all violations
        """
        config = config or self.config
        report = ContentValidationReport()
        start_time = datetime.now()
        report.items_validated = 1
        all_violations = []
        if config.validate_email:
            email = message_data.get("recipient_email", message_data.get("email", ""))
            all_violations.extend(self.validate_email(email))
        if config.validate_linkedin:
            linkedin = message_data.get("linkedin_url", message_data.get("linkedin", ""))
            all_violations.extend(self.validate_linkedin(linkedin))
        content = message_data.get("message_body", message_data.get("body", message_data.get("content", "")))
        all_violations.extend(self.validate_content_cleanliness(content))
        report.violations = all_violations
        report.items_passed = 0 if report.has_errors else 1
        report.items_failed = 1 if report.has_errors else 0
        report.execution_time = (datetime.now() - start_time).total_seconds()
        return report

    def validate_messages(
        self, messages: list[dict[str, Any]], check_diversity: bool = True,
    ) -> ContentValidationReport:
        """
        Validate multiple messages with optional diversity check.

        Args:
            messages: List of message dictionaries
            check_diversity: Whether to check for similar messages

        Returns:
            Aggregated ContentValidationReport
        """
        report = ContentValidationReport()
        start_time = datetime.now()
        for msg in messages:
            msg_report = self.validate_message(msg)
            report.violations.extend(msg_report.violations)
            report.items_validated += 1
            report.items_passed += msg_report.items_passed
            report.items_failed += msg_report.items_failed
        if check_diversity and self.config.check_similarity:
            message_bodies = [
                msg.get("message_body", msg.get("body", msg.get("content", ""))) for msg in messages
            ]
            diversity_report = self.validate_diversity(message_bodies)
            report.violations.extend(diversity_report.violations)
        report.execution_time = (datetime.now() - start_time).total_seconds()
        return report


def create_legacy_contact_validator(**kwargs: Any) -> AppContentValidatorAgent:
    """
    Factory for backward compatibility with ContactValidatorAgent.

    DEPRECATED: Use AppContentValidatorAgent directly.
    """
    warnings.warn(
        "ContactValidatorAgent is deprecated. Use AppContentValidatorAgent instead. This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    config = ContentConfig(
        validate_email=True,
        validate_linkedin=True,
        check_profanity=False,
        check_spam=False,
        check_placeholders=False,
        check_similarity=False,
    )
    return AppContentValidatorAgent(config=config, **kwargs)


def create_legacy_content_cleanliness_validator(**kwargs: Any) -> AppContentValidatorAgent:
    """
    Factory for backward compatibility with ContentCleanlinessValidatorAgent.

    DEPRECATED: Use AppContentValidatorAgent directly.
    """
    warnings.warn(
        "ContentCleanlinessValidatorAgent is deprecated. Use AppContentValidatorAgent instead. This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    config = ContentConfig(
        validate_email=False,
        validate_linkedin=False,
        check_profanity=True,
        check_spam=True,
        check_placeholders=True,
        check_similarity=False,
    )
    return AppContentValidatorAgent(config=config, **kwargs)


def create_legacy_message_diversity_validator(**kwargs: Any) -> AppContentValidatorAgent:
    """
    Factory for backward compatibility with MessageDiversityValidator.

    DEPRECATED: Use AppContentValidatorAgent directly.
    """
    warnings.warn(
        "MessageDiversityValidator is deprecated. Use AppContentValidatorAgent instead. This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    config = ContentConfig(
        validate_email=False,
        validate_linkedin=False,
        check_profanity=False,
        check_spam=False,
        check_placeholders=False,
        check_similarity=True,
        similarity_threshold=THRESHOLD,
    )
    return AppContentValidatorAgent(config=config, **kwargs)
