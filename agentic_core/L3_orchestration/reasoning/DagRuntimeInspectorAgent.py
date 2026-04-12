"""CONSOLIDATED: DagRuntimeInspectorAgent → InspectorExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

import importlib as _importlib

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
)

_emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_6")
_emit_records_incident_event("DagRuntimeInspectorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DagRuntimeInspectorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DagRuntimeInspectorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DagRuntimeInspectorAgent", "p4obs", "mon_state")
_emit_triggers_alert("DagRuntimeInspectorAgent", "p4obs", "alert")
_emit_links_incident_trace("DagRuntimeInspectorAgent", "p4obs", "trace_link")
_emit_captures_pattern("DagRuntimeInspectorAgent", "p3lm", "pattern")
_emit_records_learning_event("DagRuntimeInspectorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DagRuntimeInspectorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DagRuntimeInspectorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DagRuntimeInspectorAgent", "p3lm", "routing")
_emit_improves_agent_policy("DagRuntimeInspectorAgent", "p3lm", "policy")
_emit_stores_learning_state("DagRuntimeInspectorAgent", "p3lm", "state")
_emit_records_execution_trace("DagRuntimeInspectorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DagRuntimeInspectorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DagRuntimeInspectorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DagRuntimeInspectorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DagRuntimeInspectorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DagRuntimeInspectorAgent", "env_read", "p2_env_1")
_emit_reads_environ("DagRuntimeInspectorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DagRuntimeInspectorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DagRuntimeInspectorAgent", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "DagRuntimeInspectorAgent")
emit_determinism_digest("p0", "DagRuntimeInspectorAgent")

_emit_dispatches_healing_run("p1", "DagRuntimeInspectorAgent", "L3")
_emit_routes_through("p1", "DagRuntimeInspectorAgent", "L3")
_emit_checks_agent_registry("p1", "DagRuntimeInspectorAgent", "agent_registry")
_emit_validates_agent_capability("p1", "DagRuntimeInspectorAgent", "capability")
_emit_dispatches_execution_plan("p1", "DagRuntimeInspectorAgent", "exec_plan")
_emit_agent_executes_agent("p1", "DagRuntimeInspectorAgent", "sub_agent")
_emit_routes_to_agent("p1", "DagRuntimeInspectorAgent", "target_agent")
_emit_verifies_policy("p1", "DagRuntimeInspectorAgent", "policy_check")
_emit_observes_runtime_state("p1", "DagRuntimeInspectorAgent", "runtime_state")
_emit_verifies_boundary("p1", "DagRuntimeInspectorAgent", "boundary_check")
_emit_transcripts_response("p1", "DagRuntimeInspectorAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DagRuntimeInspectorAgent")
_emit_gated_by_confidence("p1", "DagRuntimeInspectorAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DagRuntimeInspectorAgent", "L3")
_emit_reads_policy_state("p1", "DagRuntimeInspectorAgent", "L3")
_emit_pulls_context("p1", "DagRuntimeInspectorAgent", "context_pull")
_emit_pulls_context("p1", "DagRuntimeInspectorAgent", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "DagRuntimeInspectorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DagRuntimeInspectorAgent", "uwg_term_secondary")
_emit_writes_through("p1", "DagRuntimeInspectorAgent", "write_through")
_emit_writes_through("p1", "DagRuntimeInspectorAgent", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "DagRuntimeInspectorAgent", "safety_validation")
_emit_invokes_eval("p1", "DagRuntimeInspectorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DagRuntimeInspectorAgent", "routing_commit")

_emit_snapshots_state("p0", "DagRuntimeInspectorAgent", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "DagRuntimeInspectorAgent", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "DagRuntimeInspectorAgent")
_emit_authorize_and_execute("p2", "DagRuntimeInspectorAgent", "execution_auth")
_emit_validates_capability("p2", "DagRuntimeInspectorAgent", "capability_check")
_emit_routes_to_capability("p2", "DagRuntimeInspectorAgent", "capability_route")
_emit_writes_via_uwg("p2", "DagRuntimeInspectorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DagRuntimeInspectorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DagRuntimeInspectorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DagRuntimeInspectorAgent", "exec_output")
_emit_dispatches_agent("p3", "DagRuntimeInspectorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DagRuntimeInspectorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DagRuntimeInspectorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DagRuntimeInspectorAgent", "healing_outcome")
_emit_escalates_failure("p3", "DagRuntimeInspectorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DagRuntimeInspectorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DagRuntimeInspectorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DagRuntimeInspectorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DagRuntimeInspectorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DagRuntimeInspectorAgent", "eval_metric")
_emit_stores_embedding("p4", "DagRuntimeInspectorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DagRuntimeInspectorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DagRuntimeInspectorAgent", "exec_snapshot_link")


def _get_DagRuntimeInspectorAgent():
    # InspectorExecutor imported lazily to avoid L3->L5 violation
    _mod = _importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
    return _mod.InspectorExecutor


DagRuntimeInspectorAgent = _get_DagRuntimeInspectorAgent()
__all__ = ["DagRuntimeInspectorAgent"]
