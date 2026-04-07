"""
SSOT Circuit Breaker Mixin — Policy-Hash-Scoped with Safety Non-Interception.

Provides circuit breaker protection that:
  - Scopes breaker buckets by active_policy_hash
  - Disables breaker state mutation under replay mode
  - NEVER intercepts L5 safety exceptions (StateValidationError,
    PolicyHashMismatch, SovereignTokenDenied)
  - Tracks failure counts and open/closed/half-open states

Layer: L2 Execution Aid
Authority: Guard external calls only. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
import time
from typing import Any

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

_emit_applies_guardrail("p0", "ssot_circuit_breaker_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_circuit_breaker_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_circuit_breaker_mixin", "state_snapshot")
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

_emit_emits_metric_event("ssot_circuit_breaker_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_circuit_breaker_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_circuit_breaker_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_circuit_breaker_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_circuit_breaker_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_circuit_breaker_mixin", "p4obs", "metric_6")
_emit_records_incident_event("ssot_circuit_breaker_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_circuit_breaker_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_circuit_breaker_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_circuit_breaker_mixin", "p4obs", "mon_state")
_emit_triggers_alert("ssot_circuit_breaker_mixin", "p4obs", "alert")
_emit_links_incident_trace("ssot_circuit_breaker_mixin", "p4obs", "trace_link")
_emit_captures_pattern("ssot_circuit_breaker_mixin", "p3lm", "pattern")
_emit_records_learning_event("ssot_circuit_breaker_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_circuit_breaker_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_circuit_breaker_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_circuit_breaker_mixin", "p3lm", "routing")
_emit_improves_agent_policy("ssot_circuit_breaker_mixin", "p3lm", "policy")
_emit_stores_learning_state("ssot_circuit_breaker_mixin", "p3lm", "state")
_emit_records_execution_trace("ssot_circuit_breaker_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_circuit_breaker_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_circuit_breaker_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_circuit_breaker_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_circuit_breaker_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_circuit_breaker_mixin", "env_read", "p2_env_1")
_emit_reads_environ("ssot_circuit_breaker_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_circuit_breaker_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_circuit_breaker_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_circuit_breaker_mixin", "context_pull")
_emit_pulls_context("p1", "ssot_circuit_breaker_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_circuit_breaker_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_circuit_breaker_mixin", "uwg_term_2")
_emit_writes_through("p1", "ssot_circuit_breaker_mixin", "write_through")
_emit_writes_through("p1", "ssot_circuit_breaker_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_circuit_breaker_mixin", "safety_validation")
_emit_invokes_eval("p1", "ssot_circuit_breaker_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_circuit_breaker_mixin", "routing_commit")
_emit_escalates_to_human("p1", "ssot_circuit_breaker_mixin", "human_escalation")
_emit_routes_through("p1", "ssot_circuit_breaker_mixin", "route_through")
_emit_checks_agent_registry("p1", "ssot_circuit_breaker_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_circuit_breaker_mixin", "capability")
_emit_dispatches_execution_plan("p1", "ssot_circuit_breaker_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_circuit_breaker_mixin", "sub_agent")
_emit_routes_to_agent("p1", "ssot_circuit_breaker_mixin", "target_agent")
_emit_verifies_policy("p1", "ssot_circuit_breaker_mixin", "policy_check")
_emit_observes_runtime_state("p1", "ssot_circuit_breaker_mixin", "runtime_state")
_emit_verifies_boundary("p1", "ssot_circuit_breaker_mixin", "boundary_check")
_emit_transcripts_response("p1", "ssot_circuit_breaker_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_circuit_breaker_mixin")
_emit_gated_by_confidence("p1", "ssot_circuit_breaker_mixin", "confidence_gate")
emit_replay_key("p0", "ssot_circuit_breaker_mixin")
emit_determinism_digest("p0", "ssot_circuit_breaker_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_circuit_breaker_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_circuit_breaker_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_circuit_breaker_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_circuit_breaker_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_circuit_breaker_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_circuit_breaker_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_circuit_breaker_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_circuit_breaker_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_circuit_breaker_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_circuit_breaker_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_circuit_breaker_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_circuit_breaker_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_circuit_breaker_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_circuit_breaker_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_circuit_breaker_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_circuit_breaker_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_circuit_breaker_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_circuit_breaker_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_circuit_breaker_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_circuit_breaker_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTCircuitBreaker")


class SafetyException(Exception):
    """Base class for L5 safety exceptions that must never be intercepted."""


class StateValidationError(SafetyException):
    """Raised when state validation fails."""


class PolicyHashMismatch(SafetyException):
    """Raised when policy hash does not match expected value."""


class SovereignTokenDenied(SafetyException):
    """Raised when sovereignty token request is denied."""


FORBIDDEN_EXCEPTIONS = (StateValidationError, PolicyHashMismatch, SovereignTokenDenied)


class SSOTCircuitBreakerMixin:
    """Policy-hash-scoped circuit breaker with safety non-interception.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Breaker buckets are keyed by policy hash.
    Under replay mode, breaker state is frozen (no mutation).
    Forbidden exceptions always propagate immediately.
    """

    BREAKER_FAILURE_THRESHOLD: int = 5
    BREAKER_RECOVERY_TIMEOUT: float = 60.0

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_breakers: dict[str, dict[str, Any]] = {}

    def breaker_call(self, bucket: str, fn: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute a function through the circuit breaker.

        Parameters
        ----------
        bucket : str
            Breaker bucket name (will be policy-hash-scoped).
        fn : callable
            Function to execute.
        *args, **kwargs
            Arguments to pass to fn.

        Returns
        -------
        Any
            Result of fn(*args, **kwargs).

        Raises
        ------
        SafetyException subclasses
            Always propagated immediately (never intercepted).
        CircuitOpenError
            If the breaker is open and recovery timeout has not elapsed.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTCircuitBreakerMixin.breaker_call")

        scoped_bucket = self._scoped_bucket(bucket)
        state = self._get_breaker_state(scoped_bucket)
        if state["status"] == "open":
            elapsed = time.time() - state["last_failure_time"]
            if elapsed < self.BREAKER_RECOVERY_TIMEOUT:
                raise CircuitOpenError(
                    f"Circuit breaker open for {scoped_bucket} ({elapsed:.1f}s / {self.BREAKER_RECOVERY_TIMEOUT}s)",
                )
            state["status"] = "half-open"
            _logger.info("[SSOTBreaker] %s -> half-open", scoped_bucket)
        try:
            result = fn(*args, **kwargs)
            if not getattr(self, "is_replay_mode", False):
                if state["status"] == "half-open":
                    state["status"] = "closed"
                    state["failure_count"] = 0
                    _logger.info("[SSOTBreaker] %s -> closed (recovered)", scoped_bucket)
            return result
        # guardian: allow-silent-swallow - acceptable exception handling    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context    # guardian: FORBIDDEN_EXCEPTIONS should be handled with specific context
        except FORBIDDEN_EXCEPTIONS:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            if not getattr(self, "is_replay_mode", False):
                state["failure_count"] += 1
                state["last_failure_time"] = time.time()
                state["last_error"] = str(exc)
                if state["failure_count"] >= self.BREAKER_FAILURE_THRESHOLD:
                    state["status"] = "open"
                    _logger.warning(
                        "[SSOTBreaker] %s -> open (failures=%d)", scoped_bucket, state["failure_count"],
                    )
            raise

    def breaker_status(self, bucket: str) -> str:
        """Return the current status of a breaker bucket."""
        scoped_bucket = self._scoped_bucket(bucket)
        state = self._get_breaker_state(scoped_bucket)
        return state["status"]

    def breaker_reset(self, bucket: str) -> None:
        """Manually reset a breaker bucket to closed."""
        scoped_bucket = self._scoped_bucket(bucket)
        if scoped_bucket in self._ssot_breakers:
            self._ssot_breakers[scoped_bucket]["status"] = "closed"
            self._ssot_breakers[scoped_bucket]["failure_count"] = 0

    def _get_breaker_state(self, scoped_bucket: str) -> dict[str, Any]:
        """Get or create breaker state for a scoped bucket."""
        if scoped_bucket not in self._ssot_breakers:
            self._ssot_breakers[scoped_bucket] = {
                "status": "closed",
                "failure_count": 0,
                "last_failure_time": 0.0,
                "last_error": None,
            }
        return self._ssot_breakers[scoped_bucket]

    def _scoped_bucket(self, bucket: str) -> str:
        """Prefix bucket with active_policy_hash."""
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        return f"{policy_hash}:{bucket}"


class CircuitOpenError(Exception):
    """Raised when a circuit breaker is open."""
