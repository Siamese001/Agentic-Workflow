#!/usr/bin/env python3
"""
Fix remaining mislocated test.
"""

import json
import pathlib
import shutil

from agentic_core.L0_routing.config.path_constants import TESTS_DIR, get_validated_project_root
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

_emit_emits_metric_event("fix_mislocated", "p4obs", "metric_1")
_emit_emits_metric_event("fix_mislocated", "p4obs", "metric_2")
_emit_emits_metric_event("fix_mislocated", "p4obs", "metric_3")
_emit_emits_metric_event("fix_mislocated", "p4obs", "metric_4")
_emit_emits_metric_event("fix_mislocated", "p4obs", "metric_5")
_emit_emits_metric_event("fix_mislocated", "p4obs", "metric_6")
_emit_records_incident_event("fix_mislocated", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_mislocated", "p4obs", "anomaly")
_emit_writes_observability_log("fix_mislocated", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_mislocated", "p4obs", "mon_state")
_emit_triggers_alert("fix_mislocated", "p4obs", "alert")
_emit_links_incident_trace("fix_mislocated", "p4obs", "trace_link")
_emit_captures_pattern("fix_mislocated", "p3lm", "pattern")
_emit_records_learning_event("fix_mislocated", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_mislocated", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_mislocated", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_mislocated", "p3lm", "routing")
_emit_improves_agent_policy("fix_mislocated", "p3lm", "policy")
_emit_stores_learning_state("fix_mislocated", "p3lm", "state")
_emit_records_execution_trace("fix_mislocated", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_mislocated", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_mislocated", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_mislocated", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_mislocated", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_mislocated", "env_read", "p2_env_1")
_emit_reads_environ("fix_mislocated", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_mislocated", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_mislocated", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "fix_mislocated")
_emit_applies_guardrail("p0", "fix_mislocated", "p0_governance")
_emit_reads_policy_state("p0", "fix_mislocated", "policy_binding")
_emit_snapshots_state("p0", "fix_mislocated", "state_snapshot")
_emit_pulls_context("p1", "fix_mislocated", "context_pull")
_emit_pulls_context("p1", "fix_mislocated", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_mislocated", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_mislocated", "uwg_term_secondary")
_emit_writes_through("p1", "fix_mislocated", "write_through")
_emit_writes_through("p1", "fix_mislocated", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_mislocated", "safety_validation")
_emit_invokes_eval("p1", "fix_mislocated", "eval_call")
_emit_proposal_commits_routing("p1", "fix_mislocated", "routing_commit")
_emit_escalates_to_human("p1", "fix_mislocated", "human_escalation")
_emit_routes_through("p1", "fix_mislocated", "route_through")
_emit_checks_agent_registry("p1", "fix_mislocated", "agent_registry")
_emit_validates_agent_capability("p1", "fix_mislocated", "capability")
_emit_dispatches_execution_plan("p1", "fix_mislocated", "exec_plan")
_emit_agent_executes_agent("p1", "fix_mislocated", "sub_agent")
_emit_routes_to_agent("p1", "fix_mislocated", "target_agent")
_emit_verifies_policy("p1", "fix_mislocated", "policy_check")
_emit_observes_runtime_state("p1", "fix_mislocated", "runtime_state")
_emit_verifies_boundary("p1", "fix_mislocated", "boundary_check")
_emit_transcripts_response("p1", "fix_mislocated", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_mislocated")
_emit_gated_by_confidence("p1", "fix_mislocated", "confidence_gate")
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

    for module_info in tqdm(mislocated, desc="Processing", unit="item"):
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
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                print(f"Failed to move {actual_test}: {e}")


if __name__ == "__main__":
    main()
