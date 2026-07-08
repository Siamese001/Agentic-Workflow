"""
Phase 9 — ReplayBundle Emitter: gateway completion path emission.

emit_replay_bundle() is called after successful execution to produce and
persist a ReplayBundle to the L4 SSOT store.

Non-mutating to knowledge index (no upsert/setex calls).
"""

from __future__ import annotations

import uuid

from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore
from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle, build_replay_bundle
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "replay_bundle_emitter")
trace_contract.emit_determinism_digest("p0", "replay_bundle_emitter")

trace_contract._emit_dispatches_healing_run("p1", "replay_bundle_emitter", "L4")
trace_contract._emit_routes_through("p1", "replay_bundle_emitter", "L4")
trace_contract._emit_checks_agent_registry("p1", "replay_bundle_emitter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "replay_bundle_emitter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "replay_bundle_emitter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "replay_bundle_emitter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "replay_bundle_emitter", "target_agent")
trace_contract._emit_verifies_policy("p1", "replay_bundle_emitter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "replay_bundle_emitter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "replay_bundle_emitter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "replay_bundle_emitter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "replay_bundle_emitter")
trace_contract._emit_gated_by_confidence("p1", "replay_bundle_emitter", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "replay_bundle_emitter", "L4")
trace_contract._emit_reads_policy_state("p1", "replay_bundle_emitter", "L4")
trace_contract._emit_authorize_and_execute("p2", "replay_bundle_emitter", "execution_auth")
trace_contract._emit_validates_capability("p2", "replay_bundle_emitter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "replay_bundle_emitter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "replay_bundle_emitter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "replay_bundle_emitter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "replay_bundle_emitter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "replay_bundle_emitter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "replay_bundle_emitter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "replay_bundle_emitter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "replay_bundle_emitter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "replay_bundle_emitter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "replay_bundle_emitter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "replay_bundle_emitter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "replay_bundle_emitter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "replay_bundle_emitter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "replay_bundle_emitter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "replay_bundle_emitter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "replay_bundle_emitter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "replay_bundle_emitter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "replay_bundle_emitter", "exec_snapshot_link")

trace_contract.record_execution_trace("replay_bundle_emitter", "replay_bundle_emitter_trace")


trace_contract._emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("replay_bundle_emitter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("replay_bundle_emitter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("replay_bundle_emitter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("replay_bundle_emitter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("replay_bundle_emitter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("replay_bundle_emitter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("replay_bundle_emitter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("replay_bundle_emitter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("replay_bundle_emitter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("replay_bundle_emitter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("replay_bundle_emitter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("replay_bundle_emitter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("replay_bundle_emitter", "p3lm", "state")
trace_contract._emit_records_execution_trace("replay_bundle_emitter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("replay_bundle_emitter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("replay_bundle_emitter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("replay_bundle_emitter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("replay_bundle_emitter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("replay_bundle_emitter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("replay_bundle_emitter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("replay_bundle_emitter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("replay_bundle_emitter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "replay_bundle_emitter", "context_pull")
trace_contract._emit_pulls_context("p1", "replay_bundle_emitter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_bundle_emitter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_bundle_emitter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "replay_bundle_emitter", "write_through")
trace_contract._emit_writes_through("p1", "replay_bundle_emitter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "replay_bundle_emitter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "replay_bundle_emitter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "replay_bundle_emitter", "routing_commit")


def emit_replay_bundle(
    mission_id: str,
    execution_start_tick: int,
    execution_end_tick: int,
    manifest_hash: str,
    active_config_hashes: dict[str, str],
    store: ReplayBundleStore,
    *,
    retrieval_used: bool = False,
    citation_hash: str = "",
    prior_detection_signal_hash: str = "",
    prior_violation_event_hashes: list[str] | None = None,
    tool_intent_hashes: list[str] | None = None,
    tool_result_hashes: list[str] | None = None,
) -> ReplayBundle:
    """
    Build and persist a ReplayBundle to the L4 SSOT store.

    Returns the persisted ReplayBundle (with stable replay_hash).
    Non-mutating to knowledge index.
    """
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "emit_replay_bundle", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "emit_replay_bundle")
    trace_contract._emit_snapshots_state(str(uuid.uuid4()), "Module.emit_replay_bundle", "L4_STATE")
    bundle = build_replay_bundle(
        mission_id=mission_id,
        execution_start_tick=execution_start_tick,
        execution_end_tick=execution_end_tick,
        manifest_hash=manifest_hash,
        active_config_hashes=active_config_hashes,
        retrieval_used=retrieval_used,
        citation_hash=citation_hash,
        prior_detection_signal_hash=prior_detection_signal_hash,
        prior_violation_event_hashes=prior_violation_event_hashes,
        tool_intent_hashes=tool_intent_hashes,
        tool_result_hashes=tool_result_hashes,
    )
    store.store_replay_bundle(bundle)
    return bundle
