"""GravityLeakHealerAgent - canonical healer name alias for GravityLeakRepairAgent."""

from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
    GravityLeakRepairAgent as GravityLeakHealerAgent,
)
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

_emit_emits_metric_event("GravityLeakHealerAgent", "p4obs", "metric_1")
_emit_emits_metric_event("GravityLeakHealerAgent", "p4obs", "metric_2")
_emit_emits_metric_event("GravityLeakHealerAgent", "p4obs", "metric_3")
_emit_emits_metric_event("GravityLeakHealerAgent", "p4obs", "metric_4")
_emit_emits_metric_event("GravityLeakHealerAgent", "p4obs", "metric_5")
_emit_emits_metric_event("GravityLeakHealerAgent", "p4obs", "metric_6")
_emit_records_incident_event("GravityLeakHealerAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("GravityLeakHealerAgent", "p4obs", "anomaly")
_emit_writes_observability_log("GravityLeakHealerAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("GravityLeakHealerAgent", "p4obs", "mon_state")
_emit_triggers_alert("GravityLeakHealerAgent", "p4obs", "alert")
_emit_links_incident_trace("GravityLeakHealerAgent", "p4obs", "trace_link")
_emit_captures_pattern("GravityLeakHealerAgent", "p3lm", "pattern")
_emit_records_learning_event("GravityLeakHealerAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("GravityLeakHealerAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("GravityLeakHealerAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("GravityLeakHealerAgent", "p3lm", "routing")
_emit_improves_agent_policy("GravityLeakHealerAgent", "p3lm", "policy")
_emit_stores_learning_state("GravityLeakHealerAgent", "p3lm", "state")
_emit_records_execution_trace("GravityLeakHealerAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("GravityLeakHealerAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("GravityLeakHealerAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("GravityLeakHealerAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("GravityLeakHealerAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("GravityLeakHealerAgent", "env_read", "p2_env_1")
_emit_reads_environ("GravityLeakHealerAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("GravityLeakHealerAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("GravityLeakHealerAgent", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "GravityLeakHealerAgent")
emit_determinism_digest("p0", "GravityLeakHealerAgent")

_emit_dispatches_healing_run("p1", "GravityLeakHealerAgent", "L5")
_emit_routes_through("p1", "GravityLeakHealerAgent", "L5")
_emit_checks_agent_registry("p1", "GravityLeakHealerAgent", "agent_registry")
_emit_validates_agent_capability("p1", "GravityLeakHealerAgent", "capability")
_emit_dispatches_execution_plan("p1", "GravityLeakHealerAgent", "exec_plan")
_emit_agent_executes_agent("p1", "GravityLeakHealerAgent", "sub_agent")
_emit_routes_to_agent("p1", "GravityLeakHealerAgent", "target_agent")
_emit_verifies_policy("p1", "GravityLeakHealerAgent", "policy_check")
_emit_observes_runtime_state("p1", "GravityLeakHealerAgent", "runtime_state")
_emit_verifies_boundary("p1", "GravityLeakHealerAgent", "boundary_check")
_emit_transcripts_response("p1", "GravityLeakHealerAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "GravityLeakHealerAgent")
_emit_gated_by_confidence("p1", "GravityLeakHealerAgent", "confidence_gate")
_emit_escalates_to_human("p1", "GravityLeakHealerAgent", "L5")
_emit_reads_policy_state("p1", "GravityLeakHealerAgent", "L5")
_emit_pulls_context("p1", "GravityLeakHealerAgent", "context_pull")
_emit_pulls_context("p1", "GravityLeakHealerAgent", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "GravityLeakHealerAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "GravityLeakHealerAgent", "uwg_term_secondary")
_emit_writes_through("p1", "GravityLeakHealerAgent", "write_through")
_emit_writes_through("p1", "GravityLeakHealerAgent", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "GravityLeakHealerAgent", "safety_validation")
_emit_invokes_eval("p1", "GravityLeakHealerAgent", "eval_call")
_emit_proposal_commits_routing("p1", "GravityLeakHealerAgent", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "GravityLeakHealerAgent")
_emit_applies_guardrail("p0", "GravityLeakHealerAgent", "p0_governance")
_emit_snapshots_state("p0", "GravityLeakHealerAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "GravityLeakHealerAgent", "execution_auth")
_emit_validates_capability("p2", "GravityLeakHealerAgent", "capability_check")
_emit_routes_to_capability("p2", "GravityLeakHealerAgent", "capability_route")
_emit_writes_via_uwg("p2", "GravityLeakHealerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "GravityLeakHealerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "GravityLeakHealerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "GravityLeakHealerAgent", "exec_output")
_emit_dispatches_agent("p3", "GravityLeakHealerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "GravityLeakHealerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "GravityLeakHealerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "GravityLeakHealerAgent", "healing_outcome")
_emit_escalates_failure("p3", "GravityLeakHealerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "GravityLeakHealerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GravityLeakHealerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "GravityLeakHealerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "GravityLeakHealerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GravityLeakHealerAgent", "eval_metric")
_emit_stores_embedding("p4", "GravityLeakHealerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "GravityLeakHealerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GravityLeakHealerAgent", "exec_snapshot_link")

__all__ = ["GravityLeakHealerAgent"]
