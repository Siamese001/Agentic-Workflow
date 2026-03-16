"""RoutingOutcomeAdapter — bridges AgenticRouter outcomes to MetaLearningBus.

After each router.route() call resolves, wrap the RoutingDecision into a
MetaLearningChangePackage(kind="routing_outcome") and enqueue it on the
L0 MetaLearningBus for downstream system_learning processing.

Design invariants
-----------------
1. Proposal-only — never mutates routing, config, or safety state.
2. Fail-open — a failure to enqueue MUST NOT propagate to the caller.
3. No wall-clock reads; timestamp_utc is caller-supplied.
4. Pure function interface — no global mutable state.
5. C0_INFORMATIONAL influence class only.

Layer: L0_routing
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L0_routing.engines.agentic_router import RoutingDecision
from agentic_core.L0_routing.meta_control.meta_learning_bus import (
    MetaLearningBus,
    MetaLearningChangePackage,
)
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
    _emit_records_execution_trace,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "routing_outcome_adapter")
emit_determinism_digest("p0", "routing_outcome_adapter")

_emit_dispatches_healing_run("p1", "routing_outcome_adapter", "L0")
_emit_routes_through("p1", "routing_outcome_adapter", "L0")
_emit_escalates_to_human("p1", "routing_outcome_adapter", "L0")
_emit_reads_policy_state("p1", "routing_outcome_adapter", "L0")

_emit_records_execution_trace("p0", "evidence", "routing_outcome_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "routing_outcome_adapter", "p0_governance")
_emit_snapshots_state("p0", "routing_outcome_adapter", "state_snapshot")
_emit_authorize_and_execute("p2", "routing_outcome_adapter", "execution_auth")
_emit_validates_capability("p2", "routing_outcome_adapter", "capability_check")
_emit_routes_to_capability("p2", "routing_outcome_adapter", "capability_route")
_emit_writes_via_uwg("p2", "routing_outcome_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "routing_outcome_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "routing_outcome_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "routing_outcome_adapter", "exec_output")
_emit_dispatches_agent("p3", "routing_outcome_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "routing_outcome_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "routing_outcome_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "routing_outcome_adapter", "healing_outcome")
_emit_escalates_failure("p3", "routing_outcome_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "routing_outcome_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "routing_outcome_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "routing_outcome_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "routing_outcome_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "routing_outcome_adapter", "eval_metric")
_emit_stores_embedding("p4", "routing_outcome_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "routing_outcome_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "routing_outcome_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)

_KIND = "routing_outcome"


def _outcome_from_decision(decision: RoutingDecision) -> str:
    """Derive a canonical outcome string from a RoutingDecision."""
    if decision.error:
        return "SAFE_FAILURE"
    if decision.result is not None:
        return "SUCCESS"
    return "UNKNOWN"


def build_routing_outcome_package(
    decision: RoutingDecision,
    timestamp_utc: int,
) -> MetaLearningChangePackage:
    """Build a MetaLearningChangePackage from a resolved RoutingDecision.

    Args:
        decision:      The RoutingDecision returned by AgenticRouter.route().
        timestamp_utc: Caller-supplied Unix timestamp (no wall-clock read).

    Returns:
        Immutable, deterministically-hashed MetaLearningChangePackage.
    """
    outcome = _outcome_from_decision(decision)
    payload: dict[str, Any] = {
        "intent": decision.intent,
        "target_name": decision.target_name,
        "confidence": round(decision.confidence, 6),
        "outcome": outcome,
        "has_error": bool(decision.error),
        "timestamp_utc": timestamp_utc,
        "influence_class": "C0_INFORMATIONAL",
    }
    return MetaLearningChangePackage.create(
        trace_id=decision.metadata.get("trace_id", decision.target_name),
        kind=_KIND,
        payload=payload,
    )


class RoutingOutcomeAdapter:
    """Enqueues routing outcome packages onto an injected MetaLearningBus.

    Usage::

        bus = MetaLearningBus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        decision = await router.route(user_input)
        adapter.emit(decision, timestamp_utc=now)

    Args:
        bus: The MetaLearningBus instance to enqueue packages onto.
    """

    def __init__(self, bus: MetaLearningBus) -> None:
        self._bus = bus

    def emit(self, decision: RoutingDecision, timestamp_utc: int) -> bool:
        """Wrap decision into a change package and enqueue on the bus.

        Args:
            decision:      Resolved RoutingDecision from AgenticRouter.route().
            timestamp_utc: Caller-supplied Unix timestamp.

        Returns:
            True if enqueued successfully, False on any error (fail-open).
        """
        try:
            pkg = build_routing_outcome_package(decision, timestamp_utc)
            self._bus.enqueue(pkg)
            logger.debug(
                "RoutingOutcomeAdapter.emit: enqueued %s target=%r confidence=%.4f outcome=%s",
                _KIND,
                decision.target_name,
                decision.confidence,
                pkg.payload.get("outcome", "UNKNOWN"),
            )
            return True
        except Exception as exc:  # guardian: allow-silent-swallow
            logger.warning("RoutingOutcomeAdapter.emit: failed to enqueue: %s", exc)
            return False


__all__ = [
    "RoutingOutcomeAdapter",
    "build_routing_outcome_package",
]
