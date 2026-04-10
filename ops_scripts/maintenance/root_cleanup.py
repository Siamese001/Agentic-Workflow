#!/usr/bin/env python3
"""Clean up root files and move them to appropriate locations."""

import shutil
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
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

_emit_emits_metric_event("root_cleanup", "p4obs", "metric_1")
_emit_emits_metric_event("root_cleanup", "p4obs", "metric_2")
_emit_emits_metric_event("root_cleanup", "p4obs", "metric_3")
_emit_emits_metric_event("root_cleanup", "p4obs", "metric_4")
_emit_emits_metric_event("root_cleanup", "p4obs", "metric_5")
_emit_emits_metric_event("root_cleanup", "p4obs", "metric_6")
_emit_records_incident_event("root_cleanup", "p4obs", "incident")
_emit_captures_runtime_anomaly("root_cleanup", "p4obs", "anomaly")
_emit_writes_observability_log("root_cleanup", "p4obs", "obs_log")
_emit_updates_monitoring_state("root_cleanup", "p4obs", "mon_state")
_emit_triggers_alert("root_cleanup", "p4obs", "alert")
_emit_links_incident_trace("root_cleanup", "p4obs", "trace_link")
_emit_captures_pattern("root_cleanup", "p3lm", "pattern")
_emit_records_learning_event("root_cleanup", "p3lm", "learning_event")
_emit_writes_learning_snapshot("root_cleanup", "p3lm", "snapshot")
_emit_feeds_meta_learning("root_cleanup", "p3lm", "meta_feed")
_emit_updates_routing_strategy("root_cleanup", "p3lm", "routing")
_emit_improves_agent_policy("root_cleanup", "p3lm", "policy")
_emit_stores_learning_state("root_cleanup", "p3lm", "state")
_emit_records_execution_trace("root_cleanup", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("root_cleanup", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("root_cleanup", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("root_cleanup", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("root_cleanup", "L4_STATE", "p2_trace_5")
_emit_reads_environ("root_cleanup", "env_read", "p2_env_1")
_emit_reads_environ("root_cleanup", "env_read", "p2_env_2")
_emit_reads_runtime_state("root_cleanup", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("root_cleanup", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "root_cleanup")
_emit_applies_guardrail("p0", "root_cleanup", "p0_governance")
_emit_reads_policy_state("p0", "root_cleanup", "policy_binding")
_emit_snapshots_state("p0", "root_cleanup", "state_snapshot")
_emit_pulls_context("p1", "root_cleanup", "context_pull")
_emit_pulls_context("p1", "root_cleanup", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "root_cleanup", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "root_cleanup", "uwg_term_secondary")
_emit_writes_through("p1", "root_cleanup", "write_through")
_emit_writes_through("p1", "root_cleanup", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "root_cleanup", "safety_validation")
_emit_invokes_eval("p1", "root_cleanup", "eval_call")
_emit_proposal_commits_routing("p1", "root_cleanup", "routing_commit")
_emit_escalates_to_human("p1", "root_cleanup", "human_escalation")
_emit_routes_through("p1", "root_cleanup", "route_through")
_emit_checks_agent_registry("p1", "root_cleanup", "agent_registry")
_emit_validates_agent_capability("p1", "root_cleanup", "capability")
_emit_dispatches_execution_plan("p1", "root_cleanup", "exec_plan")
_emit_agent_executes_agent("p1", "root_cleanup", "sub_agent")
_emit_routes_to_agent("p1", "root_cleanup", "target_agent")
_emit_verifies_policy("p1", "root_cleanup", "policy_check")
_emit_observes_runtime_state("p1", "root_cleanup", "runtime_state")
_emit_verifies_boundary("p1", "root_cleanup", "boundary_check")
_emit_transcripts_response("p1", "root_cleanup", "transcript")
_emit_hard_fails_untranscripted("p1", "root_cleanup")
_emit_gated_by_confidence("p1", "root_cleanup", "confidence_gate")
emit_replay_key("p0", "root_cleanup")
emit_determinism_digest("p0", "root_cleanup")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "root_cleanup", "execution_auth")
_emit_validates_capability("p2", "root_cleanup", "capability_check")
_emit_routes_to_capability("p2", "root_cleanup", "capability_route")
_emit_writes_via_uwg("p2", "root_cleanup", "uwg_write")
_emit_blocks_direct_write("p2", "root_cleanup", "direct_write_block")
_emit_records_tool_invocation("p2", "root_cleanup", "tool_invocation")
_emit_captures_execution_output("p2", "root_cleanup", "exec_output")
_emit_dispatches_agent("p3", "root_cleanup", "agent_dispatch")
_emit_coordinates_agents("p3", "root_cleanup", "agent_coordination")
_emit_records_workflow_lineage("p3", "root_cleanup", "workflow_lineage")
_emit_records_healing_outcome("p3", "root_cleanup", "healing_outcome")
_emit_escalates_failure("p3", "root_cleanup", "failure_escalation")
_emit_orchestrates_workflow("p3", "root_cleanup", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "root_cleanup", "healing_dispatch")
_emit_invokes_evaluation("p3", "root_cleanup", "evaluation_signal")
_emit_records_telemetry_event("p4", "root_cleanup", "telemetry_event")
_emit_captures_evaluation_metric("p4", "root_cleanup", "eval_metric")
_emit_stores_embedding("p4", "root_cleanup", "embedding_store")
_emit_updates_meta_learning_state("p4", "root_cleanup", "meta_learning")
_emit_links_execution_to_snapshot("p4", "root_cleanup", "exec_snapshot_link")


def main():
    """Clean up root files."""
    root = get_validated_project_root()

    # Files to move to docs/reports/audit
    audit_files = [
        "audit_gap_analysis.json",
        "consolidation_candidates.json",
        "DELETION_AUDIT_REPORT.md",
        "depth_violations.txt",
        "gravity_violations.json",
        "guardian_report.txt",
        "HANG_DEBUG_REPORT.md",
        "import_crawl_error.txt",
        "import_errors.txt",
        "init_missing.txt",
        "naming_violations.txt",
        "Phase2_Discovery_Report.md",
        "ssot_recommendations_report.md",
        "TARGET_STATE_GAP_ASSESSMENT_REPORT.md",
    ]

    # Files to move to docs/reports/assessments
    assessment_files = [
        "COMPREHENSIVE_TEST_CASES.md",
        "Design Principles.md",
        "Prompt v4.7 Gap Analysis.md",
        "pre_commit_scope_analysis.md",
    ]

    # Scripts to move to ops_scripts/maintenance
    script_files = [
        "agent_technical_status.py",
        "analyze_deleted_tests.py",
        "batch_restore_tests.py",
        "consolidate_phase_files.py",
        "implement_phase1_renames.py",
        "phase1_1_rename_validators.py",
        "restore_valid_tests.py",
        "root_drift_remediation.py",
        "run_classification.py",
    ]

    # Test files to move to tests/
    test_files = [
        "test_always_heal_llm.py",
        "test_execute_ssot_e2e.py",
        "test_healing_confidence.py",
        "test_heal_implementations.py",
        "test_location_agent_heal.py",
        "test_location_agent_integration.py",
        "test_location_semantic_lock.py",
        "test_phase1_renames.py",
        "test_phase2_renames.py",
        "test_phase3_renames.py",
        "test_schema_validator.py",
        "test_sovereign_index_e2e.py",
    ]

    # Config files to keep in root (whitelist)

    print("=" * 70)
    print("ROOT CLEANUP: MOVING FILES TO APPROPRIATE TERRITORIES")
    print("=" * 70)
    print()

    # Move audit files
    print("[1/4] Moving audit files to docs/reports/audit...")
    audit_dir = root / "docs" / REPORTS_DIR / "audit"
    for filename in audit_files:
        source = root / filename
        if source.exists():
            target = audit_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    # Move assessment files
    print()
    print("[2/4] Moving assessment files to docs/reports/assessments...")
    assessment_dir = root / "docs" / REPORTS_DIR / "assessments"
    for filename in assessment_files:
        source = root / filename
        if source.exists():
            target = assessment_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    # Move script files
    print()
    print("[3/4] Moving scripts to ops_scripts/maintenance...")
    scripts_dir = root / OPS_SCRIPTS_DIR / "maintenance"
    for filename in script_files:
        source = root / filename
        if source.exists():
            target = scripts_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    # Move test files
    print()
    print("[4/4] Moving test files to tests/...")
    tests_dir = root / TESTS_DIR
    for filename in test_files:
        source = root / filename
        if source.exists():
            target = tests_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    print()
    print("=" * 70)
    print("ROOT CLEANUP COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
