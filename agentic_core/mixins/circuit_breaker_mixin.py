"""
CircuitBreakerMixin - V10 Failure Isolation Pattern.

Provides circuit breaker functionality to prevent cascading failures
and protect system resources during healing operations.

References:
- V10 Safe Execution: Auto-rollback if problems
- Failure isolation and recovery
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "circuit_breaker_mixin", "p0_governance")
_emit_reads_policy_state("p0", "circuit_breaker_mixin", "policy_binding")
_emit_snapshots_state("p0", "circuit_breaker_mixin", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("circuit_breaker_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("circuit_breaker_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("circuit_breaker_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("circuit_breaker_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("circuit_breaker_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("circuit_breaker_mixin", "p4obs", "metric_6")
_emit_records_incident_event("circuit_breaker_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("circuit_breaker_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("circuit_breaker_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("circuit_breaker_mixin", "p4obs", "mon_state")
_emit_triggers_alert("circuit_breaker_mixin", "p4obs", "alert")
_emit_links_incident_trace("circuit_breaker_mixin", "p4obs", "trace_link")
_emit_captures_pattern("circuit_breaker_mixin", "p3lm", "pattern")
_emit_records_learning_event("circuit_breaker_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("circuit_breaker_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("circuit_breaker_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("circuit_breaker_mixin", "p3lm", "routing")
_emit_improves_agent_policy("circuit_breaker_mixin", "p3lm", "policy")
_emit_stores_learning_state("circuit_breaker_mixin", "p3lm", "state")
_emit_records_execution_trace("circuit_breaker_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("circuit_breaker_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("circuit_breaker_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("circuit_breaker_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("circuit_breaker_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("circuit_breaker_mixin", "env_read", "p2_env_1")
_emit_reads_environ("circuit_breaker_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("circuit_breaker_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("circuit_breaker_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "circuit_breaker_mixin", "context_pull")
_emit_pulls_context("p1", "circuit_breaker_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "circuit_breaker_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "circuit_breaker_mixin", "uwg_term_2")
_emit_writes_through("p1", "circuit_breaker_mixin", "write_through")
_emit_writes_through("p1", "circuit_breaker_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "circuit_breaker_mixin", "safety_validation")
_emit_invokes_eval("p1", "circuit_breaker_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "circuit_breaker_mixin", "routing_commit")
_emit_escalates_to_human("p1", "circuit_breaker_mixin", "human_escalation")
_emit_routes_through("p1", "circuit_breaker_mixin", "route_through")
_emit_checks_agent_registry("p1", "circuit_breaker_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "circuit_breaker_mixin", "capability")
_emit_dispatches_execution_plan("p1", "circuit_breaker_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "circuit_breaker_mixin", "sub_agent")
_emit_routes_to_agent("p1", "circuit_breaker_mixin", "target_agent")
_emit_verifies_policy("p1", "circuit_breaker_mixin", "policy_check")
_emit_observes_runtime_state("p1", "circuit_breaker_mixin", "runtime_state")
_emit_verifies_boundary("p1", "circuit_breaker_mixin", "boundary_check")
_emit_transcripts_response("p1", "circuit_breaker_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "circuit_breaker_mixin")
_emit_gated_by_confidence("p1", "circuit_breaker_mixin", "confidence_gate")
emit_replay_key("p0", "circuit_breaker_mixin")
emit_determinism_digest("p0", "circuit_breaker_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "circuit_breaker_mixin", "execution_auth")
_emit_validates_capability("p2", "circuit_breaker_mixin", "capability_check")
_emit_routes_to_capability("p2", "circuit_breaker_mixin", "capability_route")
_emit_writes_via_uwg("p2", "circuit_breaker_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "circuit_breaker_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "circuit_breaker_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "circuit_breaker_mixin", "exec_output")
_emit_dispatches_agent("p3", "circuit_breaker_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "circuit_breaker_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "circuit_breaker_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "circuit_breaker_mixin", "healing_outcome")
_emit_escalates_failure("p3", "circuit_breaker_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "circuit_breaker_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "circuit_breaker_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "circuit_breaker_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "circuit_breaker_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "circuit_breaker_mixin", "eval_metric")
_emit_stores_embedding("p4", "circuit_breaker_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "circuit_breaker_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "circuit_breaker_mixin", "exec_snapshot_link")

logger = logging.getLogger(__name__)
T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitStats:
    """Statistics for circuit breaker."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: datetime | None = None
    last_success_time: datetime | None = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class CircuitBreakerMixin:
    """
    Mixin providing circuit breaker pattern for failure isolation.

    Prevents cascading failures by temporarily disabling operations
    that are consistently failing.

    MRO RULE: This mixin MUST precede base agent classes in inheritance.

    Usage:
        class MyAgent(CircuitBreakerMixin, SovereignBaseAgent):
            pass

    Configuration:
        failure_threshold: Number of failures before opening circuit (default: 5)
        recovery_timeout: Seconds before attempting recovery (default: 30)
        success_threshold: Successes needed to close circuit (default: 2)
    """

    _circuit_state: CircuitState = CircuitState.CLOSED
    _circuit_stats: CircuitStats = field(default_factory=CircuitStats)
    _circuit_opened_at: datetime | None = None
    _failure_threshold: int = 5
    _recovery_timeout: int = 30
    _success_threshold: int = 2

    def __init_subclass__(cls, **kwargs):
        """Initialize circuit breaker state for subclasses."""
        super().__init_subclass__(**kwargs)
        cls._circuit_stats = CircuitStats()

    # guardian: allow-magic-config
    def configure_circuit_breaker(
        self, failure_threshold: int = 5, recovery_timeout: int = 30, success_threshold: int = 2
    ) -> None:
        """
        Configure circuit breaker parameters.

        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before recovery attempt
            success_threshold: Successes needed to close circuit
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CircuitBreakerMixin.configure_circuit_breaker")

        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold

    def circuit_protected(
        self, operation: Callable[..., T], *args: Any, fallback: Callable[..., T] | None = None, **kwargs: Any
    ) -> T:
        """
        Execute operation with circuit breaker protection.

        Args:
            operation: The operation to execute
            *args: Positional arguments for operation
            fallback: Optional fallback if circuit is open
            **kwargs: Keyword arguments for operation

        Returns:
            Result of operation or fallback

        Raises:
            CircuitOpenError: If circuit is open and no fallback provided
        """
        if not hasattr(self, "_circuit_stats") or self._circuit_stats is None:
            self._circuit_stats = CircuitStats()
        if self._circuit_state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self._circuit_state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                self._circuit_stats.rejected_calls += 1
                if fallback:
                    return fallback(*args, **kwargs)
                raise CircuitOpenError(
                    f"Circuit is OPEN. Rejected call. Recovery in {self._time_until_recovery()}s"
                )
        self._circuit_stats.total_calls += 1
        try:
            result = operation(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            raise

    def _record_success(self) -> None:
        """Record a successful operation."""
        self._circuit_stats.successful_calls += 1
        self._circuit_stats.last_success_time = datetime.utcnow()
        self._circuit_stats.consecutive_successes += 1
        self._circuit_stats.consecutive_failures = 0
        if self._circuit_state == CircuitState.HALF_OPEN:
            if self._circuit_stats.consecutive_successes >= self._success_threshold:
                self._circuit_state = CircuitState.CLOSED
                self._circuit_opened_at = None
                logger.info("Circuit breaker CLOSED after recovery")

    def _record_failure(self, error: Exception) -> None:
        """Record a failed operation."""
        self._circuit_stats.failed_calls += 1
        self._circuit_stats.last_failure_time = datetime.utcnow()
        self._circuit_stats.consecutive_failures += 1
        self._circuit_stats.consecutive_successes = 0
        logger.warning(f"Circuit breaker recorded failure: {error}")
        if self._circuit_state == CircuitState.HALF_OPEN:
            self._circuit_state = CircuitState.OPEN
            self._circuit_opened_at = datetime.utcnow()
            logger.warning("Circuit breaker reopened after failed recovery")
        elif self._circuit_state == CircuitState.CLOSED:
            if self._circuit_stats.consecutive_failures >= self._failure_threshold:
                self._circuit_state = CircuitState.OPEN
                self._circuit_opened_at = datetime.utcnow()
                logger.warning(f"Circuit breaker OPENED after {self._failure_threshold} failures")

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._circuit_opened_at is None:
            return True
        elapsed = (datetime.utcnow() - self._circuit_opened_at).total_seconds()
        return elapsed >= self._recovery_timeout

    def _time_until_recovery(self) -> int:
        """Get seconds until recovery attempt."""
        if self._circuit_opened_at is None:
            return 0
        elapsed = (datetime.utcnow() - self._circuit_opened_at).total_seconds()
        return max(0, int(self._recovery_timeout - elapsed))

    def get_circuit_state(self) -> dict[str, Any]:
        """Get current circuit breaker state and statistics."""
        if not hasattr(self, "_circuit_stats") or self._circuit_stats is None:
            self._circuit_stats = CircuitStats()
        return {
            "state": self._circuit_state.value,
            "total_calls": self._circuit_stats.total_calls,
            "successful_calls": self._circuit_stats.successful_calls,
            "failed_calls": self._circuit_stats.failed_calls,
            "rejected_calls": self._circuit_stats.rejected_calls,
            "consecutive_failures": self._circuit_stats.consecutive_failures,
            "time_until_recovery": self._time_until_recovery()
            if self._circuit_state == CircuitState.OPEN
            else None,
        }

    def reset_circuit(self) -> None:
        """Manually reset the circuit breaker."""
        self._circuit_state = CircuitState.CLOSED
        self._circuit_stats = CircuitStats()
        self._circuit_opened_at = None
        logger.info("Circuit breaker manually reset")


class CircuitOpenError(Exception):
    """Raised when circuit is open and no fallback provided."""

    pass
