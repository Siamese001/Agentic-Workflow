#!/usr/bin/env python3
"""
Fix remaining mislocated test.
"""

import json
import pathlib
import shutil

from agentic_core.L0_routing.config.path_constants import TESTS_DIR, get_validated_project_root
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_records_execution_trace("p0", "evidence", "fix_mislocated")
_emit_applies_guardrail("p0", "fix_mislocated", "p0_governance")
_emit_reads_policy_state("p0", "fix_mislocated", "policy_binding")
_emit_snapshots_state("p0", "fix_mislocated", "state_snapshot")
emit_replay_key("p0", "fix_mislocated")
emit_determinism_digest("p0", "fix_mislocated")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "fix_mislocated", "execution_auth")
_emit_validates_capability("p2", "fix_mislocated", "capability_check")
_emit_routes_to_capability("p2", "fix_mislocated", "capability_route")
_emit_writes_via_uwg("p2", "fix_mislocated", "uwg_write")
_emit_blocks_direct_write("p2", "fix_mislocated", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_mislocated", "tool_invocation")
_emit_captures_execution_output("p2", "fix_mislocated", "exec_output")
_emit_dispatches_agent("p3", "fix_mislocated", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_mislocated", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_mislocated", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_mislocated", "healing_outcome")
_emit_escalates_failure("p3", "fix_mislocated", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_mislocated", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_mislocated", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_mislocated", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_mislocated", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_mislocated", "eval_metric")
_emit_stores_embedding("p4", "fix_mislocated", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_mislocated", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_mislocated", "exec_snapshot_link")

_ROOT = get_validated_project_root()


def main():
    """Fix the single remaining mislocated test."""
    with open("tests/_contracts/mirror_discovery_snapshot.json") as f:
        snapshot = json.load(f)

    mislocated = [m for m in snapshot["modules"] if m["status"] == "MISLOCATED"]
    print(f"Found {len(mislocated)} mislocated tests")

    for module_info in mislocated:
        module_path = pathlib.Path(module_info["module"])
        expected_test_path = pathlib.Path(module_info["expected_test"])

        # Find the actual test file
        module_name = module_path.stem
        test_root = _ROOT / TESTS_DIR

        actual_test = None
        for test_file in test_root.rglob("test_*.py"):
            if test_file.name == f"test_{module_name}.py":
                actual_test = test_file
                break

        if actual_test and actual_test != expected_test_path:
            print(f"Moving: {actual_test} -> {expected_test_path}")

            # Create target directory
            expected_test_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            try:
                shutil.move(str(actual_test), str(expected_test_path))
                print("Successfully moved mislocated test")
            except Exception as e:
                raise
                print(f"Failed to move {actual_test}: {e}")


if __name__ == "__main__":
    main()
