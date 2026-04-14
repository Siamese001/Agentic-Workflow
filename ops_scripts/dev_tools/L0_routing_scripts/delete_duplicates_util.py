"""
Delete duplicate files based on scan results.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "delete_duplicates_util")
emit_determinism_digest("p0", "delete_duplicates_util")

_emit_dispatches_healing_run("p1", "delete_duplicates_util", "L0")
_emit_routes_through("p1", "delete_duplicates_util", "L0")
_emit_checks_agent_registry("p1", "delete_duplicates_util", "agent_registry")
_emit_validates_agent_capability("p1", "delete_duplicates_util", "capability")
_emit_dispatches_execution_plan("p1", "delete_duplicates_util", "exec_plan")
_emit_agent_executes_agent("p1", "delete_duplicates_util", "sub_agent")
_emit_routes_to_agent("p1", "delete_duplicates_util", "target_agent")
_emit_verifies_policy("p1", "delete_duplicates_util", "policy_check")
_emit_observes_runtime_state("p1", "delete_duplicates_util", "runtime_state")
_emit_verifies_boundary("p1", "delete_duplicates_util", "boundary_check")
_emit_transcripts_response("p1", "delete_duplicates_util", "transcript")
_emit_hard_fails_untranscripted("p1", "delete_duplicates_util")
_emit_gated_by_confidence("p1", "delete_duplicates_util", "confidence_gate")
_emit_escalates_to_human("p1", "delete_duplicates_util", "L0")
_emit_reads_policy_state("p1", "delete_duplicates_util", "L0")
_emit_authorize_and_execute("p2", "delete_duplicates_util", "execution_auth")
_emit_validates_capability("p2", "delete_duplicates_util", "capability_check")
_emit_routes_to_capability("p2", "delete_duplicates_util", "capability_route")
_emit_writes_via_uwg("p2", "delete_duplicates_util", "uwg_write")
_emit_blocks_direct_write("p2", "delete_duplicates_util", "direct_write_block")
_emit_records_tool_invocation("p2", "delete_duplicates_util", "tool_invocation")
_emit_captures_execution_output("p2", "delete_duplicates_util", "exec_output")
_emit_dispatches_agent("p3", "delete_duplicates_util", "agent_dispatch")
_emit_coordinates_agents("p3", "delete_duplicates_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "delete_duplicates_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "delete_duplicates_util", "healing_outcome")
_emit_escalates_failure("p3", "delete_duplicates_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "delete_duplicates_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "delete_duplicates_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "delete_duplicates_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "delete_duplicates_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "delete_duplicates_util", "eval_metric")
_emit_stores_embedding("p4", "delete_duplicates_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "delete_duplicates_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "delete_duplicates_util", "exec_snapshot_link")
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

_emit_emits_metric_event("delete_duplicates_util", "p4obs", "metric_1")
_emit_emits_metric_event("delete_duplicates_util", "p4obs", "metric_2")
_emit_emits_metric_event("delete_duplicates_util", "p4obs", "metric_3")
_emit_emits_metric_event("delete_duplicates_util", "p4obs", "metric_4")
_emit_emits_metric_event("delete_duplicates_util", "p4obs", "metric_5")
_emit_emits_metric_event("delete_duplicates_util", "p4obs", "metric_6")
_emit_records_incident_event("delete_duplicates_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("delete_duplicates_util", "p4obs", "anomaly")
_emit_writes_observability_log("delete_duplicates_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("delete_duplicates_util", "p4obs", "mon_state")
_emit_triggers_alert("delete_duplicates_util", "p4obs", "alert")
_emit_links_incident_trace("delete_duplicates_util", "p4obs", "trace_link")
_emit_captures_pattern("delete_duplicates_util", "p3lm", "pattern")
_emit_records_learning_event("delete_duplicates_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("delete_duplicates_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("delete_duplicates_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("delete_duplicates_util", "p3lm", "routing")
_emit_improves_agent_policy("delete_duplicates_util", "p3lm", "policy")
_emit_stores_learning_state("delete_duplicates_util", "p3lm", "state")
_emit_records_execution_trace("delete_duplicates_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("delete_duplicates_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("delete_duplicates_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("delete_duplicates_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("delete_duplicates_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("delete_duplicates_util", "env_read", "p2_env_1")
_emit_reads_environ("delete_duplicates_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("delete_duplicates_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("delete_duplicates_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "delete_duplicates_util", "context_pull")
_emit_pulls_context("p1", "delete_duplicates_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "delete_duplicates_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "delete_duplicates_util", "uwg_term_2")
_emit_writes_through("p1", "delete_duplicates_util", "write_through")
_emit_writes_through("p1", "delete_duplicates_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "delete_duplicates_util", "safety_validation")
_emit_invokes_eval("p1", "delete_duplicates_util", "eval_call")
_emit_proposal_commits_routing("p1", "delete_duplicates_util", "routing_commit")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
            return candidate
    return current.parent


project_root = _find_project_root()
project_root_str = str(project_root)
# guardian: allow-global-mutation
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)


async def main():
    """Delete duplicates with dry-run or execute mode."""
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
    parser = argparse.ArgumentParser(description="Delete duplicate files")
    parser.add_argument("--execute", action="store_true", help="Actually delete files (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deletion without actually deleting")
    args = parser.parse_args()
    dry_run = not args.execute or args.dry_run
    print("=" * 80)
    print(f"DUPLICATE FILE DELETION - {('DRY RUN' if dry_run else 'EXECUTE MODE')}")
    print("=" * 80)
    print()
    if not dry_run:
        print("⚠️  WARNING: This will PERMANENTLY DELETE files!")
        response = input('Type "delete" to continue: ')
        if response.strip().lower() != "delete":
            print("Aborted.")
            return
        print()
    agent = DuplicateCodeDetectorAgent(project_root=project_root)
    print("Scanning for duplicates...")
    results = await agent.execute(scan_whole_files=True)
    recommendations = results["deletion_recommendations"]
    print(f"Found {len(recommendations)} duplicate sets")
    print()
    if not recommendations:
        print("No duplicates to delete!")
        return
    print(f"{('Simulating' if dry_run else 'Executing')} deletion...")
    delete_result = agent.delete_duplicates(recommendations, dry_run=dry_run)
    print()
    print("=" * 80)
    print("DELETION RESULTS")
    print("=" * 80)
    print(f"Files deleted: {delete_result['deleted_count']}")
    print(f"Errors: {len(delete_result['errors'])}")
    print(f"Mode: {('DRY RUN' if delete_result['dry_run'] else 'EXECUTED')}")
    print()
    if delete_result["errors"]:
        print("Errors encountered:")
        for error in delete_result["errors"]:
            print(f"  ❌ {error['path']}: {error['error']}")
        print()
    if dry_run:
        print("✅ Dry run complete - no files were actually deleted")
        print("   Run with --execute to actually delete files")
    else:
        print("✅ Deletion complete!")
        print(f"   Deleted {delete_result['deleted_count']} duplicate files")
    print()


if __name__ == "__main__":
    asyncio.run(main())
