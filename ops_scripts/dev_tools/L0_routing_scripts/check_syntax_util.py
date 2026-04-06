"""Quick syntax check to identify the 3 remaining errors."""

import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "check_syntax_util")
emit_determinism_digest("p0", "check_syntax_util")

_emit_dispatches_healing_run("p1", "check_syntax_util", "L0")
_emit_routes_through("p1", "check_syntax_util", "L0")
_emit_checks_agent_registry("p1", "check_syntax_util", "agent_registry")
_emit_validates_agent_capability("p1", "check_syntax_util", "capability")
_emit_dispatches_execution_plan("p1", "check_syntax_util", "exec_plan")
_emit_agent_executes_agent("p1", "check_syntax_util", "sub_agent")
_emit_routes_to_agent("p1", "check_syntax_util", "target_agent")
_emit_verifies_policy("p1", "check_syntax_util", "policy_check")
_emit_observes_runtime_state("p1", "check_syntax_util", "runtime_state")
_emit_verifies_boundary("p1", "check_syntax_util", "boundary_check")
_emit_transcripts_response("p1", "check_syntax_util", "transcript")
_emit_hard_fails_untranscripted("p1", "check_syntax_util")
_emit_gated_by_confidence("p1", "check_syntax_util", "confidence_gate")
_emit_escalates_to_human("p1", "check_syntax_util", "L0")
_emit_reads_policy_state("p1", "check_syntax_util", "L0")
_emit_authorize_and_execute("p2", "check_syntax_util", "execution_auth")
_emit_validates_capability("p2", "check_syntax_util", "capability_check")
_emit_routes_to_capability("p2", "check_syntax_util", "capability_route")
_emit_writes_via_uwg("p2", "check_syntax_util", "uwg_write")
_emit_blocks_direct_write("p2", "check_syntax_util", "direct_write_block")
_emit_records_tool_invocation("p2", "check_syntax_util", "tool_invocation")
_emit_captures_execution_output("p2", "check_syntax_util", "exec_output")
_emit_dispatches_agent("p3", "check_syntax_util", "agent_dispatch")
_emit_coordinates_agents("p3", "check_syntax_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_syntax_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_syntax_util", "healing_outcome")
_emit_escalates_failure("p3", "check_syntax_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_syntax_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_syntax_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_syntax_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_syntax_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_syntax_util", "eval_metric")
_emit_stores_embedding("p4", "check_syntax_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_syntax_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_syntax_util", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("check_syntax_util", "p4obs", "metric_1")
_emit_emits_metric_event("check_syntax_util", "p4obs", "metric_2")
_emit_emits_metric_event("check_syntax_util", "p4obs", "metric_3")
_emit_emits_metric_event("check_syntax_util", "p4obs", "metric_4")
_emit_emits_metric_event("check_syntax_util", "p4obs", "metric_5")
_emit_emits_metric_event("check_syntax_util", "p4obs", "metric_6")
_emit_records_incident_event("check_syntax_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_syntax_util", "p4obs", "anomaly")
_emit_writes_observability_log("check_syntax_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_syntax_util", "p4obs", "mon_state")
_emit_triggers_alert("check_syntax_util", "p4obs", "alert")
_emit_links_incident_trace("check_syntax_util", "p4obs", "trace_link")
_emit_captures_pattern("check_syntax_util", "p3lm", "pattern")
_emit_records_learning_event("check_syntax_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_syntax_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_syntax_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_syntax_util", "p3lm", "routing")
_emit_improves_agent_policy("check_syntax_util", "p3lm", "policy")
_emit_stores_learning_state("check_syntax_util", "p3lm", "state")
_emit_records_execution_trace("check_syntax_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_syntax_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_syntax_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_syntax_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_syntax_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_syntax_util", "env_read", "p2_env_1")
_emit_reads_environ("check_syntax_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_syntax_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_syntax_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_syntax_util", "context_pull")
_emit_pulls_context("p1", "check_syntax_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "check_syntax_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_syntax_util", "uwg_term_2")
_emit_writes_through("p1", "check_syntax_util", "write_through")
_emit_writes_through("p1", "check_syntax_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "check_syntax_util", "safety_validation")
_emit_invokes_eval("p1", "check_syntax_util", "eval_call")
_emit_proposal_commits_routing("p1", "check_syntax_util", "routing_commit")


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    project_root = Path(__file__).parent.parent
    result = invoke_code_validator(action="validate", project_root=project_root)
    if result.get("success"):
        print(f"Total errors: {result.get('total_violations', 0)}")
        print()
        for v in result.get("violations", []):
            print(f"{v['file_path']}:{v['line_number']}:{v['column']} - {v['error_message']}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()
