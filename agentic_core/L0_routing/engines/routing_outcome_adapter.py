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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "routing_outcome_adapter")
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
        except (ValueError, TypeError, RuntimeError) as exc:  # guardian: allow-silent-swallow
            logger.warning("RoutingOutcomeAdapter.emit: failed to enqueue: %s", exc)
            return False


__all__ = [
    "RoutingOutcomeAdapter",
    "build_routing_outcome_package",
]
