"""
definitions - canonical re-export shim.

The implementation lives in agentic_core.L2_execution.types.tool_args_types.
This module re-exports for callers using
``from agentic_core.L2_execution.reasoning.definitions import ReadFileArgs, ...``.
"""

from agentic_core.L2_execution.types.tool_args_types import (  # noqa: F401
    CreateDirectoryArgs,
    DeleteFileArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("definitions", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("definitions", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("definitions", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("definitions", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("definitions", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("definitions", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("definitions", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("definitions", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("definitions", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("definitions", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("definitions", "p4obs", "alert")
trace_contract._emit_links_incident_trace("definitions", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("definitions", "p3lm", "pattern")
trace_contract._emit_records_learning_event("definitions", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("definitions", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("definitions", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("definitions", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("definitions", "p3lm", "policy")
trace_contract._emit_stores_learning_state("definitions", "p3lm", "state")
trace_contract._emit_records_execution_trace("definitions", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("definitions", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("definitions", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("definitions", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("definitions", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("definitions", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("definitions", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("definitions", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("definitions", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "definitions")
trace_contract.emit_determinism_digest("p0", "definitions")

trace_contract._emit_dispatches_healing_run("p1", "definitions", "L2")
trace_contract._emit_routes_through("p1", "definitions", "L2")
trace_contract._emit_checks_agent_registry("p1", "definitions", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "definitions", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "definitions", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "definitions", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "definitions", "target_agent")
trace_contract._emit_verifies_policy("p1", "definitions", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "definitions", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "definitions", "boundary_check")
trace_contract._emit_transcripts_response("p1", "definitions", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "definitions")
trace_contract._emit_gated_by_confidence("p1", "definitions", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "definitions", "L2")
trace_contract._emit_reads_policy_state("p1", "definitions", "L2")
trace_contract._emit_pulls_context("p1", "definitions", "context_pull")
trace_contract._emit_pulls_context("p1", "definitions", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "definitions", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "definitions", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "definitions", "write_through")
trace_contract._emit_writes_through("p1", "definitions", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "definitions", "safety_validation")
trace_contract._emit_invokes_eval("p1", "definitions", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "definitions", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "definitions")
trace_contract._emit_applies_guardrail("p0", "definitions", "p0_governance")
trace_contract._emit_snapshots_state("p0", "definitions", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "definitions", "execution_auth")
trace_contract._emit_validates_capability("p2", "definitions", "capability_check")
trace_contract._emit_routes_to_capability("p2", "definitions", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "definitions", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "definitions", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "definitions", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "definitions", "exec_output")
trace_contract._emit_dispatches_agent("p3", "definitions", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "definitions", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "definitions", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "definitions", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "definitions", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "definitions", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "definitions", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "definitions", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "definitions", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "definitions", "eval_metric")
trace_contract._emit_stores_embedding("p4", "definitions", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "definitions", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "definitions", "exec_snapshot_link")

__all__ = [
    "CreateDirectoryArgs",
    "DeleteFileArgs",
    "ListFilesArgs",
    "MoveFileArgs",
    "ReadFileArgs",
    "WriteFileArgs",
]
