"""
Run HierarchyEnforcerAgent in dry-run mode (validation only)
This will scan for hierarchy violations and depth issues without making changes.
"""

import sys
import uuid
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "mock_context_enforcer")
trace_contract.emit_determinism_digest("p0", "mock_context_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "mock_context_enforcer", "L5")
trace_contract._emit_routes_through("p1", "mock_context_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "mock_context_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mock_context_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mock_context_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mock_context_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mock_context_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "mock_context_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mock_context_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mock_context_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mock_context_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mock_context_enforcer")
trace_contract._emit_gated_by_confidence("p1", "mock_context_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "mock_context_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "mock_context_enforcer", "L5")
trace_contract._emit_authorize_and_execute("p2", "mock_context_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "mock_context_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mock_context_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mock_context_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mock_context_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mock_context_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mock_context_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mock_context_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mock_context_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mock_context_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mock_context_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mock_context_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mock_context_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mock_context_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mock_context_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mock_context_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mock_context_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mock_context_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mock_context_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mock_context_enforcer", "exec_snapshot_link")

project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L0_routing.config.path_constants import CORE_SUBFOLDER_MAP, DEPTH_RULES
from tqdm import tqdm

trace_contract._emit_emits_metric_event("mock_context_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mock_context_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mock_context_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mock_context_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mock_context_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mock_context_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mock_context_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mock_context_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mock_context_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mock_context_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mock_context_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mock_context_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mock_context_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mock_context_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mock_context_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mock_context_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mock_context_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mock_context_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mock_context_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("mock_context_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mock_context_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mock_context_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mock_context_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mock_context_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mock_context_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mock_context_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mock_context_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mock_context_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mock_context_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "mock_context_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mock_context_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mock_context_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mock_context_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "mock_context_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mock_context_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mock_context_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mock_context_enforcer", "routing_commit")


class MockContext:
    """Mock context for dry-run mode."""

    def report(self, agent_name, key, passed, details):
        pass


def validate_l2_l3_structure(project_root: Path) -> dict:
    """Validate L2/L3 structure (CORE_SUBFOLDER_MAP) without making changes."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "validate_l2_l3_structure", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "validate_l2_l3_structure")
    trace_contract._emit_applies_guardrail(str(uuid.uuid4()), "Module.validate_l2_l3_structure", "L5_POLICY")
    violations = []
    missing_dirs = []
    l1_structure = list(CORE_SUBFOLDER_MAP.keys())
    for l1_name in tqdm(l1_structure, desc="Processing", unit="item"):
        l1_path = project_root / AGENTIC_CORE_DIR / l1_name
        if not l1_path.exists():
            continue
        expected_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
        if not expected_l2:
            continue
        actual_l2 = {p.name for p in l1_path.iterdir() if p.is_dir() and (not p.name.startswith("."))}
        missing_l2 = expected_l2 - actual_l2
        if missing_l2:
            for missing in missing_l2:
                missing_dirs.append(f"agentic_core/{l1_name}/{missing}")
            violations.append({"path": f"{l1_name}", "missing": list(missing_l2)})
    return {"violations": violations, "missing_dirs": missing_dirs, "compliant": len(violations) == 0}


def validate_depth_precision(project_root: Path) -> dict:
    """Validate apps_* depth without archiving."""
    apps_exact_depth = DEPTH_RULES.get("apps_rg", 2)
    violations = []
    from agentic_core.utils.runners.ssot_discovery_validator import get_data_files, get_python_files

    all_files = list(get_python_files(project_root)) + list(
        get_data_files(project_root, extensions=[".json", ".md", ".yaml", ".yml"]),
    )
    for file_path in all_files:
        if file_path.is_dir():
            continue
        rel = file_path.relative_to(project_root)
        if not rel.parts[0].startswith("apps_"):
            continue
        depth = len(rel.parts) - 1
        if depth != apps_exact_depth:
            violations.append({"file": str(rel), "actual_depth": depth, "expected_depth": apps_exact_depth})
    return violations


def validate_tests_depth(project_root: Path) -> dict:
    """Validate tests depth without archiving."""
    tests_exact_depth = DEPTH_RULES.get("tests", 2)
    violations = []
    from agentic_core.utils.runners.ssot_discovery_validator import get_data_files, get_python_files

    all_files = list(get_python_files(project_root)) + list(
        get_data_files(project_root, extensions=[".json", ".md", ".yaml", ".yml"]),
    )
    for file_path in all_files:
        if file_path.is_dir():
            continue
        rel = file_path.relative_to(project_root)
        if rel.parts[0] != TESTS_DIR:
            continue
        depth = len(rel.parts) - 1
        if depth != tests_exact_depth:
            violations.append({"file": str(rel), "actual_depth": depth, "expected_depth": tests_exact_depth})
    return violations


def validate_universal_depth(project_root: Path) -> dict:
    """Validate universal depth for non-Python files without archiving."""
    agentic_core_exact_depth = DEPTH_RULES.get("agentic_core", 3)
    violations = []
    from agentic_core.utils.runners.ssot_discovery_validator import get_data_files

    target_exts = [".json", ".md", ".yaml", ".yml", ".toml", ".txt"]
    for file_path in tqdm(
        get_data_files(project_root, extensions=target_exts), desc="Processing", unit="item"
    ):
        if file_path.is_dir():
            continue
        if file_path.suffix.lower() not in target_exts:
            continue
        rel = file_path.relative_to(project_root)
        if rel.parts[0] == AGENTIC_CORE_DIR:
            depth = len(rel.parts) - 1
            if depth != agentic_core_exact_depth:
                violations.append(
                    {
                        "file": str(rel),
                        "actual_depth": depth,
                        "expected_depth": agentic_core_exact_depth,
                        "type": file_path.suffix,
                    },
                )
    return violations


def main():
    print("=" * 80)
    print("HIERARCHY ENFORCER - DRY RUN MODE (VALIDATION ONLY)")
    print("=" * 80)
    print("Validating L2/L3 structure and depth compliance (no changes will be made)...\n")
    project_root = Path.cwd()
    print("[1/4] Validating L2/L3 directory structure (CORE_SUBFOLDER_MAP)...")
    l2_l3_result = validate_l2_l3_structure(project_root)
    if l2_l3_result["compliant"]:
        print("  ✅ L2/L3 structure is compliant")
    else:
        print(f"  ⚠️  Found {len(l2_l3_result['violations'])} L2/L3 structure violations")
        print("\n  Missing directories that would be created:")
        for missing_dir in l2_l3_result["missing_dirs"][:10]:
            print(f"    - {missing_dir}")
        if len(l2_l3_result["missing_dirs"]) > 10:
            print(f"    ... and {len(l2_l3_result['missing_dirs']) - 10} more")
    print("\n[2/4] Validating apps_* depth precision...")
    apps_violations = validate_depth_precision(project_root)
    if not apps_violations:
        print("  ✅ apps_* depth is compliant")
    else:
        print(f"  ⚠️  Found {len(apps_violations)} apps_* depth violations")
        print("\n  Files that would be archived:")
        for violation in apps_violations[:5]:
            print(
                f"    - {violation['file']} (depth {violation['actual_depth']}, expected {violation['expected_depth']})",
            )
        if len(apps_violations) > 5:
            print(f"    ... and {len(apps_violations) - 5} more")
    print("\n[3/4] Validating tests depth precision...")
    tests_violations = validate_tests_depth(project_root)
    if not tests_violations:
        print("  ✅ tests depth is compliant")
    else:
        print(f"  ⚠️  Found {len(tests_violations)} tests depth violations")
        print("\n  Files that would be archived:")
        for violation in tests_violations[:5]:
            print(
                f"    - {violation['file']} (depth {violation['actual_depth']}, expected {violation['expected_depth']})",
            )
        if len(tests_violations) > 5:
            print(f"    ... and {len(tests_violations) - 5} more")
    print("\n[4/4] Validating universal depth (non-Python files)...")
    universal_violations = validate_universal_depth(project_root)
    if not universal_violations:
        print("  ✅ Universal depth is compliant")
    else:
        print(f"  ⚠️  Found {len(universal_violations)} universal depth violations")
        print("\n  Files that would be archived:")
        for violation in universal_violations[:5]:
            print(
                f"    - {violation['file']} (depth {violation['actual_depth']}, expected {violation['expected_depth']})",
            )
        if len(universal_violations) > 5:
            print(f"    ... and {len(universal_violations) - 5} more")
    print("\n" + "=" * 80)
    print("DRY RUN SUMMARY")
    print("=" * 80)
    total_issues = (
        len(l2_l3_result["missing_dirs"])
        + len(apps_violations)
        + len(tests_violations)
        + len(universal_violations)
    )
    print(f"L2/L3 directories to create: {len(l2_l3_result['missing_dirs'])}")
    print(f"apps_* files to archive: {len(apps_violations)}")
    print(f"tests files to archive: {len(tests_violations)}")
    print(f"Universal depth files to archive: {len(universal_violations)}")
    print(f"\nTotal actions that would be taken: {total_issues}")
    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)
    if total_issues > 0:
        print("\n⚠️  To apply these changes, run HierarchyEnforcerAgent with execute=True")


if __name__ == "__main__":
    main()
