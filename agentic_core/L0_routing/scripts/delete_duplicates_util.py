"""
Delete duplicate files based on scan results.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "delete_duplicates_util")
emit_determinism_digest("p0", "delete_duplicates_util")

_emit_dispatches_healing_run("p1", "delete_duplicates_util", "L0")
_emit_routes_through("p1", "delete_duplicates_util", "L0")
_emit_escalates_to_human("p1", "delete_duplicates_util", "L0")
_emit_reads_policy_state("p1", "delete_duplicates_util", "L0")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))


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
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
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
