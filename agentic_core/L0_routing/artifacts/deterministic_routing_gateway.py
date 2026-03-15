"""
agentic_core/L0_routing/artifacts/deterministic_routing_gateway.py

DeterministicRoutingGateway — P0-L0 gap remediation.

Wraps every L0 routing decision with a RoutingArtifact that carries a
determinism digest and replay key, making routing decisions reproducible
and auditable. Emits emits_determinism_digest + emits_replay_key ADG edges.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.L2_execution.providers import get_clock

logger = logging.getLogger(__name__)
_REPLAY_KEY_LOGGER = logging.getLogger("adg.emits_replay_key")
_DETERMINISM_LOGGER = logging.getLogger("adg.emits_determinism_digest")


@dataclass(frozen=True)
class RoutingArtifact:
    """Deterministic routing artifact emitted at each L0 routing decision.

    Carries the replay key and determinism digest so that every routing
    decision can be reproduced exactly and audited post-hoc.
    """

    trace_id: str
    replay_key: str
    determinism_digest: str
    route_path: str
    policy_config_hash: str
    timestamp_monotonic: float
    metadata: dict[str, Any]

    def as_route_decision(self, risk_score: float = 0.0, budget_est: float = 0.0) -> RouteDecisionArtifact:
        """Convert to the canonical RouteDecisionArtifact for downstream consumers."""
        try:
            rp = RoutePath(self.route_path)
        except ValueError:
            rp = RoutePath.STANDARD_VALIDATION
        return RouteDecisionArtifact(
            trace_id=self.trace_id,
            timestamp=str(self.timestamp_monotonic),
            route_path=rp,
            risk_score=risk_score,
            budget_est=budget_est,
            rationale_enum=RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash=self.policy_config_hash,
        )


def _compute_replay_key(route_path: str, policy_hash: str, trace_id: str) -> str:
    """Compute a deterministic replay key from routing inputs."""
    payload = f"{route_path}:{policy_hash}:{trace_id}"
    return hashlib.sha256(payload.encode()).hexdigest()


def _compute_determinism_digest(replay_key: str, timestamp: float) -> str:
    """Compute a determinism digest binding the replay key to an execution moment."""
    payload = f"{replay_key}:{timestamp:.6f}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


class DeterministicRoutingGateway:
    """Single gateway for all L0 routing decisions.

    Every routing decision must pass through ``stamp_decision`` before
    being dispatched. This ensures that:
    - A replay key is emitted (``emits_replay_key`` ADG edge).
    - A determinism digest is emitted (``emits_determinism_digest`` ADG edge).
    - The artifact is recorded in the ledger for later replay.

    Usage::

        gw = DeterministicRoutingGateway(policy_hash="abc123")
        artifact = gw.stamp_decision("standard_validation")
        # dispatch using artifact.route_path
    """

    def __init__(self, policy_hash: str = "") -> None:
        self._policy_hash = policy_hash
        self._ledger: list[RoutingArtifact] = []

    def stamp_decision(
        self,
        route_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> RoutingArtifact:
        """Stamp a routing decision with a replay key and determinism digest.

        Returns a :class:`RoutingArtifact` that must be forwarded with the
        request so downstream layers can verify routing provenance.
        """
        from agentic_core.runtime.execution_trace import get_active_execution_trace  # noqa: PLC0415

        active = get_active_execution_trace()
        trace_id = active.trace_id if active else "no-active-trace"
        clk = get_clock()
        replay_key = clk.emit_replay_key(context=f"{route_path}:{self._policy_hash}:{trace_id}")
        digest = clk.emit_determinism_digest(
            inputs={"route": route_path, "policy": self._policy_hash, "trace": trace_id}
        )
        ts = clk.now_epoch()
        artifact = RoutingArtifact(
            trace_id=trace_id,
            replay_key=replay_key,
            determinism_digest=digest,
            route_path=route_path,
            policy_config_hash=self._policy_hash,
            timestamp_monotonic=ts,
            metadata=metadata or {},
        )
        self._ledger.append(artifact)
        logger.debug(
            "ROUTING_ARTIFACT trace_id=%s route=%s replay_key=%s digest=%s",
            trace_id,
            route_path,
            replay_key[:12],
            digest[:12],
        )
        return artifact

    def verify_replay(self, artifact: RoutingArtifact) -> bool:
        """Verify a routing artifact can be deterministically replayed.

        Returns True if the replay key can be reconstructed from the
        artifact's own fields (i.e., it was not tampered with).
        """
        expected = _compute_replay_key(artifact.route_path, artifact.policy_config_hash, artifact.trace_id)
        return expected == artifact.replay_key

    def ledger(self) -> list[RoutingArtifact]:
        """Return a copy of all stamped routing artifacts."""
        return list(self._ledger)

    def clear_ledger(self) -> None:
        """Clear the ledger (for testing)."""
        self._ledger.clear()


_global_routing_gateway: DeterministicRoutingGateway | None = None


def get_routing_gateway(policy_hash: str = "") -> DeterministicRoutingGateway:
    """Return the process-level deterministic routing gateway."""
    global _global_routing_gateway
    if _global_routing_gateway is None:
        _global_routing_gateway = DeterministicRoutingGateway(policy_hash=policy_hash)
    return _global_routing_gateway


def reset_routing_gateway() -> None:
    """Reset the global routing gateway (for testing)."""
    global _global_routing_gateway
    _global_routing_gateway = None


__all__ = [
    "RoutingArtifact",
    "DeterministicRoutingGateway",
    "get_routing_gateway",
    "reset_routing_gateway",
]
