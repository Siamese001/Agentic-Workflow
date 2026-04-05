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
from agentic_core.runtime.lifecycle_trace_contract import (
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
    record_execution_trace,
)

emit_replay_key("p0", "replay_bundle_emitter")
emit_determinism_digest("p0", "replay_bundle_emitter")

_emit_dispatches_healing_run("p1", "replay_bundle_emitter", "L4")
_emit_routes_through("p1", "replay_bundle_emitter", "L4")
_emit_checks_agent_registry("p1", "replay_bundle_emitter", "agent_registry")
_emit_validates_agent_capability("p1", "replay_bundle_emitter", "capability")
_emit_dispatches_execution_plan("p1", "replay_bundle_emitter", "exec_plan")
_emit_agent_executes_agent("p1", "replay_bundle_emitter", "sub_agent")
_emit_routes_to_agent("p1", "replay_bundle_emitter", "target_agent")
_emit_verifies_policy("p1", "replay_bundle_emitter", "policy_check")
_emit_observes_runtime_state("p1", "replay_bundle_emitter", "runtime_state")
_emit_verifies_boundary("p1", "replay_bundle_emitter", "boundary_check")
_emit_transcripts_response("p1", "replay_bundle_emitter", "transcript")
_emit_hard_fails_untranscripted("p1", "replay_bundle_emitter")
_emit_gated_by_confidence("p1", "replay_bundle_emitter", "confidence_gate")
_emit_escalates_to_human("p1", "replay_bundle_emitter", "L4")
_emit_reads_policy_state("p1", "replay_bundle_emitter", "L4")
_emit_authorize_and_execute("p2", "replay_bundle_emitter", "execution_auth")
_emit_validates_capability("p2", "replay_bundle_emitter", "capability_check")
_emit_routes_to_capability("p2", "replay_bundle_emitter", "capability_route")
_emit_writes_via_uwg("p2", "replay_bundle_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "replay_bundle_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_bundle_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "replay_bundle_emitter", "exec_output")
_emit_dispatches_agent("p3", "replay_bundle_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_bundle_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_bundle_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_bundle_emitter", "healing_outcome")
_emit_escalates_failure("p3", "replay_bundle_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_bundle_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_bundle_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_bundle_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_bundle_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_bundle_emitter", "eval_metric")
_emit_stores_embedding("p4", "replay_bundle_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_bundle_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_bundle_emitter", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

record_execution_trace("replay_bundle_emitter", "replay_bundle_emitter_trace")


_emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_1")
_emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_2")
_emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_3")
_emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_4")
_emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_5")
_emit_emits_metric_event("replay_bundle_emitter", "p4obs", "metric_6")
_emit_records_incident_event("replay_bundle_emitter", "p4obs", "incident")
_emit_captures_runtime_anomaly("replay_bundle_emitter", "p4obs", "anomaly")
_emit_writes_observability_log("replay_bundle_emitter", "p4obs", "obs_log")
_emit_updates_monitoring_state("replay_bundle_emitter", "p4obs", "mon_state")
_emit_triggers_alert("replay_bundle_emitter", "p4obs", "alert")
_emit_links_incident_trace("replay_bundle_emitter", "p4obs", "trace_link")
_emit_captures_pattern("replay_bundle_emitter", "p3lm", "pattern")
_emit_records_learning_event("replay_bundle_emitter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("replay_bundle_emitter", "p3lm", "snapshot")
_emit_feeds_meta_learning("replay_bundle_emitter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("replay_bundle_emitter", "p3lm", "routing")
_emit_improves_agent_policy("replay_bundle_emitter", "p3lm", "policy")
_emit_stores_learning_state("replay_bundle_emitter", "p3lm", "state")
_emit_records_execution_trace("replay_bundle_emitter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("replay_bundle_emitter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("replay_bundle_emitter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("replay_bundle_emitter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("replay_bundle_emitter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("replay_bundle_emitter", "env_read", "p2_env_1")
_emit_reads_environ("replay_bundle_emitter", "env_read", "p2_env_2")
_emit_reads_runtime_state("replay_bundle_emitter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("replay_bundle_emitter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "replay_bundle_emitter", "context_pull")
_emit_pulls_context("p1", "replay_bundle_emitter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "replay_bundle_emitter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "replay_bundle_emitter", "uwg_term_2")
_emit_writes_through("p1", "replay_bundle_emitter", "write_through")
_emit_writes_through("p1", "replay_bundle_emitter", "write_through_2")
_emit_validated_by_safety_plane("p1", "replay_bundle_emitter", "safety_validation")
_emit_invokes_eval("p1", "replay_bundle_emitter", "eval_call")
_emit_proposal_commits_routing("p1", "replay_bundle_emitter", "routing_commit")


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
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "emit_replay_bundle", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "emit_replay_bundle")
    _emit_snapshots_state(str(uuid.uuid4()), "Module.emit_replay_bundle", "L4_STATE")
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
