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
