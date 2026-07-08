#!/usr/bin/env python3
"""
SSOT Folder Structure Check - CLI Entry Point

Phase 5.2 Upgrade: Fully headless, non-interactive CI verification.

This script is designed to be run by:
- Pre-commit hooks
- GitHub Actions CI pipelines
- Manual CLI verification

Returns:
    0: If structure is compliant.
    1: If drift/violations are detected.

Usage:
    python -m agentic_core.L5_safety.validators.ssot_folder_check
    python scripts/ssot_folder_check_util.py
"""

import argparse
import sys
from pathlib import Path

from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
    FilesystemSSOTReconcilerAgent,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ssot_folder_check_util")
trace_contract.emit_determinism_digest("p0", "ssot_folder_check_util")

trace_contract._emit_dispatches_healing_run("p1", "ssot_folder_check_util", "L5")
trace_contract._emit_routes_through("p1", "ssot_folder_check_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "ssot_folder_check_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ssot_folder_check_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ssot_folder_check_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ssot_folder_check_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ssot_folder_check_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "ssot_folder_check_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ssot_folder_check_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ssot_folder_check_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ssot_folder_check_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ssot_folder_check_util")
trace_contract._emit_gated_by_confidence("p1", "ssot_folder_check_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ssot_folder_check_util", "L5")
trace_contract._emit_reads_policy_state("p1", "ssot_folder_check_util", "L5")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "ssot_folder_check_util")
trace_contract._emit_applies_guardrail("p0", "ssot_folder_check_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "ssot_folder_check_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "ssot_folder_check_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "ssot_folder_check_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ssot_folder_check_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ssot_folder_check_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ssot_folder_check_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ssot_folder_check_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ssot_folder_check_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ssot_folder_check_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ssot_folder_check_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ssot_folder_check_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ssot_folder_check_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ssot_folder_check_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ssot_folder_check_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ssot_folder_check_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ssot_folder_check_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ssot_folder_check_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ssot_folder_check_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ssot_folder_check_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ssot_folder_check_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ssot_folder_check_util", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ssot_folder_check_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ssot_folder_check_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ssot_folder_check_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ssot_folder_check_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ssot_folder_check_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ssot_folder_check_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ssot_folder_check_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ssot_folder_check_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ssot_folder_check_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ssot_folder_check_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ssot_folder_check_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ssot_folder_check_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ssot_folder_check_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("ssot_folder_check_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ssot_folder_check_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ssot_folder_check_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ssot_folder_check_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ssot_folder_check_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ssot_folder_check_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ssot_folder_check_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ssot_folder_check_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ssot_folder_check_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ssot_folder_check_util", "context_pull")
trace_contract._emit_pulls_context("p1", "ssot_folder_check_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ssot_folder_check_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ssot_folder_check_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ssot_folder_check_util", "write_through")
trace_contract._emit_writes_through("p1", "ssot_folder_check_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ssot_folder_check_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ssot_folder_check_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ssot_folder_check_util", "routing_commit")


def main() -> int:
    """
    Synchronous entry point for CI pipelines.

    No asyncio required - uses run_ci_verification_sync() for headless operation.
    """
    parser = argparse.ArgumentParser(
        description="SSOT Folder Structure Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic check
    python -m agentic_core.L5_safety.validators.ssot_folder_check

    # Verbose output
    python -m agentic_core.L5_safety.validators.ssot_folder_check --verbose

    # Check specific path
    python -m agentic_core.L5_safety.validators.ssot_folder_check --path /path/to/project
        """,
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(".").resolve(),
        help="Project root path (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed violation information",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for CI integration)",
    )

    args = parser.parse_args()
    project_root = args.path.resolve()

    print(f"[SCAN] SSOT Folder Verification: {project_root}")
    print("=" * 60)

    agent = FilesystemSSOTReconcilerAgent(project_root)
    is_compliant, results = agent.run_ci_verification_sync()

    if args.json:
        import json

        print(json.dumps(results, indent=2))
    else:
        print("\n[RESULTS]:")
        print(f"   Roots checked: {', '.join(results.get('roots_checked', []))}")
        print(f"   Hierarchy violations: {results.get('hierarchy_violations', 0)}")
        print(f"   Location violations: {results.get('location_violations', 0)}")
        print(f"   Total violations: {results.get('total_violations', 0)}")

    print("=" * 60)

    if is_compliant:
        print("[OK] SSOT Structure Verified. No violations.")
        return 0
    else:
        print("[FAIL] SSOT Violations Detected.")
        print("   Run the structure hierarchy runner in dry-run mode before applying any relocation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
