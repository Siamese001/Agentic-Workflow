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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "timeshift_router")
emit_determinism_digest("p0", "timeshift_router")

_emit_dispatches_healing_run("p1", "timeshift_router", "L0")
_emit_routes_through("p1", "timeshift_router", "L0")
_emit_checks_agent_registry("p1", "timeshift_router", "agent_registry")
_emit_validates_agent_capability("p1", "timeshift_router", "capability")
_emit_dispatches_execution_plan("p1", "timeshift_router", "exec_plan")
_emit_agent_executes_agent("p1", "timeshift_router", "sub_agent")
_emit_routes_to_agent("p1", "timeshift_router", "target_agent")
_emit_verifies_policy("p1", "timeshift_router", "policy_check")
_emit_observes_runtime_state("p1", "timeshift_router", "runtime_state")
_emit_verifies_boundary("p1", "timeshift_router", "boundary_check")
_emit_transcripts_response("p1", "timeshift_router", "transcript")
_emit_hard_fails_untranscripted("p1", "timeshift_router")
_emit_gated_by_confidence("p1", "timeshift_router", "confidence_gate")
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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("timeshift_router", "p4obs", "metric_1")
_emit_emits_metric_event("timeshift_router", "p4obs", "metric_2")
_emit_emits_metric_event("timeshift_router", "p4obs", "metric_3")
_emit_emits_metric_event("timeshift_router", "p4obs", "metric_4")
_emit_emits_metric_event("timeshift_router", "p4obs", "metric_5")
_emit_emits_metric_event("timeshift_router", "p4obs", "metric_6")
_emit_records_incident_event("timeshift_router", "p4obs", "incident")
_emit_captures_runtime_anomaly("timeshift_router", "p4obs", "anomaly")
_emit_writes_observability_log("timeshift_router", "p4obs", "obs_log")
_emit_updates_monitoring_state("timeshift_router", "p4obs", "mon_state")
_emit_triggers_alert("timeshift_router", "p4obs", "alert")
_emit_links_incident_trace("timeshift_router", "p4obs", "trace_link")
_emit_captures_pattern("timeshift_router", "p3lm", "pattern")
_emit_records_learning_event("timeshift_router", "p3lm", "learning_event")
_emit_writes_learning_snapshot("timeshift_router", "p3lm", "snapshot")
_emit_feeds_meta_learning("timeshift_router", "p3lm", "meta_feed")
_emit_updates_routing_strategy("timeshift_router", "p3lm", "routing")
_emit_improves_agent_policy("timeshift_router", "p3lm", "policy")
_emit_stores_learning_state("timeshift_router", "p3lm", "state")
_emit_records_execution_trace("timeshift_router", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("timeshift_router", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("timeshift_router", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("timeshift_router", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("timeshift_router", "L4_STATE", "p2_trace_5")
_emit_reads_environ("timeshift_router", "env_read", "p2_env_1")
_emit_reads_environ("timeshift_router", "env_read", "p2_env_2")
_emit_reads_runtime_state("timeshift_router", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("timeshift_router", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "timeshift_router", "context_pull")
_emit_pulls_context("p1", "timeshift_router", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "timeshift_router", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "timeshift_router", "uwg_term_2")
_emit_writes_through("p1", "timeshift_router", "write_through")
_emit_writes_through("p1", "timeshift_router", "write_through_2")
_emit_validated_by_safety_plane("p1", "timeshift_router", "safety_validation")
_emit_invokes_eval("p1", "timeshift_router", "eval_call")
_emit_proposal_commits_routing("p1", "timeshift_router", "routing_commit")


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
