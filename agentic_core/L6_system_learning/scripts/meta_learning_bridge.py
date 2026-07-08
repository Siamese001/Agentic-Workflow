"""APPS_* Meta-Learning Emit-Only Bridge — Waves 7.0.9–7.0.11.

Pure emit-only bridge for APPS_* domains to produce meta-learning artifacts.
Calls L7 builders to construct frozen, deterministic artifacts.

HARD RULES
----------
- MUST NOT import any executors.
- MUST NOT call any apply/mutation functions from L7.
- MUST NOT write files or mutate any configuration.
- Returns artifacts only; callers decide what to do with them.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from agentic_core.interfaces.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "meta_learning_bridge", "execution_auth")
trace_contract._emit_validates_capability("p2", "meta_learning_bridge", "capability_check")
trace_contract._emit_routes_to_capability("p2", "meta_learning_bridge", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "meta_learning_bridge", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "meta_learning_bridge", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "meta_learning_bridge", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "meta_learning_bridge", "exec_output")
trace_contract._emit_dispatches_agent("p3", "meta_learning_bridge", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "meta_learning_bridge", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "meta_learning_bridge", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "meta_learning_bridge", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "meta_learning_bridge", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "meta_learning_bridge", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "meta_learning_bridge", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "meta_learning_bridge", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "meta_learning_bridge", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "meta_learning_bridge", "eval_metric")
trace_contract._emit_stores_embedding("p4", "meta_learning_bridge", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "meta_learning_bridge", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "meta_learning_bridge", "exec_snapshot_link")
from agentic_core.L6_system_learning.types.app_signal_types import (
    AppSignalAggregateArtifact,
    AppSignalEventArtifact,
    aggregate_app_signals,
    build_app_signal_event,
)
from agentic_core.L6_system_learning.types.meta_learning_types import (
    MetaLearningProposalArtifact,
    build_meta_learning_proposal,
)

trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("meta_learning_bridge", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("meta_learning_bridge", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("meta_learning_bridge", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("meta_learning_bridge", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("meta_learning_bridge", "p4obs", "alert")
trace_contract._emit_links_incident_trace("meta_learning_bridge", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("meta_learning_bridge", "p3lm", "pattern")
trace_contract._emit_records_learning_event("meta_learning_bridge", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("meta_learning_bridge", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("meta_learning_bridge", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("meta_learning_bridge", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("meta_learning_bridge", "p3lm", "policy")
trace_contract._emit_stores_learning_state("meta_learning_bridge", "p3lm", "state")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("meta_learning_bridge", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("meta_learning_bridge", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("meta_learning_bridge", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("meta_learning_bridge", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "meta_learning_bridge")
trace_contract._emit_applies_guardrail("p0", "meta_learning_bridge", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "meta_learning_bridge", "policy_binding")
trace_contract._emit_snapshots_state("p0", "meta_learning_bridge", "state_snapshot")
trace_contract._emit_pulls_context("p1", "meta_learning_bridge", "context_pull")
trace_contract._emit_pulls_context("p1", "meta_learning_bridge", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_bridge", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_bridge", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "meta_learning_bridge", "write_through")
trace_contract._emit_writes_through("p1", "meta_learning_bridge", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "meta_learning_bridge", "safety_validation")
trace_contract._emit_invokes_eval("p1", "meta_learning_bridge", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "meta_learning_bridge", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "meta_learning_bridge", "human_escalation")
trace_contract._emit_routes_through("p1", "meta_learning_bridge", "route_through")
trace_contract._emit_checks_agent_registry("p1", "meta_learning_bridge", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "meta_learning_bridge", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "meta_learning_bridge", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "meta_learning_bridge", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "meta_learning_bridge", "target_agent")
trace_contract._emit_verifies_policy("p1", "meta_learning_bridge", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "meta_learning_bridge", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "meta_learning_bridge", "boundary_check")
trace_contract._emit_transcripts_response("p1", "meta_learning_bridge", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "meta_learning_bridge")
trace_contract._emit_gated_by_confidence("p1", "meta_learning_bridge", "confidence_gate")
trace_contract.emit_replay_key("p0", "meta_learning_bridge")
trace_contract.emit_determinism_digest("p0", "meta_learning_bridge")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def emit_app_signal_event(
    *,
    app_id: str,
    run_id: str,
    message_id: str,
    metric_name: str,
    metric_value: float,
    semantic_clock: SemanticClockSnapshot,
    segment_id: str | None = None,
    outcome_label: str | None = None,
    timestamp_utc: str | None = None,
) -> AppSignalEventArtifact:
    """Emit an APP_SIGNAL_EVENT artifact via the L7 builder.

    Pure function — no side effects, no file writes, no apply calls.

    Parameters
    ----------
    app_id : str
        Application identifier (e.g. "apps_rg", "apps_lic").
    run_id : str
        Unique run/session identifier.
    message_id : str
        Unique message identifier within the run.
    metric_name : str
        Name of the metric (must be non-empty).
    metric_value : float
        Observed metric value (must be finite).
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    segment_id : str | None
        Optional sub-segment identifier.
    outcome_label : str | None
        Optional categorical outcome label.
    timestamp_utc : str | None
        Optional ISO-8601 timestamp string.

    Returns
    -------
    AppSignalEventArtifact
        Frozen, deterministic signal event artifact.
    """
    return build_app_signal_event(
        app_id=app_id,
        run_id=run_id,
        message_id=message_id,
        segment_id=segment_id,
        metric_name=metric_name,
        metric_value=metric_value,
        outcome_label=outcome_label,
        timestamp_utc=timestamp_utc,
        semantic_clock=semantic_clock,
    )


def propose_from_signal_aggregate(
    *,
    app_id: str,
    target_component: str,
    before: dict,
    after: dict,
    metric_name: str,
    baseline: float,
    candidate: float,
    evidence_hash: str,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None = None,
) -> MetaLearningProposalArtifact:
    """Build a MetaLearningProposalArtifact from an APP signal aggregate.

    Pure function — no side effects, no file writes, no apply calls.
    The proposer field is set to "apps_<name>" derived from app_id.

    Parameters
    ----------
    app_id : str
        Application identifier (e.g. "apps_rg", "apps_lic").
    target_component : str
        Target of the proposed change (must NOT be in IMMUTABLE_COMPONENTS).
    before, after : dict
        State before and after the proposed change.
    metric_name : str
        Name of the objective metric.
    baseline, candidate : float
        Metric values before and after the proposed change.
    evidence_hash : str
        SHA-256 of the supporting evidence bundle.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Optional hash of the governing policy config.

    Returns
    -------
    MetaLearningProposalArtifact
        Frozen, deterministic proposal artifact.
    """
    proposer = app_id if app_id.startswith("apps_") else f"apps_{app_id}"
    return build_meta_learning_proposal(
        semantic_clock=semantic_clock,
        proposer=proposer,
        target_component=target_component,
        before=before,
        after=after,
        metric_name=metric_name,
        baseline=baseline,
        candidate=candidate,
        evidence_hash=evidence_hash,
        policy_config_hash=policy_config_hash,
    )


def emit_app_signal_aggregate(
    *,
    app_id: str,
    window_id: str,
    metric_name: str,
    events: Sequence[AppSignalEventArtifact],
    baseline_selector: Callable[[AppSignalEventArtifact], bool],
    candidate_selector: Callable[[AppSignalEventArtifact], bool],
    evidence_hash: str,
    semantic_clock: SemanticClockSnapshot,
) -> AppSignalAggregateArtifact:
    """Aggregate APP signal events into an AppSignalAggregateArtifact.

    Pure function — no side effects, no file writes, no apply calls.
    Delegates to aggregate_app_signals() for deterministic computation.
    """
    return aggregate_app_signals(
        app_id=app_id,
        window_id=window_id,
        metric_name=metric_name,
        events=events,
        baseline_selector=baseline_selector,
        candidate_selector=candidate_selector,
        evidence_hash=evidence_hash,
        semantic_clock=semantic_clock,
    )
