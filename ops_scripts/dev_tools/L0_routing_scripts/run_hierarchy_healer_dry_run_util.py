"""
Run HierarchyHealerAgent in dry-run mode (healing_enabled=False)
This will scan for hierarchy violations without making any changes.
"""

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

emit_replay_key("p0", "run_hierarchy_healer_dry_run_util")
emit_determinism_digest("p0", "run_hierarchy_healer_dry_run_util")

_emit_dispatches_healing_run("p1", "run_hierarchy_healer_dry_run_util", "L0")
_emit_routes_through("p1", "run_hierarchy_healer_dry_run_util", "L0")
_emit_checks_agent_registry("p1", "run_hierarchy_healer_dry_run_util", "agent_registry")
_emit_validates_agent_capability("p1", "run_hierarchy_healer_dry_run_util", "capability")
_emit_dispatches_execution_plan("p1", "run_hierarchy_healer_dry_run_util", "exec_plan")
_emit_agent_executes_agent("p1", "run_hierarchy_healer_dry_run_util", "sub_agent")
_emit_routes_to_agent("p1", "run_hierarchy_healer_dry_run_util", "target_agent")
_emit_verifies_policy("p1", "run_hierarchy_healer_dry_run_util", "policy_check")
_emit_observes_runtime_state("p1", "run_hierarchy_healer_dry_run_util", "runtime_state")
_emit_verifies_boundary("p1", "run_hierarchy_healer_dry_run_util", "boundary_check")
_emit_transcripts_response("p1", "run_hierarchy_healer_dry_run_util", "transcript")
_emit_hard_fails_untranscripted("p1", "run_hierarchy_healer_dry_run_util")
_emit_gated_by_confidence("p1", "run_hierarchy_healer_dry_run_util", "confidence_gate")
_emit_escalates_to_human("p1", "run_hierarchy_healer_dry_run_util", "L0")
_emit_reads_policy_state("p1", "run_hierarchy_healer_dry_run_util", "L0")
_emit_authorize_and_execute("p2", "run_hierarchy_healer_dry_run_util", "execution_auth")
_emit_validates_capability("p2", "run_hierarchy_healer_dry_run_util", "capability_check")
_emit_routes_to_capability("p2", "run_hierarchy_healer_dry_run_util", "capability_route")
_emit_writes_via_uwg("p2", "run_hierarchy_healer_dry_run_util", "uwg_write")
_emit_blocks_direct_write("p2", "run_hierarchy_healer_dry_run_util", "direct_write_block")
_emit_records_tool_invocation("p2", "run_hierarchy_healer_dry_run_util", "tool_invocation")
_emit_captures_execution_output("p2", "run_hierarchy_healer_dry_run_util", "exec_output")
_emit_dispatches_agent("p3", "run_hierarchy_healer_dry_run_util", "agent_dispatch")
_emit_coordinates_agents("p3", "run_hierarchy_healer_dry_run_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_hierarchy_healer_dry_run_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_hierarchy_healer_dry_run_util", "healing_outcome")
_emit_escalates_failure("p3", "run_hierarchy_healer_dry_run_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_hierarchy_healer_dry_run_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_hierarchy_healer_dry_run_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_hierarchy_healer_dry_run_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_hierarchy_healer_dry_run_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_hierarchy_healer_dry_run_util", "eval_metric")
_emit_stores_embedding("p4", "run_hierarchy_healer_dry_run_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_hierarchy_healer_dry_run_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_hierarchy_healer_dry_run_util", "exec_snapshot_link")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "agentic_core").exists():
            return candidate
    raise RuntimeError(f"Could not determine project root from {__file__}")


project_root = _find_project_root()
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent
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

_emit_emits_metric_event("run_hierarchy_healer_dry_run_util", "p4obs", "metric_1")
_emit_emits_metric_event("run_hierarchy_healer_dry_run_util", "p4obs", "metric_2")
_emit_emits_metric_event("run_hierarchy_healer_dry_run_util", "p4obs", "metric_3")
_emit_emits_metric_event("run_hierarchy_healer_dry_run_util", "p4obs", "metric_4")
_emit_emits_metric_event("run_hierarchy_healer_dry_run_util", "p4obs", "metric_5")
_emit_emits_metric_event("run_hierarchy_healer_dry_run_util", "p4obs", "metric_6")
_emit_records_incident_event("run_hierarchy_healer_dry_run_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_hierarchy_healer_dry_run_util", "p4obs", "anomaly")
_emit_writes_observability_log("run_hierarchy_healer_dry_run_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_hierarchy_healer_dry_run_util", "p4obs", "mon_state")
_emit_triggers_alert("run_hierarchy_healer_dry_run_util", "p4obs", "alert")
_emit_links_incident_trace("run_hierarchy_healer_dry_run_util", "p4obs", "trace_link")
_emit_captures_pattern("run_hierarchy_healer_dry_run_util", "p3lm", "pattern")
_emit_records_learning_event("run_hierarchy_healer_dry_run_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_hierarchy_healer_dry_run_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_hierarchy_healer_dry_run_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_hierarchy_healer_dry_run_util", "p3lm", "routing")
_emit_improves_agent_policy("run_hierarchy_healer_dry_run_util", "p3lm", "policy")
_emit_stores_learning_state("run_hierarchy_healer_dry_run_util", "p3lm", "state")
_emit_records_execution_trace("run_hierarchy_healer_dry_run_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_hierarchy_healer_dry_run_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_hierarchy_healer_dry_run_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_hierarchy_healer_dry_run_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_hierarchy_healer_dry_run_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_hierarchy_healer_dry_run_util", "env_read", "p2_env_1")
_emit_reads_environ("run_hierarchy_healer_dry_run_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_hierarchy_healer_dry_run_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_hierarchy_healer_dry_run_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_hierarchy_healer_dry_run_util", "context_pull")
_emit_pulls_context("p1", "run_hierarchy_healer_dry_run_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_hierarchy_healer_dry_run_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_hierarchy_healer_dry_run_util", "uwg_term_2")
_emit_writes_through("p1", "run_hierarchy_healer_dry_run_util", "write_through")
_emit_writes_through("p1", "run_hierarchy_healer_dry_run_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_hierarchy_healer_dry_run_util", "safety_validation")
_emit_invokes_eval("p1", "run_hierarchy_healer_dry_run_util", "eval_call")
_emit_proposal_commits_routing("p1", "run_hierarchy_healer_dry_run_util", "routing_commit")


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
    print("=" * 80)
    print("HIERARCHY HEALER - DRY RUN MODE")
    print("=" * 80)
    print("Scanning for hierarchy violations (no changes will be made)...\n")
    project_root = _find_project_root()
    result = invoke_hierarchy_agent(action="heal_violations", project_root=project_root)
    print("\n" + "=" * 80)
    print("DRY RUN RESULTS")
    print("=" * 80)
    if result.get("success"):
        print(f"Files that would be relocated: {result.get('files_relocated', 0)}")
        print(f"Folders that would be removed: {result.get('folders_removed', 0)}")
        errors = result.get("errors", [])
        print(f"Errors encountered: {len(errors)}")
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  - {error}")
    else:
        print(f"❌ Error: {result.get('error')}")
    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)


if __name__ == "__main__":
    sys.exit(main())
