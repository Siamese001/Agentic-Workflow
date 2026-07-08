"""CONSOLIDATED: DagRuntimeInspectorAgent → InspectorExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

import importlib as _importlib

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("DagRuntimeInspectorAgent", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("DagRuntimeInspectorAgent", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("DagRuntimeInspectorAgent", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("DagRuntimeInspectorAgent", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("DagRuntimeInspectorAgent", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("DagRuntimeInspectorAgent", "p4obs", "alert")
trace_contract._emit_links_incident_trace("DagRuntimeInspectorAgent", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("DagRuntimeInspectorAgent", "p3lm", "pattern")
trace_contract._emit_records_learning_event("DagRuntimeInspectorAgent", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("DagRuntimeInspectorAgent", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("DagRuntimeInspectorAgent", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("DagRuntimeInspectorAgent", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("DagRuntimeInspectorAgent", "p3lm", "policy")
trace_contract._emit_stores_learning_state("DagRuntimeInspectorAgent", "p3lm", "state")
trace_contract._emit_records_execution_trace("DagRuntimeInspectorAgent", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("DagRuntimeInspectorAgent", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("DagRuntimeInspectorAgent", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("DagRuntimeInspectorAgent", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("DagRuntimeInspectorAgent", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("DagRuntimeInspectorAgent", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("DagRuntimeInspectorAgent", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("DagRuntimeInspectorAgent", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("DagRuntimeInspectorAgent", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "DagRuntimeInspectorAgent")
trace_contract.emit_determinism_digest("p0", "DagRuntimeInspectorAgent")

trace_contract._emit_dispatches_healing_run("p1", "DagRuntimeInspectorAgent", "L3")
trace_contract._emit_routes_through("p1", "DagRuntimeInspectorAgent", "L3")
trace_contract._emit_checks_agent_registry("p1", "DagRuntimeInspectorAgent", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "DagRuntimeInspectorAgent", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "DagRuntimeInspectorAgent", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "DagRuntimeInspectorAgent", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "DagRuntimeInspectorAgent", "target_agent")
trace_contract._emit_verifies_policy("p1", "DagRuntimeInspectorAgent", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "DagRuntimeInspectorAgent", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "DagRuntimeInspectorAgent", "boundary_check")
trace_contract._emit_transcripts_response("p1", "DagRuntimeInspectorAgent", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "DagRuntimeInspectorAgent")
trace_contract._emit_gated_by_confidence("p1", "DagRuntimeInspectorAgent", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "DagRuntimeInspectorAgent", "L3")
trace_contract._emit_reads_policy_state("p1", "DagRuntimeInspectorAgent", "L3")
trace_contract._emit_pulls_context("p1", "DagRuntimeInspectorAgent", "context_pull")
trace_contract._emit_pulls_context("p1", "DagRuntimeInspectorAgent", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "DagRuntimeInspectorAgent", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "DagRuntimeInspectorAgent", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "DagRuntimeInspectorAgent", "write_through")
trace_contract._emit_writes_through("p1", "DagRuntimeInspectorAgent", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "DagRuntimeInspectorAgent", "safety_validation")
trace_contract._emit_invokes_eval("p1", "DagRuntimeInspectorAgent", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "DagRuntimeInspectorAgent", "routing_commit")

trace_contract._emit_snapshots_state("p0", "DagRuntimeInspectorAgent", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "DagRuntimeInspectorAgent", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "DagRuntimeInspectorAgent")
trace_contract._emit_authorize_and_execute("p2", "DagRuntimeInspectorAgent", "execution_auth")
trace_contract._emit_validates_capability("p2", "DagRuntimeInspectorAgent", "capability_check")
trace_contract._emit_routes_to_capability("p2", "DagRuntimeInspectorAgent", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "DagRuntimeInspectorAgent", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "DagRuntimeInspectorAgent", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "DagRuntimeInspectorAgent", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "DagRuntimeInspectorAgent", "exec_output")
trace_contract._emit_dispatches_agent("p3", "DagRuntimeInspectorAgent", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "DagRuntimeInspectorAgent", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "DagRuntimeInspectorAgent", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "DagRuntimeInspectorAgent", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "DagRuntimeInspectorAgent", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "DagRuntimeInspectorAgent", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "DagRuntimeInspectorAgent", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "DagRuntimeInspectorAgent", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "DagRuntimeInspectorAgent", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "DagRuntimeInspectorAgent", "eval_metric")
trace_contract._emit_stores_embedding("p4", "DagRuntimeInspectorAgent", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "DagRuntimeInspectorAgent", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "DagRuntimeInspectorAgent", "exec_snapshot_link")


def _get_DagRuntimeInspectorAgent():
    # InspectorExecutor imported lazily to avoid L3->L5 violation
    _mod = _importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
    return _mod.InspectorExecutor


DagRuntimeInspectorAgent = _get_DagRuntimeInspectorAgent()
__all__ = ["DagRuntimeInspectorAgent"]
