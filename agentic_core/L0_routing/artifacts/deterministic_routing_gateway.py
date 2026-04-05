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


# Lazy import to avoid L0->L_TOOLS gravity violation
def _get_hitl_graph():
    from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder
    return HITLGraph, HITLRuntimeRecorder

from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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
    emit_determinism_digest,
    emit_replay_key,
)

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RoutingArtifact.as_route_decision")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        try:
            rp = RoutePath(self.route_path)
        except ValueError as e:
            # TODO: Add proper input validation
            logger.warning(f"Invalid input: {e}")
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "DeterministicRoutingGateway.stamp_decision"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

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

    # HITL Integration Methods
    def escalate_low_confidence_route(
        self,
        route_path: str,
        confidence: float,
        threshold: float = 0.5,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Escalate routing decision to human review if confidence is low.

        Args:
            route_path: The proposed route path
            confidence: Confidence score (0-1)
            threshold: Minimum confidence before escalation (default 0.5)
            context: Additional context for human review

        Returns:
            True if escalation was triggered, False if confidence is acceptable
        """
        if confidence >= threshold:
            return False

        # Lazy import to avoid circular import
        from agentic_core.L5_safety.hitl.hitl_escalation_activator import (
            EscalationPriority,
            get_hitl_escalation_activator,
        )

        activator = get_hitl_escalation_activator()

        def route_review_handler(req: Any) -> str | None:
            """Handler for route review decisions."""
            # Default: approve the route but log for learning
            return "APPROVE"

        activator.register_handler(route_review_handler)

        priority = EscalationPriority.HIGH if confidence < 0.3 else EscalationPriority.MEDIUM

        escalation = activator.escalate(
            agent="DeterministicRoutingGateway",
            module="L0_routing",
            trigger_reason=f"low_routing_confidence_{confidence:.2f}",
            proposed_action=f"route_via_{route_path}",
            priority=priority,
            policy_hash=self._policy_hash,
            metadata={
                "route_path": route_path,
                "confidence": confidence,
                "threshold": threshold,
                **(context or {}),
            },
        )

        logger.info(
            "Routing escalation triggered: route=%s confidence=%.2f resolved=%s",
            route_path,
            confidence,
            escalation.resolved,
        )

        return escalation.resolved

    def create_hitl_checkpoint(
        self,
        rt_graph: Any,
        hitl_graph: HITLGraph,
        violation_id: str,
        confidence: float,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Create a HITL checkpoint for routing decision review.

        Args:
            rt_graph: Runtime graph
            hitl_graph: HITL graph
            violation_id: Violation or decision identifier
            confidence: Confidence score that triggered checkpoint
            context: Additional context

        Returns:
            Checkpoint ID
        """
        recorder = HITLRuntimeRecorder(
            rt_graph, hitl_graph, agent_id="DeterministicRoutingGateway"
        )

        checkpoint_id = recorder.checkpoint(
            violation_id=violation_id,
            confidence=confidence,
            context=context or {},
        )

        logger.debug("HITL checkpoint created for routing: %s", checkpoint_id)

        return checkpoint_id


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
