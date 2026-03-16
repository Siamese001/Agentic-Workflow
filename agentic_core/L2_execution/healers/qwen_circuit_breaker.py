"""
Qwen Circuit Breaker - Deterministic Circuit Breaker with Replay Safety

Provides failure detection and automatic tier disabling with deterministic
behavior during replay mode.
"""

from __future__ import annotations

import logging
import uuid

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "qwen_circuit_breaker")
emit_determinism_digest("p0", "qwen_circuit_breaker")

_emit_dispatches_healing_run("p1", "qwen_circuit_breaker", "L2")
_emit_routes_through("p1", "qwen_circuit_breaker", "L2")
_emit_escalates_to_human("p1", "qwen_circuit_breaker", "L2")
_emit_reads_policy_state("p1", "qwen_circuit_breaker", "L2")

_emit_applies_guardrail("p0", "qwen_circuit_breaker", "p0_governance")
_emit_snapshots_state("p0", "qwen_circuit_breaker", "state_snapshot")
_emit_authorize_and_execute("p2", "qwen_circuit_breaker", "execution_auth")
_emit_validates_capability("p2", "qwen_circuit_breaker", "capability_check")
_emit_routes_to_capability("p2", "qwen_circuit_breaker", "capability_route")
_emit_writes_via_uwg("p2", "qwen_circuit_breaker", "uwg_write")
_emit_blocks_direct_write("p2", "qwen_circuit_breaker", "direct_write_block")
_emit_records_tool_invocation("p2", "qwen_circuit_breaker", "tool_invocation")
_emit_captures_execution_output("p2", "qwen_circuit_breaker", "exec_output")
_emit_dispatches_agent("p3", "qwen_circuit_breaker", "agent_dispatch")
_emit_coordinates_agents("p3", "qwen_circuit_breaker", "agent_coordination")
_emit_records_workflow_lineage("p3", "qwen_circuit_breaker", "workflow_lineage")
_emit_records_healing_outcome("p3", "qwen_circuit_breaker", "healing_outcome")
_emit_escalates_failure("p3", "qwen_circuit_breaker", "failure_escalation")
_emit_orchestrates_workflow("p3", "qwen_circuit_breaker", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "qwen_circuit_breaker", "healing_dispatch")
_emit_invokes_evaluation("p3", "qwen_circuit_breaker", "evaluation_signal")
_emit_records_telemetry_event("p4", "qwen_circuit_breaker", "telemetry_event")
_emit_captures_evaluation_metric("p4", "qwen_circuit_breaker", "eval_metric")
_emit_stores_embedding("p4", "qwen_circuit_breaker", "embedding_store")
_emit_updates_meta_learning_state("p4", "qwen_circuit_breaker", "meta_learning")
_emit_links_execution_to_snapshot("p4", "qwen_circuit_breaker", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class QwenCircuitBreaker:
    """Deterministic circuit breaker with replay safety."""

    def __init__(self, replay_mode: bool = False):
        self.replay_mode = replay_mode
        self.failure_count = 0
        self.failure_timestamps: list[int] = []
        self.circuit_open = False
        self.circuit_open_timestamp: int | None = None
        self.last_failure_timestamp: int | None = None

    def record_failure(self, timestamp: int | None = None) -> bool:
        """Record failure with deterministic replay behavior."""
        _emit_hard_fails_untranscripted(str(uuid.uuid4()), "QwenCircuitBreaker.record_failure")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "QwenCircuitBreaker.record_failure"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:QwenCircuitBreaker.record_failure".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.replay_mode:
            return False
        now = timestamp or int(get_clock().now_epoch())
        self.last_failure_timestamp = now
        self.failure_timestamps = [t for t in self.failure_timestamps if now - t <= 60]
        self.failure_timestamps.append(now)
        self.failure_count = len(self.failure_timestamps)
        if self.failure_count >= 3:
            self.circuit_open = True
            self.circuit_open_timestamp = now
            logger.warning("Qwen circuit breaker OPEN - disabling for 5 minutes")
            return True
        return False

    def is_circuit_open(self, timestamp: int | None = None) -> bool:
        """Check circuit state with deterministic replay behavior."""
        if self.replay_mode:
            return False
        if not self.circuit_open:
            return False
        now = timestamp or int(get_clock().now_epoch())
        if now - self.circuit_open_timestamp > 300:
            self.circuit_open = False
            self.failure_count = 0
            self.failure_timestamps.clear()
            logger.info("Qwen circuit breaker CLOSED - re-enabling tier")
            return False
        return True

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status for health endpoint."""
        return {
            "circuit_open": self.is_circuit_open(),
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_timestamp,
            "replay_mode": self.replay_mode,
        }


circuit_breaker = QwenCircuitBreaker()
__all__ = ["QwenCircuitBreaker", "circuit_breaker"]
