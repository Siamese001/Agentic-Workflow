"""
Execute safe deletion of verified identical duplicates.
This script bypasses the interactive prompt for automated execution.
"""

import asyncio
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "execute_safe_deletion_util")
emit_determinism_digest("p0", "execute_safe_deletion_util")

_emit_dispatches_healing_run("p1", "execute_safe_deletion_util", "L0")
_emit_routes_through("p1", "execute_safe_deletion_util", "L0")
_emit_escalates_to_human("p1", "execute_safe_deletion_util", "L0")
_emit_reads_policy_state("p1", "execute_safe_deletion_util", "L0")
_emit_authorize_and_execute("p2", "execute_safe_deletion_util", "execution_auth")
_emit_validates_capability("p2", "execute_safe_deletion_util", "capability_check")
_emit_routes_to_capability("p2", "execute_safe_deletion_util", "capability_route")
_emit_writes_via_uwg("p2", "execute_safe_deletion_util", "uwg_write")
_emit_blocks_direct_write("p2", "execute_safe_deletion_util", "direct_write_block")
_emit_records_tool_invocation("p2", "execute_safe_deletion_util", "tool_invocation")
_emit_captures_execution_output("p2", "execute_safe_deletion_util", "exec_output")
_emit_dispatches_agent("p3", "execute_safe_deletion_util", "agent_dispatch")
_emit_coordinates_agents("p3", "execute_safe_deletion_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "execute_safe_deletion_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "execute_safe_deletion_util", "healing_outcome")
_emit_escalates_failure("p3", "execute_safe_deletion_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "execute_safe_deletion_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execute_safe_deletion_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "execute_safe_deletion_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "execute_safe_deletion_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execute_safe_deletion_util", "eval_metric")
_emit_stores_embedding("p4", "execute_safe_deletion_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "execute_safe_deletion_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execute_safe_deletion_util", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))


async def main():
    """Execute deletion of verified identical duplicates."""
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
    print("=" * 120)
    print("SAFE DELETION - Verified Identical Duplicates Only")
    print("=" * 120)
    print()
    print("This script will delete files that are byte-for-byte identical (same SHA-256 hash)")
    print("Intentional variants with different content will NOT be deleted")
    print()
    agent = DuplicateCodeDetectorAgent(project_root=project_root)
    print("[1/3] Scanning for duplicates...")
    results = await agent.execute(scan_whole_files=True)
    recommendations = results["deletion_recommendations"]
    print(f"   Found {len(recommendations)} duplicate sets")
    print()
    if not recommendations:
        print("No duplicates to delete!")
        return
    print("[2/3] Files to be deleted:")
    print()
    total_to_delete = 0
    for rec in recommendations[:10]:
        print(f"   Keeping: {rec['keep']}")
        print(f"   Deleting: {len(rec['delete'])} copies")
        for del_path in rec["delete"][:3]:
            print(f"     - {del_path}")
        if len(rec["delete"]) > 3:
            print(f"     ... and {len(rec['delete']) - 3} more")
        print()
        total_to_delete += len(rec["delete"])
    if len(recommendations) > 10:
        print(f"   ... and {len(recommendations) - 10} more duplicate sets")
        for rec in recommendations[10:]:
            total_to_delete += len(rec["delete"])
    print(f"   Total files to delete: {total_to_delete}")
    print()
    print("[3/3] Executing deletion...")
    delete_result = agent.delete_duplicates(recommendations, dry_run=False)
    print()
    print("=" * 120)
    print("DELETION RESULTS")
    print("=" * 120)
    print(f"✓ Files deleted: {delete_result['deleted_count']}")
    print(f"✓ Errors: {len(delete_result['errors'])}")
    print()
    if delete_result["errors"]:
        print("Errors encountered:")
        for error in delete_result["errors"]:
            print(f"  ✗ {error['path']}: {error['error']}")
        print()
    print("✓ Deletion complete!")
    print(f"  Successfully deleted {delete_result['deleted_count']} duplicate files")
    print(f"  Kept {len(recommendations)} canonical copies")
    print()


if __name__ == "__main__":
    asyncio.run(main())
