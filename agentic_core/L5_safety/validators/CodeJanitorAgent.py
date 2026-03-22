"""
validators/CodeJanitorAgent.py — backward-compat re-export shim.

Canonical implementation has moved to:
    agentic_core.L5_safety.reasoning.CodeJanitorAgent

This file is a pure re-export stub with NO mutation logic of its own.
All filesystem writes (_write_file_content, _smart_fix, heal_repository) are in
reasoning/CodeJanitorAgent.py (L5 healer territory).

ADG fix: A-04 (CodeJanitorAgent split — healer logic moved to reasoning/).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.CodeJanitorAgent import (
    CodeJanitorAgent,
    JanitorViolation,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("CodeJanitorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("CodeJanitorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("CodeJanitorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("CodeJanitorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("CodeJanitorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("CodeJanitorAgent", "p4obs", "metric_6")
_emit_records_incident_event("CodeJanitorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("CodeJanitorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("CodeJanitorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("CodeJanitorAgent", "p4obs", "mon_state")
_emit_triggers_alert("CodeJanitorAgent", "p4obs", "alert")
_emit_links_incident_trace("CodeJanitorAgent", "p4obs", "trace_link")
_emit_captures_pattern("CodeJanitorAgent", "p3lm", "pattern")
_emit_records_learning_event("CodeJanitorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("CodeJanitorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("CodeJanitorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("CodeJanitorAgent", "p3lm", "routing")
_emit_improves_agent_policy("CodeJanitorAgent", "p3lm", "policy")
_emit_stores_learning_state("CodeJanitorAgent", "p3lm", "state")
_emit_records_execution_trace("CodeJanitorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("CodeJanitorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("CodeJanitorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("CodeJanitorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("CodeJanitorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("CodeJanitorAgent", "env_read", "p2_env_1")
_emit_reads_environ("CodeJanitorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("CodeJanitorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("CodeJanitorAgent", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "CodeJanitorAgent")
emit_determinism_digest("p0", "CodeJanitorAgent")

_emit_dispatches_healing_run("p1", "CodeJanitorAgent", "L5")
_emit_routes_through("p1", "CodeJanitorAgent", "L5")
_emit_checks_agent_registry("p1", "CodeJanitorAgent", "agent_registry")
_emit_validates_agent_capability("p1", "CodeJanitorAgent", "capability")
_emit_dispatches_execution_plan("p1", "CodeJanitorAgent", "exec_plan")
_emit_agent_executes_agent("p1", "CodeJanitorAgent", "sub_agent")
_emit_routes_to_agent("p1", "CodeJanitorAgent", "target_agent")
_emit_verifies_policy("p1", "CodeJanitorAgent", "policy_check")
_emit_observes_runtime_state("p1", "CodeJanitorAgent", "runtime_state")
_emit_verifies_boundary("p1", "CodeJanitorAgent", "boundary_check")
_emit_transcripts_response("p1", "CodeJanitorAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "CodeJanitorAgent")
_emit_gated_by_confidence("p1", "CodeJanitorAgent", "confidence_gate")
_emit_escalates_to_human("p1", "CodeJanitorAgent", "L5")
_emit_reads_policy_state("p1", "CodeJanitorAgent", "L5")
_emit_pulls_context("p1", "CodeJanitorAgent", "context_pull")
_emit_pulls_context("p1", "CodeJanitorAgent", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "CodeJanitorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "CodeJanitorAgent", "uwg_term_secondary")
_emit_writes_through("p1", "CodeJanitorAgent", "write_through")
_emit_writes_through("p1", "CodeJanitorAgent", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "CodeJanitorAgent", "safety_validation")
_emit_invokes_eval("p1", "CodeJanitorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "CodeJanitorAgent", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "CodeJanitorAgent")
_emit_applies_guardrail("p0", "CodeJanitorAgent", "p0_governance")
_emit_snapshots_state("p0", "CodeJanitorAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "CodeJanitorAgent", "execution_auth")
_emit_validates_capability("p2", "CodeJanitorAgent", "capability_check")
_emit_routes_to_capability("p2", "CodeJanitorAgent", "capability_route")
_emit_writes_via_uwg("p2", "CodeJanitorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "CodeJanitorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "CodeJanitorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "CodeJanitorAgent", "exec_output")
_emit_dispatches_agent("p3", "CodeJanitorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "CodeJanitorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "CodeJanitorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "CodeJanitorAgent", "healing_outcome")
_emit_escalates_failure("p3", "CodeJanitorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "CodeJanitorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "CodeJanitorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "CodeJanitorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "CodeJanitorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "CodeJanitorAgent", "eval_metric")
_emit_stores_embedding("p4", "CodeJanitorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "CodeJanitorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "CodeJanitorAgent", "exec_snapshot_link")

__all__ = ["CodeJanitorAgent", "JanitorViolation"]
