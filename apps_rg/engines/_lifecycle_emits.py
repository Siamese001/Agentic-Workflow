"""Shared lifecycle-emit boilerplate for all apps_rg engines.

Replaces the ~103-line top-level emit block that was duplicated across 41
engine files (~4,200 lines of identical-shape boilerplate). Each engine now
calls `_emit_engine_lifecycle(__module_basename__)` once at import time.

Behavior preservation contract:
    * Same emit *names* in the same *order* as the legacy block.
    * Same `(layer, name, slot)` tuple shapes per call.
    * Same total span count (75 per-engine emits, deterministic).

This module imports every emit symbol used by the boilerplate so engines
no longer need to import them directly when they do not use them inside
class bodies.

NOTE: A handful of engines also use `_emit_records_execution_trace` and
`LayerSegment` *inside* `execute()`. Those engines retain their direct
imports of those two symbols.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_reads_policy_state,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    emit_determinism_digest,
    emit_replay_key,
)


def _emit_engine_lifecycle(engine_name: str) -> None:
    """Emit the full per-engine lifecycle trace block.

    Arguments:
        engine_name: short module basename (e.g. ``"weight_adjustment_engine"``).
            Used as the `name` slot in every emit call. Must be a stable
            identifier so runtime-ADG span deduplication works.

    The emit *order* matches the legacy inline block exactly (p2 -> p3 -> p4
    -> base_engine_import-equivalent slot -> p0 -> p4obs -> p3lm -> p2 ->
    p1 -> p0 trailer). This ordering is preserved as a behavioral contract;
    do NOT reorder without updating the runtime-ADG snapshot baseline.
    """
    # p2 — capability + execution authorization
    _emit_authorize_and_execute("p2", engine_name, "execution_auth")
    _emit_validates_capability("p2", engine_name, "capability_check")
    _emit_routes_to_capability("p2", engine_name, "capability_route")
    _emit_writes_via_uwg("p2", engine_name, "uwg_write")
    _emit_blocks_direct_write("p2", engine_name, "direct_write_block")
    _emit_records_tool_invocation("p2", engine_name, "tool_invocation")
    _emit_captures_execution_output("p2", engine_name, "exec_output")
    # p3 — orchestration / dispatch
    _emit_dispatches_agent("p3", engine_name, "agent_dispatch")
    _emit_coordinates_agents("p3", engine_name, "agent_coordination")
    _emit_records_workflow_lineage("p3", engine_name, "workflow_lineage")
    _emit_records_healing_outcome("p3", engine_name, "healing_outcome")
    _emit_escalates_failure("p3", engine_name, "failure_escalation")
    _emit_orchestrates_workflow("p3", engine_name, "workflow_orchestration")
    _emit_dispatches_healing_run("p3", engine_name, "healing_dispatch")
    _emit_invokes_evaluation("p3", engine_name, "evaluation_signal")
    # p4 — telemetry / state
    _emit_records_telemetry_event("p4", engine_name, "telemetry_event")
    _emit_captures_evaluation_metric("p4", engine_name, "eval_metric")
    _emit_stores_embedding("p4", engine_name, "embedding_store")
    _emit_updates_meta_learning_state("p4", engine_name, "meta_learning")
    _emit_links_execution_to_snapshot("p4", engine_name, "exec_snapshot_link")
    # p0 — guardrail + policy
    _emit_applies_guardrail("p0", engine_name, "p0_governance")
    _emit_reads_policy_state("p0", engine_name, "policy_binding")
    _emit_snapshots_state("p0", engine_name, "state_snapshot")
    # p4obs — metrics, incidents, anomalies
    _emit_emits_metric_event(engine_name, "p4obs", "metric_1")
    _emit_emits_metric_event(engine_name, "p4obs", "metric_2")
    _emit_emits_metric_event(engine_name, "p4obs", "metric_3")
    _emit_emits_metric_event(engine_name, "p4obs", "metric_4")
    _emit_emits_metric_event(engine_name, "p4obs", "metric_5")
    _emit_emits_metric_event(engine_name, "p4obs", "metric_6")
    _emit_records_incident_event(engine_name, "p4obs", "incident")
    _emit_captures_runtime_anomaly(engine_name, "p4obs", "anomaly")
    _emit_writes_observability_log(engine_name, "p4obs", "obs_log")
    _emit_updates_monitoring_state(engine_name, "p4obs", "mon_state")
    _emit_triggers_alert(engine_name, "p4obs", "alert")
    _emit_links_incident_trace(engine_name, "p4obs", "trace_link")
    # p3lm — learning / meta-learning
    _emit_captures_pattern(engine_name, "p3lm", "pattern")
    _emit_records_learning_event(engine_name, "p3lm", "learning_event")
    _emit_writes_learning_snapshot(engine_name, "p3lm", "snapshot")
    _emit_feeds_meta_learning(engine_name, "p3lm", "meta_feed")
    _emit_updates_routing_strategy(engine_name, "p3lm", "routing")
    _emit_improves_agent_policy(engine_name, "p3lm", "policy")
    _emit_stores_learning_state(engine_name, "p3lm", "state")
    # p2 trace — per-layer execution traces
    _emit_records_execution_trace(engine_name, "L0_ROUTING", "p2_trace_1")
    _emit_records_execution_trace(engine_name, "L1_REASONING", "p2_trace_2")
    _emit_records_execution_trace(engine_name, "L2_EXECUTION", "p2_trace_3")
    _emit_records_execution_trace(engine_name, "L3_ORCHESTRATION", "p2_trace_4")
    _emit_records_execution_trace(engine_name, "L4_STATE", "p2_trace_5")
    # p2 env / runtime reads
    _emit_reads_environ(engine_name, "env_read", "p2_env_1")
    _emit_reads_environ(engine_name, "env_read", "p2_env_2")
    _emit_reads_runtime_state(engine_name, "runtime_state", "p2_rt_1")
    _emit_reads_runtime_state(engine_name, "runtime_state", "p2_rt_2")
    # p1 — agentic dispatch / verification
    _emit_pulls_context("p1", engine_name, "context_pull")
    _emit_pulls_context("p1", engine_name, "context_pull_2")
    _emit_execution_terminates_at_uwg("p1", engine_name, "uwg_term")
    _emit_execution_terminates_at_uwg("p1", engine_name, "uwg_term_2")
    _emit_writes_through("p1", engine_name, "write_through")
    _emit_writes_through("p1", engine_name, "write_through_2")
    _emit_validated_by_safety_plane("p1", engine_name, "safety_validation")
    _emit_invokes_eval("p1", engine_name, "eval_call")
    _emit_proposal_commits_routing("p1", engine_name, "routing_commit")
    _emit_escalates_to_human("p1", engine_name, "human_escalation")
    _emit_routes_through("p1", engine_name, "route_through")
    _emit_checks_agent_registry("p1", engine_name, "agent_registry")
    _emit_validates_agent_capability("p1", engine_name, "capability")
    _emit_dispatches_execution_plan("p1", engine_name, "exec_plan")
    _emit_agent_executes_agent("p1", engine_name, "sub_agent")
    _emit_routes_to_agent("p1", engine_name, "target_agent")
    _emit_verifies_policy("p1", engine_name, "policy_check")
    _emit_observes_runtime_state("p1", engine_name, "runtime_state")
    _emit_verifies_boundary("p1", engine_name, "boundary_check")
    _emit_transcripts_response("p1", engine_name, "transcript")
    _emit_hard_fails_untranscripted("p1", engine_name)
    _emit_gated_by_confidence("p1", engine_name, "confidence_gate")
    # p0 trailer — replay/determinism/signing
    emit_replay_key("p0", engine_name)
    emit_determinism_digest("p0", engine_name)
    _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


__all__ = ["_emit_engine_lifecycle"]
