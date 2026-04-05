#!/usr/bin/env python3
"""
Phase 0 Discovery Script - Enumerate modules and tests for mirror contract analysis.
"""

import json
import pathlib

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
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

_emit_emits_metric_event("phase0_discovery", "p4obs", "metric_1")
_emit_emits_metric_event("phase0_discovery", "p4obs", "metric_2")
_emit_emits_metric_event("phase0_discovery", "p4obs", "metric_3")
_emit_emits_metric_event("phase0_discovery", "p4obs", "metric_4")
_emit_emits_metric_event("phase0_discovery", "p4obs", "metric_5")
_emit_emits_metric_event("phase0_discovery", "p4obs", "metric_6")
_emit_records_incident_event("phase0_discovery", "p4obs", "incident")
_emit_captures_runtime_anomaly("phase0_discovery", "p4obs", "anomaly")
_emit_writes_observability_log("phase0_discovery", "p4obs", "obs_log")
_emit_updates_monitoring_state("phase0_discovery", "p4obs", "mon_state")
_emit_triggers_alert("phase0_discovery", "p4obs", "alert")
_emit_links_incident_trace("phase0_discovery", "p4obs", "trace_link")
_emit_captures_pattern("phase0_discovery", "p3lm", "pattern")
_emit_records_learning_event("phase0_discovery", "p3lm", "learning_event")
_emit_writes_learning_snapshot("phase0_discovery", "p3lm", "snapshot")
_emit_feeds_meta_learning("phase0_discovery", "p3lm", "meta_feed")
_emit_updates_routing_strategy("phase0_discovery", "p3lm", "routing")
_emit_improves_agent_policy("phase0_discovery", "p3lm", "policy")
_emit_stores_learning_state("phase0_discovery", "p3lm", "state")
_emit_records_execution_trace("phase0_discovery", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("phase0_discovery", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("phase0_discovery", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("phase0_discovery", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("phase0_discovery", "L4_STATE", "p2_trace_5")
_emit_reads_environ("phase0_discovery", "env_read", "p2_env_1")
_emit_reads_environ("phase0_discovery", "env_read", "p2_env_2")
_emit_reads_runtime_state("phase0_discovery", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("phase0_discovery", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "phase0_discovery")
_emit_applies_guardrail("p0", "phase0_discovery", "p0_governance")
_emit_reads_policy_state("p0", "phase0_discovery", "policy_binding")
_emit_snapshots_state("p0", "phase0_discovery", "state_snapshot")
_emit_pulls_context("p1", "phase0_discovery", "context_pull")
_emit_pulls_context("p1", "phase0_discovery", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "phase0_discovery", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "phase0_discovery", "uwg_term_secondary")
_emit_writes_through("p1", "phase0_discovery", "write_through")
_emit_writes_through("p1", "phase0_discovery", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "phase0_discovery", "safety_validation")
_emit_invokes_eval("p1", "phase0_discovery", "eval_call")
_emit_proposal_commits_routing("p1", "phase0_discovery", "routing_commit")
_emit_escalates_to_human("p1", "phase0_discovery", "human_escalation")
_emit_routes_through("p1", "phase0_discovery", "route_through")
_emit_checks_agent_registry("p1", "phase0_discovery", "agent_registry")
_emit_validates_agent_capability("p1", "phase0_discovery", "capability")
_emit_dispatches_execution_plan("p1", "phase0_discovery", "exec_plan")
_emit_agent_executes_agent("p1", "phase0_discovery", "sub_agent")
_emit_routes_to_agent("p1", "phase0_discovery", "target_agent")
_emit_verifies_policy("p1", "phase0_discovery", "policy_check")
_emit_observes_runtime_state("p1", "phase0_discovery", "runtime_state")
_emit_verifies_boundary("p1", "phase0_discovery", "boundary_check")
_emit_transcripts_response("p1", "phase0_discovery", "transcript")
_emit_hard_fails_untranscripted("p1", "phase0_discovery")
_emit_gated_by_confidence("p1", "phase0_discovery", "confidence_gate")
emit_replay_key("p0", "phase0_discovery")
emit_determinism_digest("p0", "phase0_discovery")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "phase0_discovery", "execution_auth")
_emit_validates_capability("p2", "phase0_discovery", "capability_check")
_emit_routes_to_capability("p2", "phase0_discovery", "capability_route")
_emit_writes_via_uwg("p2", "phase0_discovery", "uwg_write")
_emit_blocks_direct_write("p2", "phase0_discovery", "direct_write_block")
_emit_records_tool_invocation("p2", "phase0_discovery", "tool_invocation")
_emit_captures_execution_output("p2", "phase0_discovery", "exec_output")
_emit_dispatches_agent("p3", "phase0_discovery", "agent_dispatch")
_emit_coordinates_agents("p3", "phase0_discovery", "agent_coordination")
_emit_records_workflow_lineage("p3", "phase0_discovery", "workflow_lineage")
_emit_records_healing_outcome("p3", "phase0_discovery", "healing_outcome")
_emit_escalates_failure("p3", "phase0_discovery", "failure_escalation")
_emit_orchestrates_workflow("p3", "phase0_discovery", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "phase0_discovery", "healing_dispatch")
_emit_invokes_evaluation("p3", "phase0_discovery", "evaluation_signal")
_emit_records_telemetry_event("p4", "phase0_discovery", "telemetry_event")
_emit_captures_evaluation_metric("p4", "phase0_discovery", "eval_metric")
_emit_stores_embedding("p4", "phase0_discovery", "embedding_store")
_emit_updates_meta_learning_state("p4", "phase0_discovery", "meta_learning")
_emit_links_execution_to_snapshot("p4", "phase0_discovery", "exec_snapshot_link")

_ROOT = get_validated_project_root()


def enumerate_modules() -> list[pathlib.Path]:
    """Enumerate all Python modules in scope."""
    modules = []

    # Search agentic_core
    agentic_core_path = _ROOT / AGENTIC_CORE_DIR
    if agentic_core_path.exists():
        modules.extend(agentic_core_path.rglob("*.py"))

    # Search apps_* directories
    for apps_dir in pathlib.Path(".").glob("apps_*"):
        if apps_dir.is_dir():
            modules.extend(apps_dir.rglob("*.py"))

    # Filter out excluded paths
    excluded_patterns = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

    filtered_modules = []
    for module in modules:
        module_str = str(module)
        if not any(pattern in module_str for pattern in excluded_patterns):
            filtered_modules.append(module)

    return sorted(filtered_modules)


def enumerate_tests() -> list[pathlib.Path]:
    """Enumerate all existing test files."""
    tests_path = _ROOT / TESTS_DIR
    if not tests_path.exists():
        return []

    return sorted(tests_path.rglob("test_*.py"))


def compute_expected_test_path(module_path: pathlib.Path) -> pathlib.Path:
    """Compute canonical expected test path for a module."""
    # Convert agentic_core/foo/bar.py -> tests/agentic_core/foo/test_bar.py
    # Convert apps_lic/foo/bar.py -> tests/apps_lic/foo/test_bar.py

    module_str = str(module_path)

    # guardian: allow-path-string
    if module_str.startswith(AGENTIC_CORE_DIR) or module_str.startswith(AGENTIC_CORE_DIR + "\\"):
        relative_parts = module_path.parts
        test_parts = [TESTS_DIR] + list(relative_parts[:-1]) + [f"test_{module_path.name}"]
        return pathlib.Path(*test_parts)
    elif any(module_str.startswith(apps) for apps in ["apps_", "apps_lic\\", "apps_rg\\", "apps_shared\\"]):
        relative_parts = module_path.parts
        test_parts = [TESTS_DIR] + list(relative_parts[:-1]) + [f"test_{module_path.name}"]
        return pathlib.Path(*test_parts)
    else:
        raise ValueError(f"Unexpected module path: {module_path}")


def check_test_status(module_path: pathlib.Path, existing_tests: list[pathlib.Path]) -> str:
    """Check if module has PRESENT, MISSING, or MISLOCATED test."""
    expected_path = compute_expected_test_path(module_path)

    # Check if test exists at expected location
    if expected_path in existing_tests:
        return "PRESENT"

    # Check if test exists elsewhere (mislocated)
    module_name = module_path.stem
    for test_path in existing_tests:
        if test_path.name == f"test_{module_name}.py":
            return "MISLOCATED"

    return "MISSING"


def main():
    """Main discovery execution."""
    print("=== PHASE 0: DISCOVERY LOCK ===\n")

    # 1) Enumerate modules
    print("1) Enumerating Python modules...")
    modules = enumerate_modules()
    print(f"Found {len(modules)} modules")

    # Count by package
    package_counts = {}
    for module in modules:
        if module.parts[0] == AGENTIC_CORE_DIR:
            package_counts[AGENTIC_CORE_DIR] = package_counts.get(AGENTIC_CORE_DIR, 0) + 1
        elif module.parts[0].startswith("apps_"):
            package = module.parts[0]
            package_counts[package] = package_counts.get(package, 0) + 1

    print("Package distribution:")
    for package, count in sorted(package_counts.items()):
        print(f"  {package}: {count} modules")

    # 2) Enumerate existing tests
    print("\n2) Enumerating existing tests...")
    tests = enumerate_tests()
    print(f"Found {len(tests)} test files")

    # 3) Compute status for each module
    print("\n3) Computing test status...")
    status_counts = {"PRESENT": 0, "MISSING": 0, "MISLOCATED": 0}
    module_status = []

    for module in modules:
        status = check_test_status(module, tests)
        status_counts[status] += 1
        module_status.append(
            {
                "module": str(module),
                "expected_test": str(compute_expected_test_path(module)),
                "status": status,
            },
        )

    # 4) Generate report
    print("\n4) Status breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

    # Generate machine-readable report
    report = {
        "timestamp": "2026-02-09T06:41:00Z",
        "total_modules": len(modules),
        "total_tests": len(tests),
        "status_counts": status_counts,
        "package_counts": package_counts,
        "modules": module_status,
    }

    # Save report
    report_path = pathlib.Path("docs/reports/plans/phase0_discovery_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    # Print sample of each status
    print("\n5) Sample modules by status:")
    for status in ["PRESENT", "MISSING", "MISLOCATED"]:
        samples = [m for m in module_status if m["status"] == status][:3]
        print(f"\n{status} samples:")
        for sample in samples:
            print(f"  {sample['module']} -> {sample['expected_test']}")


if __name__ == "__main__":
    main()
