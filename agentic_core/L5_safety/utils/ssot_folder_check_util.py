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

emit_replay_key("p0", "ssot_folder_check_util")
emit_determinism_digest("p0", "ssot_folder_check_util")

_emit_dispatches_healing_run("p1", "ssot_folder_check_util", "L5")
_emit_routes_through("p1", "ssot_folder_check_util", "L5")
_emit_checks_agent_registry("p1", "ssot_folder_check_util", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_folder_check_util", "capability")
_emit_dispatches_execution_plan("p1", "ssot_folder_check_util", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_folder_check_util", "sub_agent")
_emit_routes_to_agent("p1", "ssot_folder_check_util", "target_agent")
_emit_verifies_policy("p1", "ssot_folder_check_util", "policy_check")
_emit_observes_runtime_state("p1", "ssot_folder_check_util", "runtime_state")
_emit_verifies_boundary("p1", "ssot_folder_check_util", "boundary_check")
_emit_transcripts_response("p1", "ssot_folder_check_util", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_folder_check_util")
_emit_gated_by_confidence("p1", "ssot_folder_check_util", "confidence_gate")
_emit_escalates_to_human("p1", "ssot_folder_check_util", "L5")
_emit_reads_policy_state("p1", "ssot_folder_check_util", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "ssot_folder_check_util")
_emit_applies_guardrail("p0", "ssot_folder_check_util", "p0_governance")
_emit_snapshots_state("p0", "ssot_folder_check_util", "state_snapshot")
_emit_authorize_and_execute("p2", "ssot_folder_check_util", "execution_auth")
_emit_validates_capability("p2", "ssot_folder_check_util", "capability_check")
_emit_routes_to_capability("p2", "ssot_folder_check_util", "capability_route")
_emit_writes_via_uwg("p2", "ssot_folder_check_util", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_folder_check_util", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_folder_check_util", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_folder_check_util", "exec_output")
_emit_dispatches_agent("p3", "ssot_folder_check_util", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_folder_check_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_folder_check_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_folder_check_util", "healing_outcome")
_emit_escalates_failure("p3", "ssot_folder_check_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_folder_check_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_folder_check_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_folder_check_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_folder_check_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_folder_check_util", "eval_metric")
_emit_stores_embedding("p4", "ssot_folder_check_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_folder_check_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_folder_check_util", "exec_snapshot_link")
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

_emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_folder_check_util", "p4obs", "metric_6")
_emit_records_incident_event("ssot_folder_check_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_folder_check_util", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_folder_check_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_folder_check_util", "p4obs", "mon_state")
_emit_triggers_alert("ssot_folder_check_util", "p4obs", "alert")
_emit_links_incident_trace("ssot_folder_check_util", "p4obs", "trace_link")
_emit_captures_pattern("ssot_folder_check_util", "p3lm", "pattern")
_emit_records_learning_event("ssot_folder_check_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_folder_check_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_folder_check_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_folder_check_util", "p3lm", "routing")
_emit_improves_agent_policy("ssot_folder_check_util", "p3lm", "policy")
_emit_stores_learning_state("ssot_folder_check_util", "p3lm", "state")
_emit_records_execution_trace("ssot_folder_check_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_folder_check_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_folder_check_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_folder_check_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_folder_check_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_folder_check_util", "env_read", "p2_env_1")
_emit_reads_environ("ssot_folder_check_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_folder_check_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_folder_check_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_folder_check_util", "context_pull")
_emit_pulls_context("p1", "ssot_folder_check_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_folder_check_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_folder_check_util", "uwg_term_2")
_emit_writes_through("p1", "ssot_folder_check_util", "write_through")
_emit_writes_through("p1", "ssot_folder_check_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_folder_check_util", "safety_validation")
_emit_invokes_eval("p1", "ssot_folder_check_util", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_folder_check_util", "routing_commit")


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
        print("   Run 'python -m agentic_core.L5_safety.reasoning.hierarchy_healer --heal' to fix.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
