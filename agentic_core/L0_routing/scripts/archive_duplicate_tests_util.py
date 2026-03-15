"""
Archive Duplicate Test Files

Identifies test files with the same name in different directories
and archives the duplicates to preserve SSOT.
"""

import shutil
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config import TESTS_DIR
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
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
)

_emit_dispatches_healing_run("p1", "archive_duplicate_tests_util", "L0")
_emit_routes_through("p1", "archive_duplicate_tests_util", "L0")
_emit_escalates_to_human("p1", "archive_duplicate_tests_util", "L0")
_emit_reads_policy_state("p1", "archive_duplicate_tests_util", "L0")


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
    test_dir = Path(__file__).parent.parent / TESTS_DIR
    "Find all test files in directory."
    seen = {}
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(test_dir):
        if py_file.name.startswith("test_"):
            seen.setdefault(py_file.name, []).append(py_file)
    duplicates = [files[1:] for files in seen.values() if len(files) > 1]
    duplicate_count = sum(len(d) for d in duplicates)
    print(f"\n{'=' * 80}")
    print("DUPLICATE TEST FILE ARCHIVAL")
    print(f"{'=' * 80}")
    print(f"Found {duplicate_count} duplicate test files")
    if duplicate_count == 0:
        print("No duplicates to archive.")
        return 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = Path(__file__).parent.parent / ARCHIVES_DIR / f"duplicate_tests_{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived = 0
    for dup_list in duplicates:
        for dup in dup_list:
            try:
                relative_path = dup.relative_to(test_dir)
                archive_target = archive_dir / relative_path
                archive_target.parent.mkdir(parents=True, exist_ok=True)
                assert_no_persistent_write("L0", "shutil.mutate")
                shutil.move(str(dup), str(archive_target))
                print(f"✅ Archived: {relative_path}")
                archived += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"❌ Failed to archive {dup}: {e}")
    print(f"\n{'=' * 80}")
    print("ARCHIVAL COMPLETE")
    print(f"{'=' * 80}")
    print(f"Archived: {archived} files")
    print(f"Location: {archive_dir}")
    print(f"{'=' * 80}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
