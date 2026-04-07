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

from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import (
    DeterministicRoutingGateway,
    RoutingArtifact,
    get_routing_gateway,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

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
            _trace_id, LayerSegment.L0_ROUTING, "ReplayVerificationResult.mismatch_summary",
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
            _trace_id, LayerSegment.L0_ROUTING, "DeterministicReplayGuard.verify_routing_replay",
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        gw: DeterministicRoutingGateway = get_routing_gateway(artifact.policy_config_hash)
        gw.stamp_decision(
            str(artifact.route_path), metadata={"guard": "replay_verify", "trace_id": artifact.trace_id},
        )
        passed = gw.verify_replay(artifact)

        expected = hashlib.sha256(
            f"{artifact.route_path}:{artifact.policy_config_hash}:{artifact.trace_id}".encode(),
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
                f"{result.mismatch_summary}",
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
