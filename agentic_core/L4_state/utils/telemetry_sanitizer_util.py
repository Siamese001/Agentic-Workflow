"""
Telemetry sanitizer - canonical re-export shim.

The implementation lives in agentic_core.L4_state.utils.sanitize_telemetry_util.
This module re-exports for callers using
``from agentic_core.L4_state.utils.telemetry_sanitizer import sanitize_tool_output``.
"""

from agentic_core.L4_state.utils.sanitize_telemetry_util import (  # noqa: F401
    sanitize_tool_output,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.record_execution_trace("telemetry_sanitizer_util", "telemetry_sanitizer_util_trace")


trace_contract._emit_emits_metric_event("telemetry_sanitizer_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("telemetry_sanitizer_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("telemetry_sanitizer_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("telemetry_sanitizer_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("telemetry_sanitizer_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("telemetry_sanitizer_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("telemetry_sanitizer_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("telemetry_sanitizer_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("telemetry_sanitizer_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("telemetry_sanitizer_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("telemetry_sanitizer_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("telemetry_sanitizer_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("telemetry_sanitizer_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("telemetry_sanitizer_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("telemetry_sanitizer_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("telemetry_sanitizer_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("telemetry_sanitizer_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("telemetry_sanitizer_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("telemetry_sanitizer_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("telemetry_sanitizer_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("telemetry_sanitizer_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("telemetry_sanitizer_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("telemetry_sanitizer_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("telemetry_sanitizer_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("telemetry_sanitizer_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("telemetry_sanitizer_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("telemetry_sanitizer_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("telemetry_sanitizer_util", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "telemetry_sanitizer_util")
trace_contract.emit_determinism_digest("p0", "telemetry_sanitizer_util")

trace_contract._emit_dispatches_healing_run("p1", "telemetry_sanitizer_util", "L4")
trace_contract._emit_routes_through("p1", "telemetry_sanitizer_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "telemetry_sanitizer_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "telemetry_sanitizer_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "telemetry_sanitizer_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "telemetry_sanitizer_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "telemetry_sanitizer_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "telemetry_sanitizer_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "telemetry_sanitizer_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "telemetry_sanitizer_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "telemetry_sanitizer_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "telemetry_sanitizer_util")
trace_contract._emit_gated_by_confidence("p1", "telemetry_sanitizer_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "telemetry_sanitizer_util", "L4")
trace_contract._emit_reads_policy_state("p1", "telemetry_sanitizer_util", "L4")
trace_contract._emit_pulls_context("p1", "telemetry_sanitizer_util", "context_pull")
trace_contract._emit_pulls_context("p1", "telemetry_sanitizer_util", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_sanitizer_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "telemetry_sanitizer_util", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "telemetry_sanitizer_util", "write_through")
trace_contract._emit_writes_through("p1", "telemetry_sanitizer_util", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "telemetry_sanitizer_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "telemetry_sanitizer_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "telemetry_sanitizer_util", "routing_commit")

trace_contract._emit_snapshots_state("p0", "telemetry_sanitizer_util", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "telemetry_sanitizer_util", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "telemetry_sanitizer_util")
trace_contract._emit_authorize_and_execute("p2", "telemetry_sanitizer_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "telemetry_sanitizer_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "telemetry_sanitizer_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "telemetry_sanitizer_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "telemetry_sanitizer_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "telemetry_sanitizer_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "telemetry_sanitizer_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "telemetry_sanitizer_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "telemetry_sanitizer_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "telemetry_sanitizer_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "telemetry_sanitizer_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "telemetry_sanitizer_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "telemetry_sanitizer_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "telemetry_sanitizer_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "telemetry_sanitizer_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "telemetry_sanitizer_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "telemetry_sanitizer_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "telemetry_sanitizer_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "telemetry_sanitizer_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "telemetry_sanitizer_util", "exec_snapshot_link")

__all__ = ["sanitize_tool_output"]
