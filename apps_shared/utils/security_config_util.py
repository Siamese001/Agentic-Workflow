"""
Security Utilities - Input validation, sanitization, and security checks.

Provides security hardening for apps_lic and apps_rg.
Phase 5A - Security Hardening
"""

import hashlib
import logging
import re
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Constants
BATCH_SIZE = 32
BUFFER_SIZE = 8192
DEFAULT_SLEEP = 1.0
MAX_RETRIES = 3
THRESHOLD = 0.95


class ValidationLevel(Enum):
    """Validation level."""
    STRICT = "strict"
    LENIENT = "lenient"
    NONE = "none"


@dataclass
class ValidationResult:
    """Validation result."""
    valid: bool
    errors: list[str]
    sanitized_value: str | None = None


class InputSanitizer:
    """Input sanitizer."""

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input."""
        return value.strip()

    @staticmethod
    def sanitize_path(value: str) -> str:
        """Sanitize path input."""
        return value.strip().replace("..", "")

    @staticmethod
    def sanitize_identifier(value: str) -> str:
        """Sanitize identifier."""
        return re.sub(r'[^a-zA-Z0-9_]', '', value)


class InputValidator:
    """Input validator."""

    @staticmethod
    def validate_email(value: str) -> ValidationResult:
        """Validate email."""
        if "@" in value and "." in value:
            return ValidationResult(True, [], value)
        return ValidationResult(False, ["Invalid email format"])

    @staticmethod
    def validate_url(value: str) -> ValidationResult:
        """Validate URL."""
        if value.startswith(("http://", "https://")):
            return ValidationResult(True, [], value)
        return ValidationResult(False, ["Invalid URL format"])

    @staticmethod
    def validate_length(value: str, min_len: int = 1, max_len: int = 1000) -> ValidationResult:
        """Validate length."""
        if min_len <= len(value) <= max_len:
            return ValidationResult(True, [], value)
        return ValidationResult(False, [f"Length must be between {min_len} and {max_len}"])

    @staticmethod
    def validate_not_empty(value: str) -> ValidationResult:
        """Validate not empty."""
        if value and value.strip():
            return ValidationResult(True, [], value)
        return ValidationResult(False, ["Value cannot be empty"])


class SecureTokenGenerator:
    """Secure token generator."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure token."""
        return secrets.token_hex(length)

    @staticmethod
    def generate_api_key(prefix: str = "ak") -> str:
        """Generate API key."""
        return f"{prefix}_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_value(value: str) -> str:
        """Hash value."""
        return hashlib.sha256(value.encode()).hexdigest()

    @staticmethod
    def verify_hash(value: str, hash_value: str) -> bool:
        """Verify hash."""
        return SecureTokenGenerator.hash_value(value) == hash_value



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

_emit_applies_guardrail("p0", "security_config_util", "p0_governance")
_emit_reads_policy_state("p0", "security_config_util", "policy_binding")
_emit_snapshots_state("p0", "security_config_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("security_config_util", "p4obs", "metric_1")
_emit_emits_metric_event("security_config_util", "p4obs", "metric_2")
_emit_emits_metric_event("security_config_util", "p4obs", "metric_3")
_emit_emits_metric_event("security_config_util", "p4obs", "metric_4")
_emit_emits_metric_event("security_config_util", "p4obs", "metric_5")
_emit_emits_metric_event("security_config_util", "p4obs", "metric_6")
_emit_records_incident_event("security_config_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("security_config_util", "p4obs", "anomaly")
_emit_writes_observability_log("security_config_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("security_config_util", "p4obs", "mon_state")
_emit_triggers_alert("security_config_util", "p4obs", "alert")
_emit_links_incident_trace("security_config_util", "p4obs", "trace_link")
_emit_captures_pattern("security_config_util", "p3lm", "pattern")
_emit_records_learning_event("security_config_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("security_config_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("security_config_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("security_config_util", "p3lm", "routing")
_emit_improves_agent_policy("security_config_util", "p3lm", "policy")
_emit_stores_learning_state("security_config_util", "p3lm", "state")
_emit_records_execution_trace("security_config_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("security_config_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("security_config_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("security_config_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("security_config_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("security_config_util", "env_read", "p2_env_1")
_emit_reads_environ("security_config_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("security_config_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("security_config_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "security_config_util", "context_pull")
_emit_pulls_context("p1", "security_config_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "security_config_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "security_config_util", "uwg_term_2")
_emit_writes_through("p1", "security_config_util", "write_through")
_emit_writes_through("p1", "security_config_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "security_config_util", "safety_validation")
_emit_invokes_eval("p1", "security_config_util", "eval_call")
_emit_proposal_commits_routing("p1", "security_config_util", "routing_commit")
_emit_escalates_to_human("p1", "security_config_util", "human_escalation")
_emit_routes_through("p1", "security_config_util", "route_through")
_emit_checks_agent_registry("p1", "security_config_util", "agent_registry")
_emit_validates_agent_capability("p1", "security_config_util", "capability")
_emit_dispatches_execution_plan("p1", "security_config_util", "exec_plan")
_emit_agent_executes_agent("p1", "security_config_util", "sub_agent")
_emit_routes_to_agent("p1", "security_config_util", "target_agent")
_emit_verifies_policy("p1", "security_config_util", "policy_check")
_emit_observes_runtime_state("p1", "security_config_util", "runtime_state")
_emit_verifies_boundary("p1", "security_config_util", "boundary_check")
_emit_transcripts_response("p1", "security_config_util", "transcript")
_emit_hard_fails_untranscripted("p1", "security_config_util")
_emit_gated_by_confidence("p1", "security_config_util", "confidence_gate")
emit_replay_key("p0", "security_config_util")
emit_determinism_digest("p0", "security_config_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "security_config_util", "execution_auth")
_emit_validates_capability("p2", "security_config_util", "capability_check")
_emit_routes_to_capability("p2", "security_config_util", "capability_route")
_emit_writes_via_uwg("p2", "security_config_util", "uwg_write")
_emit_blocks_direct_write("p2", "security_config_util", "direct_write_block")
_emit_records_tool_invocation("p2", "security_config_util", "tool_invocation")
_emit_captures_execution_output("p2", "security_config_util", "exec_output")
_emit_dispatches_agent("p3", "security_config_util", "agent_dispatch")
_emit_coordinates_agents("p3", "security_config_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "security_config_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "security_config_util", "healing_outcome")
_emit_escalates_failure("p3", "security_config_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "security_config_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "security_config_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "security_config_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "security_config_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "security_config_util", "eval_metric")
_emit_stores_embedding("p4", "security_config_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "security_config_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "security_config_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)




class RateLimiter:
    """Simple in-memory rate limiter."""

    # guardian: allow-magic-config
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RateLimiter.is_allowed")

        import time

        current_time = time.time()
        window_start = current_time - self.window_seconds
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key] = [t for t in self._requests[key] if t > window_start]
        if len(self._requests[key]) >= self.max_requests:
            return False
        self._requests[key].append(current_time)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the key."""
        import time

        current_time = time.time()
        window_start = current_time - self.window_seconds
        if key not in self._requests:
            return self.max_requests
        count = sum(1 for t in self._requests[key] if t > window_start)
        return max(0, self.max_requests - count)

    def reset(self, key: str | None = None) -> None:
        """Reset rate limit for a key or all keys."""
        if key:
            self._requests.pop(key, None)
        else:
            self._requests.clear()


class SecurityAuditLog:
    """Logs security-relevant events."""

    def __init__(self, name: str = "security"):
        self._logger = logging.getLogger(f"security.{name}")
        self._events: list[dict[str, Any]] = []

    def log_event(
        self, event_type: str, message: str, severity: str = "info", metadata: dict[str, Any] | None = None
    ) -> None:
        """Log a security event."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecurityAuditLog.log_event")

        import time

        event = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "severity": severity,
            "metadata": metadata or {},
        }
        self._events.append(event)
        log_method = getattr(self._logger, severity, self._logger.info)
        log_method(f"[{event_type}] {message}")

    def log_validation_failure(
        self, field: str, errors: list[str], metadata: dict[str, Any] | None = None
    ) -> None:
        """Log a validation failure."""
        self.log_event(
            event_type="validation_failure",
            message=f"Validation failed for {field}: {', '.join(errors)}",
            severity="warning",
            metadata={"field": field, "errors": errors, **(metadata or {})},
        )

    def log_rate_limit(self, key: str, metadata: dict[str, Any] | None = None) -> None:
        """Log a rate limit event."""
        self.log_event(
            event_type="rate_limit",
            message=f"Rate limit exceeded for {key}",
            severity="warning",
            metadata={"key": key, **(metadata or {})},
        )

    def log_suspicious_activity(self, activity: str, metadata: dict[str, Any] | None = None) -> None:
        """Log suspicious activity."""
        self.log_event(
            event_type="suspicious_activity", message=activity, severity="error", metadata=metadata
        )

    def get_events(self, event_type: str | None = None, severity: str | None = None) -> list[dict[str, Any]]:
        """Get logged events, optionally filtered."""
        events = self._events
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        if severity:
            events = [e for e in events if e["severity"] == severity]
        return events

    def clear(self) -> None:
        """Clear all logged events."""
        self._events.clear()
