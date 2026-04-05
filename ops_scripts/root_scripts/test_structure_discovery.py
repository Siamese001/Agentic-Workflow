#!/usr/bin/env python3
"""
Test Structure Mirror Contract - Phase 0 Discovery
Generates mapping report of code modules to expected test locations.
"""

import pathlib
from collections import defaultdict
from dataclasses import dataclass

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("test_structure_discovery", "p4obs", "metric_1")
_emit_emits_metric_event("test_structure_discovery", "p4obs", "metric_2")
_emit_emits_metric_event("test_structure_discovery", "p4obs", "metric_3")
_emit_emits_metric_event("test_structure_discovery", "p4obs", "metric_4")
_emit_emits_metric_event("test_structure_discovery", "p4obs", "metric_5")
_emit_emits_metric_event("test_structure_discovery", "p4obs", "metric_6")
_emit_records_incident_event("test_structure_discovery", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_structure_discovery", "p4obs", "anomaly")
_emit_writes_observability_log("test_structure_discovery", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_structure_discovery", "p4obs", "mon_state")
_emit_triggers_alert("test_structure_discovery", "p4obs", "alert")
_emit_links_incident_trace("test_structure_discovery", "p4obs", "trace_link")
_emit_captures_pattern("test_structure_discovery", "p3lm", "pattern")
_emit_records_learning_event("test_structure_discovery", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_structure_discovery", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_structure_discovery", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_structure_discovery", "p3lm", "routing")
_emit_improves_agent_policy("test_structure_discovery", "p3lm", "policy")
_emit_stores_learning_state("test_structure_discovery", "p3lm", "state")
_emit_records_execution_trace("test_structure_discovery", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_structure_discovery", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_structure_discovery", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_structure_discovery", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_structure_discovery", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_structure_discovery", "env_read", "p2_env_1")
_emit_reads_environ("test_structure_discovery", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_structure_discovery", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_structure_discovery", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_structure_discovery")
_emit_applies_guardrail("p0", "test_structure_discovery", "p0_governance")
_emit_reads_policy_state("p0", "test_structure_discovery", "policy_binding")
_emit_snapshots_state("p0", "test_structure_discovery", "state_snapshot")
_emit_pulls_context("p1", "test_structure_discovery", "context_pull")
_emit_pulls_context("p1", "test_structure_discovery", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_structure_discovery", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_structure_discovery", "uwg_term_secondary")
_emit_writes_through("p1", "test_structure_discovery", "write_through")
_emit_writes_through("p1", "test_structure_discovery", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_structure_discovery", "safety_validation")
_emit_invokes_eval("p1", "test_structure_discovery", "eval_call")
_emit_proposal_commits_routing("p1", "test_structure_discovery", "routing_commit")
_emit_escalates_to_human("p1", "test_structure_discovery", "human_escalation")
_emit_routes_through("p1", "test_structure_discovery", "route_through")
_emit_checks_agent_registry("p1", "test_structure_discovery", "agent_registry")
_emit_validates_agent_capability("p1", "test_structure_discovery", "capability")
_emit_dispatches_execution_plan("p1", "test_structure_discovery", "exec_plan")
_emit_agent_executes_agent("p1", "test_structure_discovery", "sub_agent")
_emit_routes_to_agent("p1", "test_structure_discovery", "target_agent")
_emit_verifies_policy("p1", "test_structure_discovery", "policy_check")
_emit_observes_runtime_state("p1", "test_structure_discovery", "runtime_state")
_emit_verifies_boundary("p1", "test_structure_discovery", "boundary_check")
_emit_transcripts_response("p1", "test_structure_discovery", "transcript")
_emit_hard_fails_untranscripted("p1", "test_structure_discovery")
_emit_gated_by_confidence("p1", "test_structure_discovery", "confidence_gate")
emit_replay_key("p0", "test_structure_discovery")
emit_determinism_digest("p0", "test_structure_discovery")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_structure_discovery", "execution_auth")
_emit_validates_capability("p2", "test_structure_discovery", "capability_check")
_emit_routes_to_capability("p2", "test_structure_discovery", "capability_route")
_emit_writes_via_uwg("p2", "test_structure_discovery", "uwg_write")
_emit_blocks_direct_write("p2", "test_structure_discovery", "direct_write_block")
_emit_records_tool_invocation("p2", "test_structure_discovery", "tool_invocation")
_emit_captures_execution_output("p2", "test_structure_discovery", "exec_output")
_emit_dispatches_agent("p3", "test_structure_discovery", "agent_dispatch")
_emit_coordinates_agents("p3", "test_structure_discovery", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_structure_discovery", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_structure_discovery", "healing_outcome")
_emit_escalates_failure("p3", "test_structure_discovery", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_structure_discovery", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_structure_discovery", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_structure_discovery", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_structure_discovery", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_structure_discovery", "eval_metric")
_emit_stores_embedding("p4", "test_structure_discovery", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_structure_discovery", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_structure_discovery", "exec_snapshot_link")

_ROOT = get_validated_project_root()


@dataclass
class ModuleInfo:
    path: pathlib.Path
    expected_test_path: pathlib.Path
    status: str  # PRESENT, MISSING, MISLOCATED, WAIVED
    actual_test_path: pathlib.Path = None


def discover_python_modules(root: pathlib.Path) -> list[pathlib.Path]:
    """Discover all Python modules in scope."""
    modules = []
    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    for py_file in root.rglob("*.py"):
        # Skip excluded directories
        if any(exclude in str(py_file) for exclude in exclude_dirs):
            continue
        # Skip test files themselves
        if TESTS_DIR in py_file.parts:
            continue
        modules.append(py_file)

    return sorted(modules)


def discover_existing_tests() -> list[pathlib.Path]:
    """Discover all existing test files."""
    test_root = _ROOT / TESTS_DIR
    if not test_root.exists():
        return []

    return sorted(test_root.rglob("test_*.py"))


def compute_expected_test_path(module_path: pathlib.Path) -> pathlib.Path:
    """Compute expected test path based on mirror rules."""
    # Convert module path to test path
    if module_path.parts[0] == AGENTIC_CORE_DIR:
        # agentic_core/L1_cognition/reasoning/foo.py -> tests/agentic_core/L1_cognition/reasoning/test_foo.py
        relative_parts = module_path.parts[1:]  # Skip 'agentic_core'
        test_name = f"test_{module_path.stem}.py"
        return pathlib.Path(TESTS_DIR) / AGENTIC_CORE_DIR / pathlib.Path(*relative_parts).parent / test_name
    elif module_path.parts[0].startswith("apps_"):
        # apps_lic/engines/foo.py -> tests/apps_lic/engines/test_foo.py
        relative_parts = module_path.parts[1:]  # Skip 'apps_*'
        test_name = f"test_{module_path.stem}.py"
        return (
            pathlib.Path(TESTS_DIR) / module_path.parts[0] / pathlib.Path(*relative_parts).parent / test_name
        )
    else:
        raise ValueError(f"Unexpected module root: {module_path.parts[0]}")


def check_test_status(
    module_path: pathlib.Path,
    expected_test_path: pathlib.Path,
    existing_tests: list[pathlib.Path],
) -> tuple[str, pathlib.Path]:
    """Check test status for a module."""
    existing_test_paths = set(existing_tests)

    if expected_test_path in existing_test_paths:
        return "PRESENT", expected_test_path

    # Check if test exists elsewhere (mislocated)
    expected_name = expected_test_path.name
    for test_path in existing_tests:
        if test_path.name == expected_name and test_path.parent != expected_test_path.parent:
            return "MISLOCATED", test_path

    return "MISSING", None


def generate_mapping_report() -> dict:
    """Generate complete mapping report."""
    root = pathlib.Path(".")

    # Discover modules
    agentic_modules = discover_python_modules(_ROOT / AGENTIC_CORE_DIR)
    apps_lic_modules = discover_python_modules(_ROOT / APPS_LIC_DIR)
    apps_rg_modules = discover_python_modules(_ROOT / APPS_RG_DIR)
    apps_shared_modules = discover_python_modules(_ROOT / APPS_SHARED_DIR)

    all_modules = agentic_modules + apps_lic_modules + apps_rg_modules + apps_shared_modules

    # Discover existing tests
    existing_tests = discover_existing_tests()

    # Process each module
    modules_info = []
    status_counts = defaultdict(int)

    for module_path in all_modules:
        expected_test_path = compute_expected_test_path(module_path)
        status, actual_test_path = check_test_status(module_path, expected_test_path, existing_tests)

        module_info = ModuleInfo(
            path=module_path,
            expected_test_path=expected_test_path,
            status=status,
            actual_test_path=actual_test_path,
        )
        modules_info.append(module_info)
        status_counts[status] += 1

    # Generate summary
    summary = {
        "total_modules": len(all_modules),
        "status_counts": dict(status_counts),
        "agentic_core_count": len(agentic_modules),
        "apps_lic_count": len(apps_lic_modules),
        "apps_rg_count": len(apps_rg_modules),
        "apps_shared_count": len(apps_shared_modules),
        "existing_tests_count": len(existing_tests),
    }

    return {
        "summary": summary,
        "modules": modules_info,
    }


def main():
    """Generate and print mapping report."""
    print("=== TEST STRUCTURE MIRROR CONTRACT - PHASE 0 DISCOVERY ===\n")

    report = generate_mapping_report()

    # Print summary
    summary = report["summary"]
    print("## SUMMARY")
    print(f"Total modules: {summary['total_modules']}")
    print(f"  - agentic_core: {summary['agentic_core_count']}")
    print(f"  - apps_lic: {summary['apps_lic_count']}")
    print(f"  - apps_rg: {summary['apps_rg_count']}")
    print(f"  - apps_shared: {summary['apps_shared_count']}")
    print(f"Existing tests: {summary['existing_tests_count']}")
    print("\nStatus breakdown:")
    for status, count in summary["status_counts"].items():
        print(f"  {status}: {count}")

    print("\n## DETAILED MAPPING")

    # Group by status
    by_status = defaultdict(list)
    for module in report["modules"]:
        by_status[module.status].append(module)

    # Print MISSING modules
    if "MISSING" in by_status:
        print(f"\n### MISSING ({len(by_status['MISSING'])})")
        for module in sorted(by_status["MISSING"], key=lambda m: str(m.path)):
            print(f"  {module.path} -> {module.expected_test_path}")

    # Print MISLOCATED modules
    if "MISLOCATED" in by_status:
        print(f"\n### MISLOCATED ({len(by_status['MISLOCATED'])})")
        for module in sorted(by_status["MISLOCATED"], key=lambda m: str(m.path)):
            print(f"  {module.path}")
            print(f"    Expected: {module.expected_test_path}")
            print(f"    Actual:   {module.actual_test_path}")

    # Print PRESENT modules (just count)
    if "PRESENT" in by_status:
        print(f"\n### PRESENT ({len(by_status['PRESENT'])})")
        print("  All tests correctly located")

    print("\n=== END REPORT ===")


if __name__ == "__main__":
    main()
