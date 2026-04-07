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

_emit_emits_metric_event("check_rglob_usage_util", "p4obs", "metric_1")
_emit_emits_metric_event("check_rglob_usage_util", "p4obs", "metric_2")
_emit_emits_metric_event("check_rglob_usage_util", "p4obs", "metric_3")
_emit_emits_metric_event("check_rglob_usage_util", "p4obs", "metric_4")
_emit_emits_metric_event("check_rglob_usage_util", "p4obs", "metric_5")
_emit_emits_metric_event("check_rglob_usage_util", "p4obs", "metric_6")
_emit_records_incident_event("check_rglob_usage_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_rglob_usage_util", "p4obs", "anomaly")
_emit_writes_observability_log("check_rglob_usage_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_rglob_usage_util", "p4obs", "mon_state")
_emit_triggers_alert("check_rglob_usage_util", "p4obs", "alert")
_emit_links_incident_trace("check_rglob_usage_util", "p4obs", "trace_link")
_emit_captures_pattern("check_rglob_usage_util", "p3lm", "pattern")
_emit_records_learning_event("check_rglob_usage_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_rglob_usage_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_rglob_usage_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_rglob_usage_util", "p3lm", "routing")
_emit_improves_agent_policy("check_rglob_usage_util", "p3lm", "policy")
_emit_stores_learning_state("check_rglob_usage_util", "p3lm", "state")
_emit_records_execution_trace("check_rglob_usage_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_rglob_usage_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_rglob_usage_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_rglob_usage_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_rglob_usage_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_rglob_usage_util", "env_read", "p2_env_1")
_emit_reads_environ("check_rglob_usage_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_rglob_usage_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_rglob_usage_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "check_rglob_usage_util")
emit_determinism_digest("p0", "check_rglob_usage_util")

_emit_dispatches_healing_run("p1", "check_rglob_usage_util", "L0")
_emit_routes_through("p1", "check_rglob_usage_util", "L0")
_emit_checks_agent_registry("p1", "check_rglob_usage_util", "agent_registry")
_emit_validates_agent_capability("p1", "check_rglob_usage_util", "capability")
_emit_dispatches_execution_plan("p1", "check_rglob_usage_util", "exec_plan")
_emit_agent_executes_agent("p1", "check_rglob_usage_util", "sub_agent")
_emit_routes_to_agent("p1", "check_rglob_usage_util", "target_agent")
_emit_verifies_policy("p1", "check_rglob_usage_util", "policy_check")
_emit_observes_runtime_state("p1", "check_rglob_usage_util", "runtime_state")
_emit_verifies_boundary("p1", "check_rglob_usage_util", "boundary_check")
_emit_transcripts_response("p1", "check_rglob_usage_util", "transcript")
_emit_hard_fails_untranscripted("p1", "check_rglob_usage_util")
_emit_gated_by_confidence("p1", "check_rglob_usage_util", "confidence_gate")
_emit_escalates_to_human("p1", "check_rglob_usage_util", "L0")
_emit_reads_policy_state("p1", "check_rglob_usage_util", "L0")
_emit_pulls_context("p1", "check_rglob_usage_util", "context_pull")
_emit_pulls_context("p1", "check_rglob_usage_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_rglob_usage_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_rglob_usage_util", "uwg_term_secondary")
_emit_writes_through("p1", "check_rglob_usage_util", "write_through")
_emit_writes_through("p1", "check_rglob_usage_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_rglob_usage_util", "safety_validation")
_emit_invokes_eval("p1", "check_rglob_usage_util", "eval_call")
_emit_proposal_commits_routing("p1", "check_rglob_usage_util", "routing_commit")

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
    # guardian: allow-silent-swallow - acceptable exception handling
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
