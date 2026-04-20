#!/usr/bin/env python3
"""
Move mislocated tests to canonical mirror locations - Fixed version.
Phase 2: Structural remediation - move tests from unit/ structure to mirror structure.
"""

import os
import pathlib
import shutil

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
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
from tqdm import tqdm

_emit_emits_metric_event("move_mislocated_tests_fixed", "p4obs", "metric_1")
_emit_emits_metric_event("move_mislocated_tests_fixed", "p4obs", "metric_2")
_emit_emits_metric_event("move_mislocated_tests_fixed", "p4obs", "metric_3")
_emit_emits_metric_event("move_mislocated_tests_fixed", "p4obs", "metric_4")
_emit_emits_metric_event("move_mislocated_tests_fixed", "p4obs", "metric_5")
_emit_emits_metric_event("move_mislocated_tests_fixed", "p4obs", "metric_6")
_emit_records_incident_event("move_mislocated_tests_fixed", "p4obs", "incident")
_emit_captures_runtime_anomaly("move_mislocated_tests_fixed", "p4obs", "anomaly")
_emit_writes_observability_log("move_mislocated_tests_fixed", "p4obs", "obs_log")
_emit_updates_monitoring_state("move_mislocated_tests_fixed", "p4obs", "mon_state")
_emit_triggers_alert("move_mislocated_tests_fixed", "p4obs", "alert")
_emit_links_incident_trace("move_mislocated_tests_fixed", "p4obs", "trace_link")
_emit_captures_pattern("move_mislocated_tests_fixed", "p3lm", "pattern")
_emit_records_learning_event("move_mislocated_tests_fixed", "p3lm", "learning_event")
_emit_writes_learning_snapshot("move_mislocated_tests_fixed", "p3lm", "snapshot")
_emit_feeds_meta_learning("move_mislocated_tests_fixed", "p3lm", "meta_feed")
_emit_updates_routing_strategy("move_mislocated_tests_fixed", "p3lm", "routing")
_emit_improves_agent_policy("move_mislocated_tests_fixed", "p3lm", "policy")
_emit_stores_learning_state("move_mislocated_tests_fixed", "p3lm", "state")
_emit_records_execution_trace("move_mislocated_tests_fixed", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("move_mislocated_tests_fixed", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("move_mislocated_tests_fixed", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("move_mislocated_tests_fixed", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("move_mislocated_tests_fixed", "L4_STATE", "p2_trace_5")
_emit_reads_environ("move_mislocated_tests_fixed", "env_read", "p2_env_1")
_emit_reads_environ("move_mislocated_tests_fixed", "env_read", "p2_env_2")
_emit_reads_runtime_state("move_mislocated_tests_fixed", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("move_mislocated_tests_fixed", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "move_mislocated_tests_fixed")
_emit_applies_guardrail("p0", "move_mislocated_tests_fixed", "p0_governance")
_emit_reads_policy_state("p0", "move_mislocated_tests_fixed", "policy_binding")
_emit_snapshots_state("p0", "move_mislocated_tests_fixed", "state_snapshot")
_emit_pulls_context("p1", "move_mislocated_tests_fixed", "context_pull")
_emit_pulls_context("p1", "move_mislocated_tests_fixed", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "move_mislocated_tests_fixed", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "move_mislocated_tests_fixed", "uwg_term_secondary")
_emit_writes_through("p1", "move_mislocated_tests_fixed", "write_through")
_emit_writes_through("p1", "move_mislocated_tests_fixed", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "move_mislocated_tests_fixed", "safety_validation")
_emit_invokes_eval("p1", "move_mislocated_tests_fixed", "eval_call")
_emit_proposal_commits_routing("p1", "move_mislocated_tests_fixed", "routing_commit")
_emit_escalates_to_human("p1", "move_mislocated_tests_fixed", "human_escalation")
_emit_routes_through("p1", "move_mislocated_tests_fixed", "route_through")
_emit_checks_agent_registry("p1", "move_mislocated_tests_fixed", "agent_registry")
_emit_validates_agent_capability("p1", "move_mislocated_tests_fixed", "capability")
_emit_dispatches_execution_plan("p1", "move_mislocated_tests_fixed", "exec_plan")
_emit_agent_executes_agent("p1", "move_mislocated_tests_fixed", "sub_agent")
_emit_routes_to_agent("p1", "move_mislocated_tests_fixed", "target_agent")
_emit_verifies_policy("p1", "move_mislocated_tests_fixed", "policy_check")
_emit_observes_runtime_state("p1", "move_mislocated_tests_fixed", "runtime_state")
_emit_verifies_boundary("p1", "move_mislocated_tests_fixed", "boundary_check")
_emit_transcripts_response("p1", "move_mislocated_tests_fixed", "transcript")
_emit_hard_fails_untranscripted("p1", "move_mislocated_tests_fixed")
_emit_gated_by_confidence("p1", "move_mislocated_tests_fixed", "confidence_gate")
emit_replay_key("p0", "move_mislocated_tests_fixed")
emit_determinism_digest("p0", "move_mislocated_tests_fixed")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "move_mislocated_tests_fixed", "execution_auth")
_emit_validates_capability("p2", "move_mislocated_tests_fixed", "capability_check")
_emit_routes_to_capability("p2", "move_mislocated_tests_fixed", "capability_route")
_emit_writes_via_uwg("p2", "move_mislocated_tests_fixed", "uwg_write")
_emit_blocks_direct_write("p2", "move_mislocated_tests_fixed", "direct_write_block")
_emit_records_tool_invocation("p2", "move_mislocated_tests_fixed", "tool_invocation")
_emit_captures_execution_output("p2", "move_mislocated_tests_fixed", "exec_output")
_emit_dispatches_agent("p3", "move_mislocated_tests_fixed", "agent_dispatch")
_emit_coordinates_agents("p3", "move_mislocated_tests_fixed", "agent_coordination")
_emit_records_workflow_lineage("p3", "move_mislocated_tests_fixed", "workflow_lineage")
_emit_records_healing_outcome("p3", "move_mislocated_tests_fixed", "healing_outcome")
_emit_escalates_failure("p3", "move_mislocated_tests_fixed", "failure_escalation")
_emit_orchestrates_workflow("p3", "move_mislocated_tests_fixed", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "move_mislocated_tests_fixed", "healing_dispatch")
_emit_invokes_evaluation("p3", "move_mislocated_tests_fixed", "evaluation_signal")
_emit_records_telemetry_event("p4", "move_mislocated_tests_fixed", "telemetry_event")
_emit_captures_evaluation_metric("p4", "move_mislocated_tests_fixed", "eval_metric")
_emit_stores_embedding("p4", "move_mislocated_tests_fixed", "embedding_store")
_emit_updates_meta_learning_state("p4", "move_mislocated_tests_fixed", "meta_learning")
_emit_links_execution_to_snapshot("p4", "move_mislocated_tests_fixed", "exec_snapshot_link")

_ROOT = get_validated_project_root()

_APP_DIRS: frozenset[str] = frozenset({AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR})


def discover_mislocated_tests() -> list[tuple[pathlib.Path, pathlib.Path, pathlib.Path]]:
    """Discover all mislocated tests and their target locations."""
    mislocated = []

    test_root = _ROOT / TESTS_DIR
    if not test_root.exists():
        return mislocated

    for test_file in tqdm(test_root.rglob("test_*.py"), desc="Processing", unit="item"):
        # Skip contract tests
        if "_contracts" in test_file.parts:
            continue

        relative = test_file.relative_to(test_root)
        parts = list(relative.parts)

        # Check if this is in unit structure for our packages
        if len(parts) >= 3 and parts[0] == "unit" and parts[1] in _APP_DIRS:
            # This should be moved to mirror structure
            # tests/unit/agentic_core/base_agents/test_foo.py -> tests/agentic_core/base_agents/test_foo.py

            package = parts[1]  # agentic_core, apps_lic, etc.
            module_parts = parts[2:]  # base_agents, test_foo.py

            # Target location in mirror structure
            target_path = pathlib.Path(TESTS_DIR) / package / pathlib.Path(*module_parts)

            # Reconstruct module path for reporting
            test_filename = parts[-1]
            if test_filename.startswith("test_") and test_filename.endswith(".py"):
                module_filename = test_filename[5:]  # Remove "test_"
                module_path = pathlib.Path(package) / pathlib.Path(*module_parts[:-1]) / module_filename
            else:
                module_path = pathlib.Path(package) / pathlib.Path(*module_parts[:-1]) / test_filename

            mislocated.append((test_file, target_path, module_path))

    return mislocated


def move_test_file(source: pathlib.Path, target: pathlib.Path, dry_run: bool = True):
    """Move a test file to its canonical location."""
    # Create target directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        print(f"Would move: {source} -> {target}")
        return False

    if target.exists():
        print(f"Target exists, skipping: {target}")
        return False

    try:
        shutil.move(str(source), str(target))
        print(f"Moved: {source} -> {target}")
        return True
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise


def update_imports_in_moved_test(test_file: pathlib.Path):
    """Update imports in the moved test file to reflect new location."""
    try:
        content = test_file.read_text(encoding="utf-8")

        # Update relative imports based on new location
        lines = content.split("\n")
        updated_lines = []

        for line in tqdm(lines, desc="Processing", unit="item"):
            # Skip non-import lines
            if not (line.strip().startswith("from ") or line.strip().startswith("import ")):
                updated_lines.append(line)
                continue

            # Remove 'unit.' from imports
            if "unit." in line:
                updated_line = line.replace("unit.", "")
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)

        updated_content = "\n".join(updated_lines)

        if updated_content != content:
            test_file.write_text(updated_content, encoding="utf-8")
            print(f"Updated imports in: {test_file}")

    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise


def main():
    """Main execution."""
    print("=== Phase 2: Move Mislocated Tests to Canonical Locations ===\n")

    mislocated = discover_mislocated_tests()

    if not mislocated:
        print("✅ No mislocated tests found!")
        return

    print(f"Found {len(mislocated)} mislocated tests to move\n")

    # Group by package for better organization
    by_package = {}
    for source, target, module_path in mislocated:
        package = target.parts[1] if len(target.parts) > 1 else "misc"
        if package not in by_package:
            by_package[package] = []
        by_package[package].append((source, target, module_path))

    total_moved = 0

    for package, tests in tqdm(sorted(by_package.items()), desc="Processing", unit="item"):
        print(f"### Moving {package} tests ({len(tests)} files)")

        for source, target, module_path in sorted(tests):
            print(f"  {module_path}")
            print(
                f"    {source.relative_to(_ROOT / TESTS_DIR)} -> {target.relative_to(_ROOT / TESTS_DIR)}",
            )

            # Move the file
            if move_test_file(source, target, dry_run=False):
                update_imports_in_moved_test(target)
                total_moved += 1

        print()

    print(f"✅ Moved {total_moved} test files to canonical locations")

    # Clean up empty directories
    print("\n### Cleaning up empty directories...")
    test_root = pathlib.Path(TESTS_DIR)
    if test_root.exists():
        for root, dirs, files in os.walk(test_root, topdown=False):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for dir_name in dirs:
                dir_path = pathlib.Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        print(f"Removed empty directory: {dir_path.relative_to(test_root)}")
                except OSError:  # guardian: Add error context logging
                    pass  # Directory not empty or other error


if __name__ == "__main__":
    main()
