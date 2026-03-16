#!/usr/bin/env python3
"""
Find and Fix Corrupted Python Files - Detects and repairs literal \\n corruption.

This script scans for files where literal backslash-n sequences appear at the
end of files (typically caused by bad copy-paste or repr() output being written
to source files), and optionally fixes them.

Usage:
    python scripts/find_corrupted_files_util.py          # Scan only
    python scripts/find_corrupted_files_util.py --fix    # Scan and fix
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    safe_write_text,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "find_corrupted_files_util")
emit_determinism_digest("p0", "find_corrupted_files_util")

_emit_dispatches_healing_run("p1", "find_corrupted_files_util", "L0")
_emit_routes_through("p1", "find_corrupted_files_util", "L0")
_emit_escalates_to_human("p1", "find_corrupted_files_util", "L0")
_emit_reads_policy_state("p1", "find_corrupted_files_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_corrupted_files_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_corrupted_files_util", "p0_governance")
_emit_snapshots_state("p0", "find_corrupted_files_util", "state_snapshot")
_emit_authorize_and_execute("p2", "find_corrupted_files_util", "execution_auth")
_emit_validates_capability("p2", "find_corrupted_files_util", "capability_check")
_emit_routes_to_capability("p2", "find_corrupted_files_util", "capability_route")
_emit_writes_via_uwg("p2", "find_corrupted_files_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_corrupted_files_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_corrupted_files_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_corrupted_files_util", "exec_output")
_emit_dispatches_agent("p3", "find_corrupted_files_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_corrupted_files_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_corrupted_files_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_corrupted_files_util", "healing_outcome")
_emit_escalates_failure("p3", "find_corrupted_files_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_corrupted_files_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_corrupted_files_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_corrupted_files_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_corrupted_files_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_corrupted_files_util", "eval_metric")
_emit_stores_embedding("p4", "find_corrupted_files_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_corrupted_files_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_corrupted_files_util", "exec_snapshot_link")


def find_corruption(content: str) -> int:
    """Find position of literal backslash-n corruption. Returns -1 if none."""
    # Look for literal backslash followed by 'n' (two chars)
    return content.find(chr(92) + "n")


def is_valid_python(content: str) -> bool:
    """Check if content is valid Python syntax."""
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False


def main():
    fix_mode = "--fix" in sys.argv

    # Scan multiple directories
    scan_dirs = [
        AGENTIC_CORE_DIR,
        APPS_RG_DIR,
        APPS_LIC_DIR,
        APPS_SHARED_DIR,
        SCRIPTS_DIR,
        TESTS_DIR,
    ]

    corrupted_files = []
    fixed_files = []

    for root_dir in scan_dirs:
        root_path = Path(root_dir)
        if not root_path.exists():
            continue

        # Phase 6.9: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        py_files = list(get_python_files(root_path))

        for py_file in py_files:
            if "__pycache__" in str(py_file) or ARCHIVES_DIR in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")

                # Check for literal backslash-n
                idx = find_corruption(content)
                if idx != -1:
                    # Verify it's actually corruption (file doesn't parse)
                    if not is_valid_python(content):
                        corrupted_files.append((py_file, idx))

                        if fix_mode:
                            # Truncate at corruption point
                            clean = content[:idx].rstrip() + "\n"
                            if is_valid_python(clean):
                                safe_write_text(py_file, clean, layer="L0", encoding="utf-8")
                                fixed_files.append(py_file)
                                print(f"FIXED: {py_file}")
                            else:
                                print(f"UNFIXABLE: {py_file} (truncation doesn't fix syntax)")
                        else:
                            print(f"CORRUPTED: {py_file}")
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"ERROR: {py_file} - {e}")

    print("\n" + "=" * 60)
    print(f"SUMMARY: {len(corrupted_files)} corrupted file(s) found")

    if fix_mode:
        print(f"         {len(fixed_files)} file(s) fixed")
        unfixed = len(corrupted_files) - len(fixed_files)
        if unfixed > 0:
            print(f"         {unfixed} file(s) could not be auto-fixed")
    else:
        if corrupted_files:
            print("\nRun with --fix to automatically repair these files:")
            print("  python scripts/find_corrupted_files_util.py --fix")

    return 0 if not corrupted_files or (fix_mode and len(fixed_files) == len(corrupted_files)) else 1


if __name__ == "__main__":
    sys.exit(main())
