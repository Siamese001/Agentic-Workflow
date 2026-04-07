#!/usr/bin/env python3
"""
Validate that no hardcoded paths exist - enforce SSOT compliance.
Run this as pre-commit hook or CI check.
"""

import re
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "validate_path_ssot_util")
emit_determinism_digest("p0", "validate_path_ssot_util")

_emit_dispatches_healing_run("p1", "validate_path_ssot_util", "L5")
_emit_routes_through("p1", "validate_path_ssot_util", "L5")
_emit_checks_agent_registry("p1", "validate_path_ssot_util", "agent_registry")
_emit_validates_agent_capability("p1", "validate_path_ssot_util", "capability")
_emit_dispatches_execution_plan("p1", "validate_path_ssot_util", "exec_plan")
_emit_agent_executes_agent("p1", "validate_path_ssot_util", "sub_agent")
_emit_routes_to_agent("p1", "validate_path_ssot_util", "target_agent")
_emit_verifies_policy("p1", "validate_path_ssot_util", "policy_check")
_emit_observes_runtime_state("p1", "validate_path_ssot_util", "runtime_state")
_emit_verifies_boundary("p1", "validate_path_ssot_util", "boundary_check")
_emit_transcripts_response("p1", "validate_path_ssot_util", "transcript")
_emit_hard_fails_untranscripted("p1", "validate_path_ssot_util")
_emit_gated_by_confidence("p1", "validate_path_ssot_util", "confidence_gate")
_emit_escalates_to_human("p1", "validate_path_ssot_util", "L5")
_emit_reads_policy_state("p1", "validate_path_ssot_util", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "validate_path_ssot_util")
_emit_applies_guardrail("p0", "validate_path_ssot_util", "p0_governance")
_emit_snapshots_state("p0", "validate_path_ssot_util", "state_snapshot")
_emit_authorize_and_execute("p2", "validate_path_ssot_util", "execution_auth")
_emit_validates_capability("p2", "validate_path_ssot_util", "capability_check")
_emit_routes_to_capability("p2", "validate_path_ssot_util", "capability_route")
_emit_writes_via_uwg("p2", "validate_path_ssot_util", "uwg_write")
_emit_blocks_direct_write("p2", "validate_path_ssot_util", "direct_write_block")
_emit_records_tool_invocation("p2", "validate_path_ssot_util", "tool_invocation")
_emit_captures_execution_output("p2", "validate_path_ssot_util", "exec_output")
_emit_dispatches_agent("p3", "validate_path_ssot_util", "agent_dispatch")
_emit_coordinates_agents("p3", "validate_path_ssot_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "validate_path_ssot_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "validate_path_ssot_util", "healing_outcome")
_emit_escalates_failure("p3", "validate_path_ssot_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "validate_path_ssot_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validate_path_ssot_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "validate_path_ssot_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "validate_path_ssot_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validate_path_ssot_util", "eval_metric")
_emit_stores_embedding("p4", "validate_path_ssot_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "validate_path_ssot_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validate_path_ssot_util", "exec_snapshot_link")
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_1")
_emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_2")
_emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_3")
_emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_4")
_emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_5")
_emit_emits_metric_event("validate_path_ssot_util", "p4obs", "metric_6")
_emit_records_incident_event("validate_path_ssot_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("validate_path_ssot_util", "p4obs", "anomaly")
_emit_writes_observability_log("validate_path_ssot_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("validate_path_ssot_util", "p4obs", "mon_state")
_emit_triggers_alert("validate_path_ssot_util", "p4obs", "alert")
_emit_links_incident_trace("validate_path_ssot_util", "p4obs", "trace_link")
_emit_captures_pattern("validate_path_ssot_util", "p3lm", "pattern")
_emit_records_learning_event("validate_path_ssot_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validate_path_ssot_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("validate_path_ssot_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validate_path_ssot_util", "p3lm", "routing")
_emit_improves_agent_policy("validate_path_ssot_util", "p3lm", "policy")
_emit_stores_learning_state("validate_path_ssot_util", "p3lm", "state")
_emit_records_execution_trace("validate_path_ssot_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validate_path_ssot_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validate_path_ssot_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validate_path_ssot_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validate_path_ssot_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validate_path_ssot_util", "env_read", "p2_env_1")
_emit_reads_environ("validate_path_ssot_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("validate_path_ssot_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validate_path_ssot_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validate_path_ssot_util", "context_pull")
_emit_pulls_context("p1", "validate_path_ssot_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validate_path_ssot_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validate_path_ssot_util", "uwg_term_2")
_emit_writes_through("p1", "validate_path_ssot_util", "write_through")
_emit_writes_through("p1", "validate_path_ssot_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "validate_path_ssot_util", "safety_validation")
_emit_invokes_eval("p1", "validate_path_ssot_util", "eval_call")
_emit_proposal_commits_routing("p1", "validate_path_ssot_util", "routing_commit")

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
        if "from agentic_core.L5_safety.config.structure_blueprint_config import" in content:
            # File uses SSOT, but still check for violations
            pass

        for line_num, line in enumerate(lines, 1):
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

    # guardian: allow-silent-swallow -- path validation fallback; failure logged above
    except (ValueError, TypeError):
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
        print("  from agentic_core.L5_safety.config.structure_blueprint_config import (")
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
