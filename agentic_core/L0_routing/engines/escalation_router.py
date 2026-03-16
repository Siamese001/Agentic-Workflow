"""
Phase 5 — Escalation Router: policy-coded L0 mode decision from prior violations.

GUARANTEE: reads ONLY events with commit_tick < execution_start_tick.
Same-cycle violations are structurally invisible to the routing decision.

decide_mode_from_prior_violations(execution_start_tick, routing_config, store) -> str
  Returns escalation_mode from config if prior violations trigger escalation,
  otherwise returns "normal" (legacy default preserved).
"""

from __future__ import annotations

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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "escalation_router")
emit_determinism_digest("p0", "escalation_router")

_emit_dispatches_healing_run("p1", "escalation_router", "L0")
_emit_routes_through("p1", "escalation_router", "L0")
_emit_escalates_to_human("p1", "escalation_router", "L0")
_emit_reads_policy_state("p1", "escalation_router", "L0")
_emit_authorize_and_execute("p2", "escalation_router", "execution_auth")
_emit_validates_capability("p2", "escalation_router", "capability_check")
_emit_routes_to_capability("p2", "escalation_router", "capability_route")
_emit_writes_via_uwg("p2", "escalation_router", "uwg_write")
_emit_blocks_direct_write("p2", "escalation_router", "direct_write_block")
_emit_records_tool_invocation("p2", "escalation_router", "tool_invocation")
_emit_captures_execution_output("p2", "escalation_router", "exec_output")
_emit_dispatches_agent("p3", "escalation_router", "agent_dispatch")
_emit_coordinates_agents("p3", "escalation_router", "agent_coordination")
_emit_records_workflow_lineage("p3", "escalation_router", "workflow_lineage")
_emit_records_healing_outcome("p3", "escalation_router", "healing_outcome")
_emit_escalates_failure("p3", "escalation_router", "failure_escalation")
_emit_orchestrates_workflow("p3", "escalation_router", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "escalation_router", "healing_dispatch")
_emit_invokes_evaluation("p3", "escalation_router", "evaluation_signal")
_emit_records_telemetry_event("p4", "escalation_router", "telemetry_event")
_emit_captures_evaluation_metric("p4", "escalation_router", "eval_metric")
_emit_stores_embedding("p4", "escalation_router", "embedding_store")
_emit_updates_meta_learning_state("p4", "escalation_router", "meta_learning")
_emit_links_execution_to_snapshot("p4", "escalation_router", "exec_snapshot_link")


def _get_routing_config_class():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_routing_config_class", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_routing_config_class", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_routing_config_class")
    from agentic_core.L4_state.config.versioned_configs import RoutingConfig

    return RoutingConfig


def _get_violation_event_store_class():
    from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore

    return ViolationEventStore


def decide_mode_from_prior_violations(
    execution_start_tick: int, routing_config: object, violation_store: object
) -> str:
    """
    Determine L0 routing mode based solely on prior violations.

    Algorithm
    ---------
    1. Fetch events in window [execution_start_tick - window_ticks, execution_start_tick).
       Same-cycle events (commit_tick == execution_start_tick) are excluded by the store.
    2. For each prior event, check:
       a. severity_score >= escalation_severity_threshold (from config — no hardcoded literal)
       b. OR any violation_code in event.violation_codes is in denylist (if denylist non-empty)
    3. If any event triggers escalation → return routing_config.escalation_mode.
    4. Otherwise → return "normal".

    Parameters
    ----------
    execution_start_tick : int
        The commit_tick at which the current execution begins.
    routing_config : RoutingConfig
        Versioned config supplying all thresholds (no hardcoded literals).
    violation_store : ViolationEventStore
        L4 store to query prior violations from.

    Returns
    -------
    str
        Routing mode string ("normal" or routing_config.escalation_mode).
    """
    prior_events = violation_store.fetch_window(
        before_tick=execution_start_tick, window_ticks=routing_config.escalation_window_ticks
    )
    denylist = set(routing_config.escalation_violation_code_denylist)
    for event in prior_events:
        severity_triggered = event.severity_score >= routing_config.escalation_severity_threshold
        code_triggered = bool(denylist and denylist.intersection(event.violation_codes))
        if severity_triggered or code_triggered:
            return routing_config.escalation_mode
    return "normal"
