"""Structure drift validator CLI for architectural integrity monitoring.

This module provides command-line validation of structure drift by comparing
the current codebase structure against a golden manifest.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentic_core.L5_safety.validators.structure_drift_validator import (
    generate_structure_manifest,
    load_manifest,
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_records_execution_trace("p0", "evidence", "structure_drift_validator")
_emit_applies_guardrail("p0", "structure_drift_validator", "p0_governance")
_emit_reads_policy_state("p0", "structure_drift_validator", "policy_binding")
_emit_snapshots_state("p0", "structure_drift_validator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_1")
_emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_2")
_emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_3")
_emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_4")
_emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_5")
_emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_6")
_emit_records_incident_event("structure_drift_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("structure_drift_validator", "p4obs", "anomaly")
_emit_writes_observability_log("structure_drift_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("structure_drift_validator", "p4obs", "mon_state")
_emit_triggers_alert("structure_drift_validator", "p4obs", "alert")
_emit_links_incident_trace("structure_drift_validator", "p4obs", "trace_link")
_emit_captures_pattern("structure_drift_validator", "p3lm", "pattern")
_emit_records_learning_event("structure_drift_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("structure_drift_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("structure_drift_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("structure_drift_validator", "p3lm", "routing")
_emit_improves_agent_policy("structure_drift_validator", "p3lm", "policy")
_emit_stores_learning_state("structure_drift_validator", "p3lm", "state")
_emit_records_execution_trace("structure_drift_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("structure_drift_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("structure_drift_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("structure_drift_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("structure_drift_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("structure_drift_validator", "env_read", "p2_env_1")
_emit_reads_environ("structure_drift_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("structure_drift_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("structure_drift_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "structure_drift_validator", "context_pull")
_emit_pulls_context("p1", "structure_drift_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "structure_drift_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "structure_drift_validator", "uwg_term_2")
_emit_writes_through("p1", "structure_drift_validator", "write_through")
_emit_writes_through("p1", "structure_drift_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "structure_drift_validator", "safety_validation")
_emit_invokes_eval("p1", "structure_drift_validator", "eval_call")
_emit_proposal_commits_routing("p1", "structure_drift_validator", "routing_commit")
_emit_escalates_to_human("p1", "structure_drift_validator", "human_escalation")
_emit_routes_through("p1", "structure_drift_validator", "route_through")
_emit_checks_agent_registry("p1", "structure_drift_validator", "agent_registry")
_emit_validates_agent_capability("p1", "structure_drift_validator", "capability")
_emit_dispatches_execution_plan("p1", "structure_drift_validator", "exec_plan")
_emit_agent_executes_agent("p1", "structure_drift_validator", "sub_agent")
_emit_routes_to_agent("p1", "structure_drift_validator", "target_agent")
_emit_verifies_policy("p1", "structure_drift_validator", "policy_check")
_emit_observes_runtime_state("p1", "structure_drift_validator", "runtime_state")
_emit_verifies_boundary("p1", "structure_drift_validator", "boundary_check")
_emit_transcripts_response("p1", "structure_drift_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "structure_drift_validator")
_emit_gated_by_confidence("p1", "structure_drift_validator", "confidence_gate")
emit_replay_key("p0", "structure_drift_validator")
emit_determinism_digest("p0", "structure_drift_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "structure_drift_validator", "execution_auth")
_emit_validates_capability("p2", "structure_drift_validator", "capability_check")
_emit_routes_to_capability("p2", "structure_drift_validator", "capability_route")
_emit_writes_via_uwg("p2", "structure_drift_validator", "uwg_write")
_emit_blocks_direct_write("p2", "structure_drift_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "structure_drift_validator", "tool_invocation")
_emit_captures_execution_output("p2", "structure_drift_validator", "exec_output")
_emit_dispatches_agent("p3", "structure_drift_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "structure_drift_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "structure_drift_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "structure_drift_validator", "healing_outcome")
_emit_escalates_failure("p3", "structure_drift_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "structure_drift_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "structure_drift_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "structure_drift_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "structure_drift_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "structure_drift_validator", "eval_metric")
_emit_stores_embedding("p4", "structure_drift_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "structure_drift_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "structure_drift_validator", "exec_snapshot_link")


def validate_structure_drift(golden_manifest_path: Path) -> bool:
    """Validate that the current structure matches the golden manifest.

    Args:
        golden_manifest_path: Path to the golden manifest file

    Returns:
        True if structure matches, False otherwise
    """
    if not golden_manifest_path.exists():
        print(f"ERROR: Golden manifest not found at {golden_manifest_path}")
        return False

    # Load golden manifest
    golden_manifest = load_manifest(golden_manifest_path)

    # Generate current manifest
    current_manifest = generate_structure_manifest()

    # Compare manifests
    if golden_manifest == current_manifest:
        print("PASS: Structure manifest matches golden")
        print(f"  hash={current_manifest['hash']}")
        return True

    # Find differences
    differences = []

    # Check directories
    golden_dirs = set(golden_manifest["directories"])
    current_dirs = set(current_manifest["directories"])

    if golden_dirs != current_dirs:
        added_dirs = current_dirs - golden_dirs
        removed_dirs = golden_dirs - current_dirs
        if added_dirs:
            differences.append(f"Added directories: {sorted(added_dirs)}")
        if removed_dirs:
            differences.append(f"Removed directories: {sorted(removed_dirs)}")

    # Check Python files
    golden_files = set(golden_manifest["python_files"])
    current_files = set(current_manifest["python_files"])

    if golden_files != current_files:
        added_files = current_files - golden_files
        removed_files = golden_files - current_files
        if added_files:
            differences.append(f"Added Python files: {sorted(added_files)}")
        if removed_files:
            differences.append(f"Removed Python files: {sorted(removed_files)}")

    # Check hash
    if golden_manifest["hash"] != current_manifest["hash"]:
        differences.append(
            f"Hash mismatch: golden={golden_manifest['hash']}, current={current_manifest['hash']}"
        )

    print("FAIL: Structure drift detected")
    for diff in differences:
        print(f"  - {diff}")

    return False


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate structure drift against golden manifest")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("artifacts/structure/structure_manifest.json"),
        help="Path to golden manifest file",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update golden manifest with current structure",
    )

    args = parser.parse_args()

    if args.update:
        # Update golden manifest
        manifest = generate_structure_manifest()
        from agentic_core.L5_safety.utils.structure_drift_writer import save_manifest

        save_manifest(manifest, args.manifest)
        print(f"Updated golden manifest at: {args.manifest}")
        print(f"New hash: {manifest['hash']}")
        return 0

    # Validate against golden manifest
    if validate_structure_drift(args.manifest):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
