from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "circuit_breaker_util")
emit_determinism_digest("p0", "circuit_breaker_util")

_emit_dispatches_healing_run("p1", "circuit_breaker_util", "L4")
_emit_routes_through("p1", "circuit_breaker_util", "L4")
_emit_escalates_to_human("p1", "circuit_breaker_util", "L4")
_emit_reads_policy_state("p1", "circuit_breaker_util", "L4")

_emit_applies_guardrail("p0", "circuit_breaker_util", "p0_governance")
_emit_authorize_and_execute("p2", "circuit_breaker_util", "execution_auth")
_emit_validates_capability("p2", "circuit_breaker_util", "capability_check")
_emit_routes_to_capability("p2", "circuit_breaker_util", "capability_route")
_emit_writes_via_uwg("p2", "circuit_breaker_util", "uwg_write")
_emit_blocks_direct_write("p2", "circuit_breaker_util", "direct_write_block")
_emit_records_tool_invocation("p2", "circuit_breaker_util", "tool_invocation")
_emit_captures_execution_output("p2", "circuit_breaker_util", "exec_output")
_emit_dispatches_agent("p3", "circuit_breaker_util", "agent_dispatch")
_emit_coordinates_agents("p3", "circuit_breaker_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "circuit_breaker_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "circuit_breaker_util", "healing_outcome")
_emit_escalates_failure("p3", "circuit_breaker_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "circuit_breaker_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "circuit_breaker_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "circuit_breaker_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "circuit_breaker_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "circuit_breaker_util", "eval_metric")
_emit_stores_embedding("p4", "circuit_breaker_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "circuit_breaker_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "circuit_breaker_util", "exec_snapshot_link")

"Circuit Breaker implementation for fault tolerance.\n\nMigrated from archives/legacy_root_folders/tools/runtime_utils.py\nPhase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)\n"
import time
from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


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

        _emit_snapshots_state(str(_uuid.uuid4()), "CircuitBreaker.can_execute", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "CircuitBreaker.can_execute")

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
    name: str, failure_threshold: int = 5, reset_after_s: int = 30, half_open_max_calls: int = 3
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
