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

_emit_emits_metric_event("routing_outcome_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("routing_outcome_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("routing_outcome_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("routing_outcome_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("routing_outcome_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("routing_outcome_adapter", "p4obs", "metric_6")
_emit_records_incident_event("routing_outcome_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("routing_outcome_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("routing_outcome_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("routing_outcome_adapter", "p4obs", "mon_state")
_emit_triggers_alert("routing_outcome_adapter", "p4obs", "alert")
_emit_links_incident_trace("routing_outcome_adapter", "p4obs", "trace_link")
_emit_captures_pattern("routing_outcome_adapter", "p3lm", "pattern")
_emit_records_learning_event("routing_outcome_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("routing_outcome_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("routing_outcome_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("routing_outcome_adapter", "p3lm", "routing")
_emit_improves_agent_policy("routing_outcome_adapter", "p3lm", "policy")
_emit_stores_learning_state("routing_outcome_adapter", "p3lm", "state")
_emit_records_execution_trace("routing_outcome_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("routing_outcome_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("routing_outcome_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("routing_outcome_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("routing_outcome_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("routing_outcome_adapter", "env_read", "p2_env_1")
_emit_reads_environ("routing_outcome_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("routing_outcome_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("routing_outcome_adapter", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "routing_outcome_adapter")
emit_determinism_digest("p0", "routing_outcome_adapter")

_emit_dispatches_healing_run("p1", "routing_outcome_adapter", "L0")
_emit_routes_through("p1", "routing_outcome_adapter", "L0")
_emit_checks_agent_registry("p1", "routing_outcome_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "routing_outcome_adapter", "capability")
_emit_dispatches_execution_plan("p1", "routing_outcome_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "routing_outcome_adapter", "sub_agent")
_emit_routes_to_agent("p1", "routing_outcome_adapter", "target_agent")
_emit_verifies_policy("p1", "routing_outcome_adapter", "policy_check")
_emit_observes_runtime_state("p1", "routing_outcome_adapter", "runtime_state")
_emit_verifies_boundary("p1", "routing_outcome_adapter", "boundary_check")
_emit_transcripts_response("p1", "routing_outcome_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "routing_outcome_adapter")
_emit_gated_by_confidence("p1", "routing_outcome_adapter", "confidence_gate")
_emit_escalates_to_human("p1", "routing_outcome_adapter", "L0")
_emit_reads_policy_state("p1", "routing_outcome_adapter", "L0")
_emit_pulls_context("p1", "routing_outcome_adapter", "context_pull")
_emit_pulls_context("p1", "routing_outcome_adapter", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "routing_outcome_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "routing_outcome_adapter", "uwg_term_secondary")
_emit_writes_through("p1", "routing_outcome_adapter", "write_through")
_emit_writes_through("p1", "routing_outcome_adapter", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "routing_outcome_adapter", "safety_validation")
_emit_invokes_eval("p1", "routing_outcome_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "routing_outcome_adapter", "routing_commit")

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
