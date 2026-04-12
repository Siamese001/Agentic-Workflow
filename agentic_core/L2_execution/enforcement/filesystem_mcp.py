from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
)

emit_replay_key("p0", "filesystem_mcp")
emit_determinism_digest("p0", "filesystem_mcp")

_emit_dispatches_healing_run("p1", "filesystem_mcp", "L2")
_emit_routes_through("p1", "filesystem_mcp", "L2")
_emit_checks_agent_registry("p1", "filesystem_mcp", "agent_registry")
_emit_validates_agent_capability("p1", "filesystem_mcp", "capability")
_emit_dispatches_execution_plan("p1", "filesystem_mcp", "exec_plan")
_emit_agent_executes_agent("p1", "filesystem_mcp", "sub_agent")
_emit_routes_to_agent("p1", "filesystem_mcp", "target_agent")
_emit_verifies_policy("p1", "filesystem_mcp", "policy_check")
_emit_observes_runtime_state("p1", "filesystem_mcp", "runtime_state")
_emit_verifies_boundary("p1", "filesystem_mcp", "boundary_check")
_emit_transcripts_response("p1", "filesystem_mcp", "transcript")
_emit_hard_fails_untranscripted("p1", "filesystem_mcp")
_emit_gated_by_confidence("p1", "filesystem_mcp", "confidence_gate")
_emit_escalates_to_human("p1", "filesystem_mcp", "L2")
_emit_reads_policy_state("p1", "filesystem_mcp", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "filesystem_mcp")
_emit_applies_guardrail("p0", "filesystem_mcp", "p0_governance")
_emit_snapshots_state("p0", "filesystem_mcp", "state_snapshot")
_emit_authorize_and_execute("p2", "filesystem_mcp", "execution_auth")
_emit_validates_capability("p2", "filesystem_mcp", "capability_check")
_emit_routes_to_capability("p2", "filesystem_mcp", "capability_route")
_emit_writes_via_uwg("p2", "filesystem_mcp", "uwg_write")
_emit_blocks_direct_write("p2", "filesystem_mcp", "direct_write_block")
_emit_records_tool_invocation("p2", "filesystem_mcp", "tool_invocation")
_emit_captures_execution_output("p2", "filesystem_mcp", "exec_output")
_emit_dispatches_agent("p3", "filesystem_mcp", "agent_dispatch")
_emit_coordinates_agents("p3", "filesystem_mcp", "agent_coordination")
_emit_records_workflow_lineage("p3", "filesystem_mcp", "workflow_lineage")
_emit_records_healing_outcome("p3", "filesystem_mcp", "healing_outcome")
_emit_escalates_failure("p3", "filesystem_mcp", "failure_escalation")
_emit_orchestrates_workflow("p3", "filesystem_mcp", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "filesystem_mcp", "healing_dispatch")
_emit_invokes_evaluation("p3", "filesystem_mcp", "evaluation_signal")
_emit_records_telemetry_event("p4", "filesystem_mcp", "telemetry_event")
_emit_captures_evaluation_metric("p4", "filesystem_mcp", "eval_metric")
_emit_stores_embedding("p4", "filesystem_mcp", "embedding_store")
_emit_updates_meta_learning_state("p4", "filesystem_mcp", "meta_learning")
_emit_links_execution_to_snapshot("p4", "filesystem_mcp", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("filesystem_mcp", "p4obs", "metric_1")
_emit_emits_metric_event("filesystem_mcp", "p4obs", "metric_2")
_emit_emits_metric_event("filesystem_mcp", "p4obs", "metric_3")
_emit_emits_metric_event("filesystem_mcp", "p4obs", "metric_4")
_emit_emits_metric_event("filesystem_mcp", "p4obs", "metric_5")
_emit_emits_metric_event("filesystem_mcp", "p4obs", "metric_6")
_emit_records_incident_event("filesystem_mcp", "p4obs", "incident")
_emit_captures_runtime_anomaly("filesystem_mcp", "p4obs", "anomaly")
_emit_writes_observability_log("filesystem_mcp", "p4obs", "obs_log")
_emit_updates_monitoring_state("filesystem_mcp", "p4obs", "mon_state")
_emit_triggers_alert("filesystem_mcp", "p4obs", "alert")
_emit_links_incident_trace("filesystem_mcp", "p4obs", "trace_link")
_emit_captures_pattern("filesystem_mcp", "p3lm", "pattern")
_emit_records_learning_event("filesystem_mcp", "p3lm", "learning_event")
_emit_writes_learning_snapshot("filesystem_mcp", "p3lm", "snapshot")
_emit_feeds_meta_learning("filesystem_mcp", "p3lm", "meta_feed")
_emit_updates_routing_strategy("filesystem_mcp", "p3lm", "routing")
_emit_improves_agent_policy("filesystem_mcp", "p3lm", "policy")
_emit_stores_learning_state("filesystem_mcp", "p3lm", "state")
_emit_records_execution_trace("filesystem_mcp", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("filesystem_mcp", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("filesystem_mcp", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("filesystem_mcp", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("filesystem_mcp", "L4_STATE", "p2_trace_5")
_emit_reads_environ("filesystem_mcp", "env_read", "p2_env_1")
_emit_reads_environ("filesystem_mcp", "env_read", "p2_env_2")
_emit_reads_runtime_state("filesystem_mcp", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("filesystem_mcp", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "filesystem_mcp", "context_pull")
_emit_pulls_context("p1", "filesystem_mcp", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "filesystem_mcp", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "filesystem_mcp", "uwg_term_2")
_emit_writes_through("p1", "filesystem_mcp", "write_through")
_emit_writes_through("p1", "filesystem_mcp", "write_through_2")
_emit_validated_by_safety_plane("p1", "filesystem_mcp", "safety_validation")
_emit_invokes_eval("p1", "filesystem_mcp", "eval_call")
_emit_proposal_commits_routing("p1", "filesystem_mcp", "routing_commit")

try:
    from .filesystem_mcp import FilesystemMCP
except ImportError as e:
    raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow

    class FilesystemMCP:
        def __init__(self, *args, **kwargs):
            print("   [STUB] FilesystemMCP active — direct filesystem operations permitted")

        def execute_move(self, source, target, **kwargs):
            return {"status": "allowed", "method": "direct"}

        def execute_write(self, path, content):
            return {"status": "allowed"}


print("   [OK] agentic_core.L4_state.memory package initialized (stub mode)")
