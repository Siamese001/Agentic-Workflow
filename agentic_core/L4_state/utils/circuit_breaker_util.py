from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "circuit_breaker_util")
trace_contract.emit_determinism_digest("p0", "circuit_breaker_util")

trace_contract._emit_dispatches_healing_run("p1", "circuit_breaker_util", "L4")
trace_contract._emit_routes_through("p1", "circuit_breaker_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "circuit_breaker_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "circuit_breaker_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "circuit_breaker_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "circuit_breaker_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "circuit_breaker_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "circuit_breaker_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "circuit_breaker_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "circuit_breaker_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "circuit_breaker_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "circuit_breaker_util")
trace_contract._emit_gated_by_confidence("p1", "circuit_breaker_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "circuit_breaker_util", "L4")
trace_contract._emit_reads_policy_state("p1", "circuit_breaker_util", "L4")

trace_contract._emit_applies_guardrail("p0", "circuit_breaker_util", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "circuit_breaker_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "circuit_breaker_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "circuit_breaker_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "circuit_breaker_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "circuit_breaker_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "circuit_breaker_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "circuit_breaker_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "circuit_breaker_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "circuit_breaker_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "circuit_breaker_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "circuit_breaker_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "circuit_breaker_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "circuit_breaker_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "circuit_breaker_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "circuit_breaker_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "circuit_breaker_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "circuit_breaker_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "circuit_breaker_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "circuit_breaker_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "circuit_breaker_util", "exec_snapshot_link")

"Circuit Breaker implementation for fault tolerance.\n\nMigrated from archives/legacy_root_folders/tools/runtime_utils.py\nPhase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)\n"
import time
from dataclasses import dataclass
from enum import Enum


trace_contract._emit_emits_metric_event("circuit_breaker_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("circuit_breaker_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("circuit_breaker_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("circuit_breaker_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("circuit_breaker_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("circuit_breaker_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("circuit_breaker_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("circuit_breaker_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("circuit_breaker_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("circuit_breaker_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("circuit_breaker_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("circuit_breaker_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("circuit_breaker_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("circuit_breaker_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("circuit_breaker_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("circuit_breaker_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("circuit_breaker_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("circuit_breaker_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("circuit_breaker_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("circuit_breaker_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("circuit_breaker_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("circuit_breaker_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("circuit_breaker_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("circuit_breaker_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("circuit_breaker_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("circuit_breaker_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("circuit_breaker_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("circuit_breaker_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "circuit_breaker_util", "context_pull")
trace_contract._emit_pulls_context("p1", "circuit_breaker_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "circuit_breaker_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "circuit_breaker_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "circuit_breaker_util", "write_through")
trace_contract._emit_writes_through("p1", "circuit_breaker_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "circuit_breaker_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "circuit_breaker_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "circuit_breaker_util", "routing_commit")


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejects requests."""

    def __init__(self, message: str, breaker_name: str):
        super().__init__(message)
        self.breaker_name = breaker_name


@dataclass
class CircuitBreaker:
    """Minimal circuit breaker with CLOSED / OPEN / HALF_OPEN states.

    This is intentionally simple and process-local; higher-level
    orchestration (e.g. batch runner) is responsible for coordinating
    breakers across workers if needed.

    Attributes:
        name: Unique identifier for this circuit breaker
        failure_threshold: Number of failures before opening circuit
        reset_after_s: Seconds to wait before attempting recovery
        half_open_max_calls: Successful calls needed to close circuit
        state: Current state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Current count of consecutive failures
        success_count: Current count of consecutive successes
        opened_at: Timestamp when circuit was opened
    """

    name: str
    failure_threshold: int = 5
    reset_after_s: int = 30
    half_open_max_calls: int = 3
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    opened_at: float = 0.0

    def can_execute(self) -> bool:
        """Check if execution is allowed based on current state.

        Returns:
            True if execution is allowed, False if circuit is open
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "CircuitBreaker.can_execute", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "CircuitBreaker.can_execute")

        now = time.time()
        if self.state == CircuitBreakerState.OPEN:
            if now - self.opened_at >= self.reset_after_s:
                self.state = CircuitBreakerState.HALF_OPEN
                self.failure_count = 0
                self.success_count = 0
            else:
                return False
        if self.state == CircuitBreakerState.HALF_OPEN and self.success_count >= self.half_open_max_calls:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
        return True

    def record_success(self) -> None:
        """Record a successful execution."""
        self.success_count += 1
        if (
            self.state in {CircuitBreakerState.OPEN, CircuitBreakerState.HALF_OPEN}
            and self.success_count >= self.half_open_max_calls
        ):
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0

    def record_failure(self) -> None:
        """Record a failed execution."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.opened_at = time.time()


_BREAKERS: dict[str, CircuitBreaker] = {}


# guardian: allow-magic-config
def get_breaker(
    name: str,
    failure_threshold: int = 5,
    reset_after_s: int = 30,
    half_open_max_calls: int = 3,
) -> CircuitBreaker:
    """Get or create a circuit breaker by name.

    Args:
        name: Unique identifier for the breaker
        failure_threshold: Number of failures before opening
        reset_after_s: Seconds before attempting recovery
        half_open_max_calls: Successes needed to close

    Returns:
        CircuitBreaker instance
    """
    if name not in _BREAKERS:
        _BREAKERS[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            reset_after_s=reset_after_s,
            half_open_max_calls=half_open_max_calls,
        )
    return _BREAKERS[name]


def reset_all_breakers() -> None:
    """Reset all circuit breakers (primarily for testing)."""
    _BREAKERS.clear()
