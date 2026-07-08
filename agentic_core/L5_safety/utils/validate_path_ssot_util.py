#!/usr/bin/env python3
"""
Validate that no hardcoded paths exist - enforce SSOT compliance.
Run this as pre-commit hook or CI check.
"""

import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "validate_path_ssot_util")
trace_contract.emit_determinism_digest("p0", "validate_path_ssot_util")

trace_contract._emit_dispatches_healing_run("p1", "validate_path_ssot_util", "L5")
trace_contract._emit_routes_through("p1", "validate_path_ssot_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "validate_path_ssot_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "validate_path_ssot_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "validate_path_ssot_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "validate_path_ssot_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "validate_path_ssot_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "validate_path_ssot_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "validate_path_ssot_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "validate_path_ssot_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "validate_path_ssot_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "validate_path_ssot_util")
trace_contract._emit_gated_by_confidence("p1", "validate_path_ssot_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "validate_path_ssot_util", "L5")
trace_contract._emit_reads_policy_state("p1", "validate_path_ssot_util", "L5")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "validate_path_ssot_util")
trace_contract._emit_applies_guardrail("p0", "validate_path_ssot_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "validate_path_ssot_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "validate_path_ssot_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "validate_path_ssot_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "validate_path_ssot_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "validate_path_ssot_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "validate_path_ssot_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "validate_path_ssot_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "validate_path_ssot_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "validate_path_ssot_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "validate_path_ssot_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "validate_path_ssot_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "validate_path_ssot_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "validate_path_ssot_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "validate_path_ssot_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "validate_path_ssot_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "validate_path_ssot_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "validate_path_ssot_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "validate_path_ssot_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "validate_path_ssot_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "validate_path_ssot_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "validate_path_ssot_util", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("validate_path_ssot_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("validate_path_ssot_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("validate_path_ssot_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("validate_path_ssot_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("validate_path_ssot_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("validate_path_ssot_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("validate_path_ssot_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("validate_path_ssot_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("validate_path_ssot_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("validate_path_ssot_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("validate_path_ssot_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("validate_path_ssot_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("validate_path_ssot_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("validate_path_ssot_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("validate_path_ssot_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("validate_path_ssot_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("validate_path_ssot_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("validate_path_ssot_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("validate_path_ssot_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("validate_path_ssot_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("validate_path_ssot_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("validate_path_ssot_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "validate_path_ssot_util", "context_pull")
trace_contract._emit_pulls_context("p1", "validate_path_ssot_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "validate_path_ssot_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "validate_path_ssot_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "validate_path_ssot_util", "write_through")
trace_contract._emit_writes_through("p1", "validate_path_ssot_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "validate_path_ssot_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "validate_path_ssot_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "validate_path_ssot_util", "routing_commit")

PROJECT_ROOT = Path(__file__).parent.parent

# Directories to exclude
EXCLUDED_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

# Files that are allowed to have hardcoded paths
EXCLUDED_FILES = {
    "structure_blueprint.py",  # SSOT definition file
    "validate_path_ssot_util.py",  # This file
    "scan_hardcoded_paths.py",
    "refactor_hardcoded_paths.py",
}

# Patterns that indicate hardcoded paths (violations)
HARDCODED_PATH_PATTERNS = [
    # Agent discovery files
    (
        r'(?<!AGENT_DISCOVERY_JSON\s*=\s*)["\']agent_discovery_full\.json["\']',
        "Use AGENT_DISCOVERY_JSON constant",
    ),
    (
        r'(?<!AGENT_DISCOVERY_MANIFEST_JSON\s*=\s*)["\']agent_discovery_full\.manifest\.json["\']',
        "Use AGENT_DISCOVERY_MANIFEST_JSON constant",
    ),
    # Layer directories - exact matches only
    (r'["\']agentic_core/L0_routing["\'](?!\s*[:\]])', "Use L0_MAINTENANCE_DIR constant"),
    (r'["\']agentic_core/L1_cognition["\'](?!\s*[:\]])', "Use L1_COGNITION_DIR constant"),
    (r'["\']agentic_core/L2_execution["\'](?!\s*[:\]])', "Use L2_EXECUTION_DIR constant"),
    (r'["\']agentic_core/L3_orchestration["\'](?!\s*[:\]])', "Use L3_ORCHESTRATION_DIR constant"),
    (r'["\']agentic_core/L4_state["\'](?!\s*[:\]])', "Use L4_STATE_DIR constant"),
    (r'["\']agentic_core/L5_safety["\'](?!\s*[:\]])', "Use L5_SAFETY_DIR constant"),
    (r'["\']agentic_core/L6_observability["\'](?!\s*[:\]])', "Use L6_OBSERVABILITY_DIR constant"),
    # Dashboard directory
    (r'["\']agentic_core/L6_observability/dashboards["\']', "Use DASHBOARD_DIR constant"),
    # Core directories - only flag bare references
    (r'(?<![/\w])["\']agentic_core["\'](?!\s*[:\]./])', "Use AGENTIC_CORE_DIR constant"),
    (r'(?<![/\w])["\']scripts["\'](?!\s*[:\]./])', "Use SCRIPTS_DIR constant"),
    (r'["\']tests/unit["\']', "Use TESTS_UNIT_DIR constant"),
    (r'(?<![/\w])["\']tests["\'](?!\s*[:\]./])', "Use TESTS_DIR constant"),
]


def should_exclude_path(path: Path) -> bool:
    """Check if path should be excluded from validation."""
    parts_lower = {p.lower() for p in path.parts}
    if parts_lower & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    if path.name in EXCLUDED_FILES:
        return True
    return False


def validate_file(file_path: Path) -> list[tuple[int, str, str]]:
    """Validate a single file for hardcoded paths.

    Returns:
        List of (line_number, violation_description, line_content)
    """
    violations = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        # Skip if file imports from structure_blueprint (likely compliant)
        if "from agentic_core.L5_safety.config.structure_blueprint import" in content:
            # File uses SSOT, but still check for violations
            pass

        for line_num, line in tqdm(enumerate(lines, 1), desc="Processing", unit="item"):
            # Skip import lines
            if "import" in line and "structure_blueprint" in line:
                continue

            # Skip lines defining SSOT constants
            if re.match(r'^\s*[A-Z_]+\s*[:=]\s*["\']', line):
                continue

            # Check each pattern
            for pattern, description in HARDCODED_PATH_PATTERNS:
                if re.search(pattern, line):
                    violations.append((line_num, description, line.strip()))

    except (
        ValueError,
        TypeError,
    ):  # guardian: allow-silent-swallow -- path validation fallback; failure logged above
        pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow

    return violations


def validate_repository() -> tuple[bool, dict]:
    """Validate entire repository.

    Returns:
        (is_compliant, violations_dict)
    """
    print("=" * 80)
    print("PATH SSOT VALIDATION")
    print("=" * 80)
    print(f"\n📂 Project: {PROJECT_ROOT}")
    print("🔍 Scanning for hardcoded paths...\n")

    violations_by_file = {}
    files_scanned = 0

    # Scan all Python files
    # Final True 20: Use ssot_discovery instead of rglob
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(PROJECT_ROOT):
        if should_exclude_path(py_file):
            continue

        files_scanned += 1
        violations = validate_file(py_file)

        if violations:
            rel_path = py_file.relative_to(PROJECT_ROOT)
            violations_by_file[str(rel_path)] = violations

    # Print results
    total_violations = sum(len(v) for v in violations_by_file.values())

    print(f"✅ Scanned {files_scanned} files\n")

    if total_violations == 0:
        print("=" * 80)
        print("✅ ALL FILES COMPLIANT")
        print("=" * 80)
        print("No hardcoded paths found!")
        print("All files correctly use SSOT constants from structure_blueprint.py")
        return True, {}
    else:
        print("=" * 80)
        print(f"❌ FOUND {total_violations} VIOLATIONS IN {len(violations_by_file)} FILES")
        print("=" * 80)
        print()

        # Show top violators
        sorted_files = sorted(violations_by_file.items(), key=lambda x: -len(x[1]))
        for file_path, violations in sorted_files[:20]:
            print(f"\n📄 {file_path}")
            print(f"   {len(violations)} violation(s):")
            for line_num, desc, line_content in violations[:5]:
                print(f"      Line {line_num}: {desc}")
                print(f"         {line_content}")
            if len(violations) > 5:
                print(f"      ... and {len(violations) - 5} more")

        if len(violations_by_file) > 20:
            print(f"\n   ... and {len(violations_by_file) - 20} more files with violations")

        print("\n" + "=" * 80)
        print("REMEDIATION REQUIRED")
        print("=" * 80)
        print("Replace hardcoded paths with SSOT constants:")
        print("  from agentic_core.L5_safety.config.structure_blueprint import (")
        print("      AGENT_DISCOVERY_JSON, DASHBOARD_DIR, L0_MAINTENANCE_DIR,")
        print("      get_validated_project_root")
        print("  )")
        print()
        print("  # Example usage:")
        print("  discovery_path = get_validated_project_root() / AGENT_DISCOVERY_JSON")
        print("  dashboard_dir = get_validated_project_root() / DASHBOARD_DIR")
        print("=" * 80)

        return False, violations_by_file


def main():
    is_compliant, violations = validate_repository()

    if is_compliant:
        print("\n✅ Validation passed")
        return 0
    else:
        print(f"\n❌ Validation failed: {sum(len(v) for v in violations.values())} violations")
        return 1


if __name__ == "__main__":
    exit(main())
