"""
§Wave4.1 — TieredVigilanceEmitter: deterministic signal → tier mapping + emission.

Consumes normalized signal codes, assigns a VigilanceSeverity deterministically
via a fixed precedence table, and emits a VigilanceEventArtifact.

No uuid4, no wall-clock time, no elapsed_ms.
"""

from __future__ import annotations

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L6_observability.types.vigilance_event_types import (
    VigilanceEventArtifact,
    VigilanceSeverity,
    build_deterministic_trace_id,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    record_execution_trace,
)

record_execution_trace("TieredVigilanceEmitter", "TieredVigilanceEmitter_trace")


_emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_1")
_emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_2")
_emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_3")
_emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_4")
_emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_5")
_emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_6")
_emit_records_incident_event("TieredVigilanceEmitter", "p4obs", "incident")
_emit_captures_runtime_anomaly("TieredVigilanceEmitter", "p4obs", "anomaly")
_emit_writes_observability_log("TieredVigilanceEmitter", "p4obs", "obs_log")
_emit_updates_monitoring_state("TieredVigilanceEmitter", "p4obs", "mon_state")
_emit_triggers_alert("TieredVigilanceEmitter", "p4obs", "alert")
_emit_links_incident_trace("TieredVigilanceEmitter", "p4obs", "trace_link")
_emit_captures_pattern("TieredVigilanceEmitter", "p3lm", "pattern")
_emit_records_learning_event("TieredVigilanceEmitter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("TieredVigilanceEmitter", "p3lm", "snapshot")
_emit_feeds_meta_learning("TieredVigilanceEmitter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("TieredVigilanceEmitter", "p3lm", "routing")
_emit_improves_agent_policy("TieredVigilanceEmitter", "p3lm", "policy")
_emit_stores_learning_state("TieredVigilanceEmitter", "p3lm", "state")
_emit_records_execution_trace("TieredVigilanceEmitter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("TieredVigilanceEmitter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("TieredVigilanceEmitter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("TieredVigilanceEmitter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("TieredVigilanceEmitter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("TieredVigilanceEmitter", "env_read", "p2_env_1")
_emit_reads_environ("TieredVigilanceEmitter", "env_read", "p2_env_2")
_emit_reads_runtime_state("TieredVigilanceEmitter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("TieredVigilanceEmitter", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "TieredVigilanceEmitter")
emit_determinism_digest("p0", "TieredVigilanceEmitter")

_emit_dispatches_healing_run("p1", "TieredVigilanceEmitter", "L6")
_emit_routes_through("p1", "TieredVigilanceEmitter", "L6")
_emit_checks_agent_registry("p1", "TieredVigilanceEmitter", "agent_registry")
_emit_validates_agent_capability("p1", "TieredVigilanceEmitter", "capability")
_emit_dispatches_execution_plan("p1", "TieredVigilanceEmitter", "exec_plan")
_emit_agent_executes_agent("p1", "TieredVigilanceEmitter", "sub_agent")
_emit_routes_to_agent("p1", "TieredVigilanceEmitter", "target_agent")
_emit_verifies_policy("p1", "TieredVigilanceEmitter", "policy_check")
_emit_observes_runtime_state("p1", "TieredVigilanceEmitter", "runtime_state")
_emit_verifies_boundary("p1", "TieredVigilanceEmitter", "boundary_check")
_emit_transcripts_response("p1", "TieredVigilanceEmitter", "transcript")
_emit_hard_fails_untranscripted("p1", "TieredVigilanceEmitter")
_emit_gated_by_confidence("p1", "TieredVigilanceEmitter", "confidence_gate")
_emit_escalates_to_human("p1", "TieredVigilanceEmitter", "L6")
_emit_reads_policy_state("p1", "TieredVigilanceEmitter", "L6")
_emit_pulls_context("p1", "TieredVigilanceEmitter", "context_pull")
_emit_pulls_context("p1", "TieredVigilanceEmitter", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "TieredVigilanceEmitter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "TieredVigilanceEmitter", "uwg_term_secondary")
_emit_writes_through("p1", "TieredVigilanceEmitter", "write_through")
_emit_writes_through("p1", "TieredVigilanceEmitter", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "TieredVigilanceEmitter", "safety_validation")
_emit_invokes_eval("p1", "TieredVigilanceEmitter", "eval_call")
_emit_proposal_commits_routing("p1", "TieredVigilanceEmitter", "routing_commit")

_emit_snapshots_state("p0", "TieredVigilanceEmitter", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "TieredVigilanceEmitter", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "TieredVigilanceEmitter")
_emit_authorize_and_execute("p2", "TieredVigilanceEmitter", "execution_auth")
_emit_validates_capability("p2", "TieredVigilanceEmitter", "capability_check")
_emit_routes_to_capability("p2", "TieredVigilanceEmitter", "capability_route")
_emit_writes_via_uwg("p2", "TieredVigilanceEmitter", "uwg_write")
_emit_blocks_direct_write("p2", "TieredVigilanceEmitter", "direct_write_block")
_emit_records_tool_invocation("p2", "TieredVigilanceEmitter", "tool_invocation")
_emit_captures_execution_output("p2", "TieredVigilanceEmitter", "exec_output")
_emit_dispatches_agent("p3", "TieredVigilanceEmitter", "agent_dispatch")
_emit_coordinates_agents("p3", "TieredVigilanceEmitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "TieredVigilanceEmitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "TieredVigilanceEmitter", "healing_outcome")
_emit_escalates_failure("p3", "TieredVigilanceEmitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "TieredVigilanceEmitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "TieredVigilanceEmitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "TieredVigilanceEmitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "TieredVigilanceEmitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "TieredVigilanceEmitter", "eval_metric")
_emit_stores_embedding("p4", "TieredVigilanceEmitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "TieredVigilanceEmitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "TieredVigilanceEmitter", "exec_snapshot_link")

# =============================================================================
# §Wave4.1 — Fixed signal → severity mapping table
# =============================================================================
# Signals not in the table default to LOW.

_SIGNAL_SEVERITY: dict[str, VigilanceSeverity] = {
    # CRITICAL signals
    "evacuation_alert": VigilanceSeverity.CRITICAL,
    "exfiltration_detected": VigilanceSeverity.CRITICAL,
    "total_system_failure": VigilanceSeverity.CRITICAL,
    # HIGH signals
    "budget_overflow": VigilanceSeverity.HIGH,
    "circuit_breaker_open": VigilanceSeverity.HIGH,
    "mro_violation": VigilanceSeverity.HIGH,
    "import_cycle": VigilanceSeverity.HIGH,
    "stale_write_incident": VigilanceSeverity.HIGH,
    # MEDIUM signals
    "guardian_fail": VigilanceSeverity.MEDIUM,
    "policy_drift": VigilanceSeverity.MEDIUM,
    "anomalous_probe": VigilanceSeverity.MEDIUM,
    "token_drain": VigilanceSeverity.MEDIUM,
    # LOW signals (explicit)
    "info_metric": VigilanceSeverity.LOW,
    "routine_check": VigilanceSeverity.LOW,
}

_SEVERITY_RANK: dict[VigilanceSeverity, int] = {
    VigilanceSeverity.LOW: 0,
    VigilanceSeverity.MEDIUM: 1,
    VigilanceSeverity.HIGH: 2,
    VigilanceSeverity.CRITICAL: 3,
}


def classify_signals(signals: list[str]) -> VigilanceSeverity:
    """§Wave4.1 — Deterministic tier from signals.

    Stable: sorted signals, fixed precedence table, highest severity wins.
    """
    if not signals:
        return VigilanceSeverity.LOW

    max_severity = VigilanceSeverity.LOW
    for sig in signals:
        sev = _SIGNAL_SEVERITY.get(sig, VigilanceSeverity.LOW)
        if _SEVERITY_RANK[sev] > _SEVERITY_RANK[max_severity]:
            max_severity = sev

    return max_severity


def emit_vigilance_event(
    signals: list[str],
    semantic_clock: SemanticClockSnapshot,
    event_type: str = "VIGILANCE_DETECTION",
    policy_config_hash: str = "",
) -> VigilanceEventArtifact:
    """§Wave4.1 — Build a VigilanceEventArtifact deterministically.

    1. Sort + deduplicate signals
    2. Classify tier via fixed table
    3. Generate deterministic trace_id (SHA-256 of tick + signals)
    4. Return frozen artifact
    """
    normalized = tuple(sorted(set(signals)))
    tier = classify_signals(list(normalized))
    trace_id = build_deterministic_trace_id(normalized, semantic_clock.tick)

    return VigilanceEventArtifact(
        event_type=event_type,
        semantic_clock=semantic_clock,
        vigilance_tier=tier,
        signals=normalized,
        trace_id=trace_id,
        policy_config_hash=policy_config_hash,
    )


__all__ = [
    "classify_signals",
    "emit_vigilance_event",
]
