"""
CI Guard: rglob/glob Usage Checker

Phase 4.1 CI Enforcement: This script counts un-guarded rglob/glob calls
to prevent performance regression. It should be run in CI/CD pipelines.

Usage:
    python scripts/check_rglob_usage_util.py

Exit Codes:
    0: Pass - rglob count is within limits
    1: Fail - rglob count exceeds maximum allowed

Author: Cascade
Date: January 19, 2026
Phase: 4.1 - Scaled Refactoring & CI Enforcement
"""

import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
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

emit_replay_key("p0", "check_rglob_usage_util")
emit_determinism_digest("p0", "check_rglob_usage_util")

_emit_dispatches_healing_run("p1", "check_rglob_usage_util", "L0")
_emit_routes_through("p1", "check_rglob_usage_util", "L0")
_emit_escalates_to_human("p1", "check_rglob_usage_util", "L0")
_emit_reads_policy_state("p1", "check_rglob_usage_util", "L0")

_emit_records_execution_trace("p0", "evidence", "check_rglob_usage_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "check_rglob_usage_util", "p0_governance")
_emit_snapshots_state("p0", "check_rglob_usage_util", "state_snapshot")
_emit_authorize_and_execute("p2", "check_rglob_usage_util", "execution_auth")
_emit_validates_capability("p2", "check_rglob_usage_util", "capability_check")
_emit_routes_to_capability("p2", "check_rglob_usage_util", "capability_route")
_emit_writes_via_uwg("p2", "check_rglob_usage_util", "uwg_write")
_emit_blocks_direct_write("p2", "check_rglob_usage_util", "direct_write_block")
_emit_records_tool_invocation("p2", "check_rglob_usage_util", "tool_invocation")
_emit_captures_execution_output("p2", "check_rglob_usage_util", "exec_output")
_emit_dispatches_agent("p3", "check_rglob_usage_util", "agent_dispatch")
_emit_coordinates_agents("p3", "check_rglob_usage_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_rglob_usage_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_rglob_usage_util", "healing_outcome")
_emit_escalates_failure("p3", "check_rglob_usage_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_rglob_usage_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_rglob_usage_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_rglob_usage_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_rglob_usage_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_rglob_usage_util", "eval_metric")
_emit_stores_embedding("p4", "check_rglob_usage_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_rglob_usage_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_rglob_usage_util", "exec_snapshot_link")

# configuration
# guardian: allow-magic-config
MAX_ALLOWED_RGLOB = 260  # Phase 6: Temporary ceiling, target is 50

# Files to exclude from the count (these are the utilities that wrap rglob)
EXCLUDED_FILES = {
    "ssot_discovery.py",
    "scan_guard.py",
    "check_rglob_usage_util.py",  # This script
}

# Directories to exclude
EXCLUDED_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def count_rglob_in_file(file_path: Path) -> int:
    """
    Count rglob/glob calls in a single file.

    Args:
        file_path: Path to the Python file

    Returns:
        Number of rglob/glob calls found
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0

    # Pattern to match .rglob( and .glob( calls
    rglob_pattern = r"\.rglob\s*\("
    glob_pattern = r"\.glob\s*\("

    rglob_count = len(re.findall(rglob_pattern, content))
    glob_count = len(re.findall(glob_pattern, content))

    return rglob_count + glob_count


def should_exclude_path(file_path: Path) -> bool:
    """Check if a file path should be excluded from counting."""
    # Check if file is in excluded list
    if file_path.name in EXCLUDED_FILES:
        return True

    # Check if any parent directory is excluded
    for part in file_path.parts:
        if part in EXCLUDED_DIRS:
            return True

    return False


def scan_for_rglob_usage(root_dir: Path) -> tuple[int, list[dict]]:
    """
    Scan directory for rglob/glob usage.

    Args:
        root_dir: Root directory to scan

    Returns:
        Tuple of (total_count, list of offender details)
    """
    total_count = 0
    offenders = []

    for py_file in root_dir.rglob("*.py"):
        # Skip excluded paths
        if should_exclude_path(py_file):
            continue

        count = count_rglob_in_file(py_file)
        if count > 0:
            offenders.append({"file": str(py_file.relative_to(root_dir)), "count": count})
            total_count += count

    # Sort by count descending
    offenders.sort(key=lambda x: x["count"], reverse=True)

    return total_count, offenders


def main():
    """Main entry point for CI check."""
    print("=" * 60)
    print("CI GUARD: rglob/glob Usage Check")
    print("=" * 60)

    # Find project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    agentic_core = project_root / AGENTIC_CORE_DIR

    if not agentic_core.exists():
        print(f"ERROR: agentic_core directory not found at {agentic_core}")
        sys.exit(1)

    print(f"Scanning: {agentic_core}")
    print(f"Maximum allowed: {MAX_ALLOWED_RGLOB}")
    print()

    # Scan for rglob usage
    total_count, offenders = scan_for_rglob_usage(agentic_core)

    # Report results
    print(f"Total rglob/glob calls: {total_count}")
    print(f"Files with rglob/glob: {len(offenders)}")
    print()

    # Show top offenders
    if offenders:
        print("Top 10 Offenders:")
        for i, offender in enumerate(offenders[:10], 1):
            print(f"  {i:2}. {offender['file']}: {offender['count']} calls")
        print()

    # Check against threshold
    if total_count > MAX_ALLOWED_RGLOB:
        print("=" * 60)
        print(f"❌ FAIL: Count ({total_count}) exceeds maximum ({MAX_ALLOWED_RGLOB})")
        print("=" * 60)
        print()
        print("Action Required:")
        print("  1. Refactor files to use ssot_discovery.get_python_files()")
        print("  2. Or use scan_guard.guarded_rglob() for tracking")
        print()
        sys.exit(1)
    else:
        print("=" * 60)
        print(f"✅ PASS: Count ({total_count}) is within limit ({MAX_ALLOWED_RGLOB})")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
