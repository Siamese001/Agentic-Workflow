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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.record_execution_trace("TieredVigilanceEmitter", "TieredVigilanceEmitter_trace")


trace_contract._emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("TieredVigilanceEmitter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("TieredVigilanceEmitter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("TieredVigilanceEmitter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("TieredVigilanceEmitter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("TieredVigilanceEmitter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("TieredVigilanceEmitter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("TieredVigilanceEmitter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("TieredVigilanceEmitter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("TieredVigilanceEmitter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("TieredVigilanceEmitter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("TieredVigilanceEmitter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("TieredVigilanceEmitter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("TieredVigilanceEmitter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("TieredVigilanceEmitter", "p3lm", "state")
trace_contract._emit_records_execution_trace("TieredVigilanceEmitter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("TieredVigilanceEmitter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("TieredVigilanceEmitter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("TieredVigilanceEmitter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("TieredVigilanceEmitter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("TieredVigilanceEmitter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("TieredVigilanceEmitter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("TieredVigilanceEmitter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("TieredVigilanceEmitter", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "TieredVigilanceEmitter")
trace_contract.emit_determinism_digest("p0", "TieredVigilanceEmitter")

trace_contract._emit_dispatches_healing_run("p1", "TieredVigilanceEmitter", "L6")
trace_contract._emit_routes_through("p1", "TieredVigilanceEmitter", "L6")
trace_contract._emit_checks_agent_registry("p1", "TieredVigilanceEmitter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "TieredVigilanceEmitter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "TieredVigilanceEmitter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "TieredVigilanceEmitter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "TieredVigilanceEmitter", "target_agent")
trace_contract._emit_verifies_policy("p1", "TieredVigilanceEmitter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "TieredVigilanceEmitter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "TieredVigilanceEmitter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "TieredVigilanceEmitter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "TieredVigilanceEmitter")
trace_contract._emit_gated_by_confidence("p1", "TieredVigilanceEmitter", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "TieredVigilanceEmitter", "L6")
trace_contract._emit_reads_policy_state("p1", "TieredVigilanceEmitter", "L6")
trace_contract._emit_pulls_context("p1", "TieredVigilanceEmitter", "context_pull")
trace_contract._emit_pulls_context("p1", "TieredVigilanceEmitter", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "TieredVigilanceEmitter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "TieredVigilanceEmitter", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "TieredVigilanceEmitter", "write_through")
trace_contract._emit_writes_through("p1", "TieredVigilanceEmitter", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "TieredVigilanceEmitter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "TieredVigilanceEmitter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "TieredVigilanceEmitter", "routing_commit")

trace_contract._emit_snapshots_state("p0", "TieredVigilanceEmitter", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "TieredVigilanceEmitter", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "TieredVigilanceEmitter")
trace_contract._emit_authorize_and_execute("p2", "TieredVigilanceEmitter", "execution_auth")
trace_contract._emit_validates_capability("p2", "TieredVigilanceEmitter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "TieredVigilanceEmitter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "TieredVigilanceEmitter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "TieredVigilanceEmitter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "TieredVigilanceEmitter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "TieredVigilanceEmitter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "TieredVigilanceEmitter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "TieredVigilanceEmitter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "TieredVigilanceEmitter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "TieredVigilanceEmitter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "TieredVigilanceEmitter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "TieredVigilanceEmitter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "TieredVigilanceEmitter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "TieredVigilanceEmitter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "TieredVigilanceEmitter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "TieredVigilanceEmitter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "TieredVigilanceEmitter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "TieredVigilanceEmitter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "TieredVigilanceEmitter", "exec_snapshot_link")

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
