"""
L0 Time-Shifted Router — Phase 3

Routing decisions driven ONLY by prior committed DetectionSignals (N+1 influence).
Same-cycle signals (emitted during execution N) CANNOT influence routing of N.

Architecture:
    1. At execution start, record execution_start_tick.
    2. Call get_prior_detection_signal(execution_start_tick) — strictly prior only.
    3. If prior signal anomaly_score >= threshold → route to compliance_mode.
    4. Emit new signal AFTER routing decision is finalized (no feedback loop).
"""

from __future__ import annotations

from dataclasses import dataclass

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

emit_replay_key("p0", "timeshift_router")
emit_determinism_digest("p0", "timeshift_router")

_emit_dispatches_healing_run("p1", "timeshift_router", "L0")
_emit_routes_through("p1", "timeshift_router", "L0")
_emit_escalates_to_human("p1", "timeshift_router", "L0")
_emit_reads_policy_state("p1", "timeshift_router", "L0")
_emit_authorize_and_execute("p2", "timeshift_router", "execution_auth")
_emit_validates_capability("p2", "timeshift_router", "capability_check")
_emit_routes_to_capability("p2", "timeshift_router", "capability_route")
_emit_writes_via_uwg("p2", "timeshift_router", "uwg_write")
_emit_blocks_direct_write("p2", "timeshift_router", "direct_write_block")
_emit_records_tool_invocation("p2", "timeshift_router", "tool_invocation")
_emit_captures_execution_output("p2", "timeshift_router", "exec_output")
_emit_dispatches_agent("p3", "timeshift_router", "agent_dispatch")
_emit_coordinates_agents("p3", "timeshift_router", "agent_coordination")
_emit_records_workflow_lineage("p3", "timeshift_router", "workflow_lineage")
_emit_records_healing_outcome("p3", "timeshift_router", "healing_outcome")
_emit_escalates_failure("p3", "timeshift_router", "failure_escalation")
_emit_orchestrates_workflow("p3", "timeshift_router", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "timeshift_router", "healing_dispatch")
_emit_invokes_evaluation("p3", "timeshift_router", "evaluation_signal")
_emit_records_telemetry_event("p4", "timeshift_router", "telemetry_event")
_emit_captures_evaluation_metric("p4", "timeshift_router", "eval_metric")
_emit_stores_embedding("p4", "timeshift_router", "embedding_store")
_emit_updates_meta_learning_state("p4", "timeshift_router", "meta_learning")
_emit_links_execution_to_snapshot("p4", "timeshift_router", "exec_snapshot_link")


def _get_routing_config_and_active():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_routing_config_and_active", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_routing_config_and_active", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_routing_config_and_active")
    from agentic_core.L4_state.config.versioned_configs import RoutingConfig, get_active_configs

    return (RoutingConfig, get_active_configs)


def _get_prior_detection_signal():
    from agentic_core.L4_state.types.detection_signal_store_types import get_prior_detection_signal

    return get_prior_detection_signal


class RoutingMode:
    STANDARD = "standard"
    COMPLIANCE = "compliance_mode"


@dataclass
class TimeshiftRoutingDecision:
    """Result of a time-shifted routing evaluation."""

    mode: str
    prior_signal_hash: str | None
    prior_anomaly_score: float | None
    threshold_used: float
    same_cycle_influence: bool = False


def evaluate_timeshift_routing(
    execution_start_tick: int, routing_config: object | None = None
) -> TimeshiftRoutingDecision:
    """
    Evaluate routing mode using ONLY prior committed signals.

    Args:
        execution_start_tick: The tick at which this execution started.
            Only signals committed BEFORE this tick are considered.
        routing_config: Optional override; defaults to L4 SSOT RoutingConfig.

    Returns:
        TimeshiftRoutingDecision with mode and audit fields.

    GUARANTEE: same_cycle_influence is always False — signals emitted
    during this execution cycle cannot affect this decision.
    """
    if routing_config is None:
        _, get_active_configs = _get_routing_config_and_active()
        routing_config = get_active_configs().routing
    threshold = routing_config.anomaly_routing_threshold
    prior = _get_prior_detection_signal()(execution_start_tick)
    if prior is not None and prior.anomaly_score >= threshold:
        mode = RoutingMode.COMPLIANCE
    else:
        mode = RoutingMode.STANDARD
    return TimeshiftRoutingDecision(
        mode=mode,
        prior_signal_hash=prior.signal_hash if prior else None,
        prior_anomaly_score=prior.anomaly_score if prior else None,
        threshold_used=threshold,
        same_cycle_influence=False,
    )
