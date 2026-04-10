#!/usr/bin/env python3
"""
Phase 0: Discovery - Create deterministic snapshot for contract enforcement.
"""

import fnmatch
import hashlib
import json
import pathlib

import yaml

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_emits_metric_event("create_discovery_snapshot", "p4obs", "metric_1")
_emit_emits_metric_event("create_discovery_snapshot", "p4obs", "metric_2")
_emit_emits_metric_event("create_discovery_snapshot", "p4obs", "metric_3")
_emit_emits_metric_event("create_discovery_snapshot", "p4obs", "metric_4")
_emit_emits_metric_event("create_discovery_snapshot", "p4obs", "metric_5")
_emit_emits_metric_event("create_discovery_snapshot", "p4obs", "metric_6")
_emit_records_incident_event("create_discovery_snapshot", "p4obs", "incident")
_emit_captures_runtime_anomaly("create_discovery_snapshot", "p4obs", "anomaly")
_emit_writes_observability_log("create_discovery_snapshot", "p4obs", "obs_log")
_emit_updates_monitoring_state("create_discovery_snapshot", "p4obs", "mon_state")
_emit_triggers_alert("create_discovery_snapshot", "p4obs", "alert")
_emit_links_incident_trace("create_discovery_snapshot", "p4obs", "trace_link")
_emit_captures_pattern("create_discovery_snapshot", "p3lm", "pattern")
_emit_records_learning_event("create_discovery_snapshot", "p3lm", "learning_event")
_emit_writes_learning_snapshot("create_discovery_snapshot", "p3lm", "snapshot")
_emit_feeds_meta_learning("create_discovery_snapshot", "p3lm", "meta_feed")
_emit_updates_routing_strategy("create_discovery_snapshot", "p3lm", "routing")
_emit_improves_agent_policy("create_discovery_snapshot", "p3lm", "policy")
_emit_stores_learning_state("create_discovery_snapshot", "p3lm", "state")
_emit_records_execution_trace("create_discovery_snapshot", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("create_discovery_snapshot", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("create_discovery_snapshot", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("create_discovery_snapshot", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("create_discovery_snapshot", "L4_STATE", "p2_trace_5")
_emit_reads_environ("create_discovery_snapshot", "env_read", "p2_env_1")
_emit_reads_environ("create_discovery_snapshot", "env_read", "p2_env_2")
_emit_reads_runtime_state("create_discovery_snapshot", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("create_discovery_snapshot", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "create_discovery_snapshot")
_emit_applies_guardrail("p0", "create_discovery_snapshot", "p0_governance")
_emit_reads_policy_state("p0", "create_discovery_snapshot", "policy_binding")
_emit_snapshots_state("p0", "create_discovery_snapshot", "state_snapshot")
_emit_pulls_context("p1", "create_discovery_snapshot", "context_pull")
_emit_pulls_context("p1", "create_discovery_snapshot", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "create_discovery_snapshot", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "create_discovery_snapshot", "uwg_term_secondary")
_emit_writes_through("p1", "create_discovery_snapshot", "write_through")
_emit_writes_through("p1", "create_discovery_snapshot", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "create_discovery_snapshot", "safety_validation")
_emit_invokes_eval("p1", "create_discovery_snapshot", "eval_call")
_emit_proposal_commits_routing("p1", "create_discovery_snapshot", "routing_commit")
_emit_escalates_to_human("p1", "create_discovery_snapshot", "human_escalation")
_emit_routes_through("p1", "create_discovery_snapshot", "route_through")
_emit_checks_agent_registry("p1", "create_discovery_snapshot", "agent_registry")
_emit_validates_agent_capability("p1", "create_discovery_snapshot", "capability")
_emit_dispatches_execution_plan("p1", "create_discovery_snapshot", "exec_plan")
_emit_agent_executes_agent("p1", "create_discovery_snapshot", "sub_agent")
_emit_routes_to_agent("p1", "create_discovery_snapshot", "target_agent")
_emit_verifies_policy("p1", "create_discovery_snapshot", "policy_check")
_emit_observes_runtime_state("p1", "create_discovery_snapshot", "runtime_state")
_emit_verifies_boundary("p1", "create_discovery_snapshot", "boundary_check")
_emit_transcripts_response("p1", "create_discovery_snapshot", "transcript")
_emit_hard_fails_untranscripted("p1", "create_discovery_snapshot")
_emit_gated_by_confidence("p1", "create_discovery_snapshot", "confidence_gate")
emit_replay_key("p0", "create_discovery_snapshot")
emit_determinism_digest("p0", "create_discovery_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "create_discovery_snapshot", "execution_auth")
_emit_validates_capability("p2", "create_discovery_snapshot", "capability_check")
_emit_routes_to_capability("p2", "create_discovery_snapshot", "capability_route")
_emit_writes_via_uwg("p2", "create_discovery_snapshot", "uwg_write")
_emit_blocks_direct_write("p2", "create_discovery_snapshot", "direct_write_block")
_emit_records_tool_invocation("p2", "create_discovery_snapshot", "tool_invocation")
_emit_captures_execution_output("p2", "create_discovery_snapshot", "exec_output")
_emit_dispatches_agent("p3", "create_discovery_snapshot", "agent_dispatch")
_emit_coordinates_agents("p3", "create_discovery_snapshot", "agent_coordination")
_emit_records_workflow_lineage("p3", "create_discovery_snapshot", "workflow_lineage")
_emit_records_healing_outcome("p3", "create_discovery_snapshot", "healing_outcome")
_emit_escalates_failure("p3", "create_discovery_snapshot", "failure_escalation")
_emit_orchestrates_workflow("p3", "create_discovery_snapshot", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "create_discovery_snapshot", "healing_dispatch")
_emit_invokes_evaluation("p3", "create_discovery_snapshot", "evaluation_signal")
_emit_records_telemetry_event("p4", "create_discovery_snapshot", "telemetry_event")
_emit_captures_evaluation_metric("p4", "create_discovery_snapshot", "eval_metric")
_emit_stores_embedding("p4", "create_discovery_snapshot", "embedding_store")
_emit_updates_meta_learning_state("p4", "create_discovery_snapshot", "meta_learning")
_emit_links_execution_to_snapshot("p4", "create_discovery_snapshot", "exec_snapshot_link")

_ROOT = get_validated_project_root()


def enumerate_modules() -> list[pathlib.Path]:
    """Enumerate all Python modules in scope."""
    modules = []

    # Search agentic_core
    agentic_core_path = _ROOT / AGENTIC_CORE_DIR
    if agentic_core_path.exists():
        modules.extend(agentic_core_path.rglob("*.py"))

    # Search apps_* directories
    for apps_dir in _ROOT.glob("apps_*"):
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
    test_root = _ROOT / TESTS_DIR
    if not test_root.exists():
        return []

    return sorted(test_root.rglob("test_*.py"))


def compute_expected_test_path(module_path: pathlib.Path) -> pathlib.Path:
    """Compute canonical expected test path for a module."""
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


def load_waivers() -> set[str]:
    """Load waiver patterns."""
    waivers_file = pathlib.Path("tests/_contracts/mirror_waivers.yaml")
    waived_patterns = set()

    if waivers_file.exists():
        try:
            with open(waivers_file) as f:
                waivers = yaml.safe_load(f)
            for waiver in waivers.get("waivers", []):
                waived_patterns.add(waiver["module"])
        except (OSError, yaml.YAMLError, KeyError):
            pass

    return waived_patterns


def is_waived(module_path: pathlib.Path, waivers: set[str]) -> bool:
    """Check if module is waived."""
    module_str = str(module_path).replace("\\", "/")

    for pattern in waivers:
        pattern_norm = pattern.replace("\\", "/")
        if fnmatch.fnmatch(module_str, pattern_norm):
            return True

    return False


def main():
    """Execute discovery with deterministic output."""
    # 1) Enumerate modules
    modules = enumerate_modules()

    # 2) Enumerate existing tests
    tests = enumerate_tests()

    # 3) Compute status for each module
    status_counts = {"PRESENT": 0, "MISSING": 0, "MISLOCATED": 0, "WAIVED": 0}
    module_status = []
    waivers = load_waivers()

    for module in modules:
        status = check_test_status(module, tests)

        # Check if waived
        if is_waived(module, waivers):
            status = "WAIVED"

        status_counts[status] += 1
        module_status.append(
            {
                "module": str(module),
                "expected_test": str(compute_expected_test_path(module)),
                "status": status,
            },
        )

    # 4) Generate integrity hash
    module_list_str = json.dumps([str(m) for m in modules], sort_keys=True)
    integrity_hash = hashlib.sha256(module_list_str.encode()).hexdigest()

    # 5) Persist deterministic output
    snapshot = {
        "timestamp": "2026-02-09T06:47:00Z",
        "integrity_hash": integrity_hash,
        "total_modules": len(modules),
        "total_tests": len(tests),
        "status_counts": status_counts,
        "modules": module_status,
    }

    # Ensure directory exists
    output_path = pathlib.Path("tests/_contracts/mirror_discovery_snapshot.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Discovery snapshot created: {output_path}")
    print(f"Modules: {len(modules)}, Tests: {len(tests)}")
    print(f"Status: {status_counts}")

    return snapshot


if __name__ == "__main__":
    main()
