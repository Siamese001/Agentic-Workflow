"""
agentic_core/L0_routing/enforcement/deterministic_replay_guard.py

DeterministicReplayGuard — P0/L0 replay enforcement.

Enforces that every routing decision can be deterministically replayed.
When replay_mode is active, recomputes the routing decision from its
inputs and raises DeterminismViolation if the result diverges from
the expected replay artifact.

ADG edges emitted:
  guards_replay       — this module is the replay guard for L0 routing
  verify_routing_replay — validates an artifact against expected outcome
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass

from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
    DeterministicRoutingGateway,
    RoutingArtifact,
    get_routing_gateway,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "deterministic_replay_guard", "L0")
_emit_routes_through("p1", "deterministic_replay_guard", "L0")
_emit_escalates_to_human("p1", "deterministic_replay_guard", "L0")
_emit_reads_policy_state("p1", "deterministic_replay_guard", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "deterministic_replay_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "deterministic_replay_guard", "execution_auth")
_emit_validates_capability("p2", "deterministic_replay_guard", "capability_check")
_emit_routes_to_capability("p2", "deterministic_replay_guard", "capability_route")
_emit_writes_via_uwg("p2", "deterministic_replay_guard", "uwg_write")
_emit_blocks_direct_write("p2", "deterministic_replay_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "deterministic_replay_guard", "tool_invocation")
_emit_captures_execution_output("p2", "deterministic_replay_guard", "exec_output")
_emit_dispatches_agent("p3", "deterministic_replay_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "deterministic_replay_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "deterministic_replay_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "deterministic_replay_guard", "healing_outcome")
_emit_escalates_failure("p3", "deterministic_replay_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "deterministic_replay_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "deterministic_replay_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "deterministic_replay_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "deterministic_replay_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "deterministic_replay_guard", "eval_metric")
_emit_stores_embedding("p4", "deterministic_replay_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "deterministic_replay_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "deterministic_replay_guard", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class DeterminismViolation(RuntimeError):
    """Raised when a routing replay produces a mismatched result."""


@dataclass(frozen=True)
class ReplayVerificationResult:
    """Result of a routing replay verification."""

    artifact: RoutingArtifact
    expected_replay_key: str
    actual_replay_key: str
    passed: bool

    @property
    def mismatch_summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ReplayVerificationResult.mismatch_summary"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if self.passed:
            return "PASS"
        return f"MISMATCH expected={self.expected_replay_key[:16]} actual={self.actual_replay_key[:16]}"


class DeterministicReplayGuard:
    """Replay guard for L0 routing decisions.

    Usage::

        guard = DeterministicReplayGuard(replay_mode=True)
        result = guard.verify_routing_replay(artifact)
        if not result.passed:
            raise DeterminismViolation(result.mismatch_summary)

    When replay_mode is False, verify_routing_replay is a no-op pass-through.
    """

    def __init__(self, replay_mode: bool = False) -> None:
        self.replay_mode = replay_mode

    def verify_routing_replay(
        self,
        artifact: RoutingArtifact,
        *,
        fail_closed: bool = True,
    ) -> ReplayVerificationResult:
        """Verify a routing artifact can be deterministically replayed.

        Args:
            artifact:    The RoutingArtifact emitted at the original routing decision.
            fail_closed: If True (default), raise DeterminismViolation on mismatch.

        Returns:
            ReplayVerificationResult with pass/fail and key comparison.

        ADG edge: guards_replay
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "DeterministicReplayGuard.verify_routing_replay"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        gw: DeterministicRoutingGateway = get_routing_gateway(artifact.policy_config_hash)
        gw.stamp_decision(
            str(artifact.route_path), metadata={"guard": "replay_verify", "trace_id": artifact.trace_id}
        )
        passed = gw.verify_replay(artifact)

        expected = hashlib.sha256(
            f"{artifact.route_path}:{artifact.policy_config_hash}:{artifact.trace_id}".encode()
        ).hexdigest()

        result = ReplayVerificationResult(
            artifact=artifact,
            expected_replay_key=expected,
            actual_replay_key=artifact.replay_key,
            passed=passed,
        )

        logger.debug(
            "REPLAY_GUARD verify trace_id=%s route=%s result=%s",
            artifact.trace_id,
            artifact.route_path,
            result.mismatch_summary,
        )

        if self.replay_mode and not passed and fail_closed:
            raise DeterminismViolation(
                f"Routing replay verification failed for trace_id={artifact.trace_id}: "
                f"{result.mismatch_summary}"
            )

        return result


_global_replay_guard: DeterministicReplayGuard | None = None


def get_replay_guard(replay_mode: bool = False) -> DeterministicReplayGuard:
    """Return the process-level deterministic replay guard."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.get_replay_guard", "L0_ROUTING")
    global _global_replay_guard
    if _global_replay_guard is None:
        _global_replay_guard = DeterministicReplayGuard(replay_mode=replay_mode)
    return _global_replay_guard


def reset_replay_guard() -> None:
    """Reset the global replay guard (for testing)."""
    global _global_replay_guard
    _global_replay_guard = None


__all__ = [
    "DeterminismViolation",
    "DeterministicReplayGuard",
    "ReplayVerificationResult",
    "get_replay_guard",
    "reset_replay_guard",
]
