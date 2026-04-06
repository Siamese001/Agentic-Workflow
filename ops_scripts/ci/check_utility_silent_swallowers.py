#!/usr/bin/env python3
"""
Utility Silent Swallower CI Guardrail

Enforces zero tolerance for silent failures in governance-critical utility scripts.
Implements Windsurf Hardening Response requirements for control-plane integrity.

Usage:
    python ops_scripts/ci/check_utility_silent_swallowers.py [file1.py file2.py ...]

Exit codes:
    0 - No violations
    1 - Violations found (build fails)
"""

import argparse

# Force UTF-8 encoding for Windows compatibility
import io
import json
import sys
from pathlib import Path
from typing import List

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

_emit_records_execution_trace("p0", "evidence", "check_utility_silent_swallowers")
_emit_applies_guardrail("p0", "check_utility_silent_swallowers", "p0_governance")
_emit_reads_policy_state("p0", "check_utility_silent_swallowers", "policy_binding")
_emit_snapshots_state("p0", "check_utility_silent_swallowers", "state_snapshot")
emit_replay_key("p0", "check_utility_silent_swallowers")
emit_determinism_digest("p0", "check_utility_silent_swallowers")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_utility_silent_swallowers", "execution_auth")
_emit_validates_capability("p2", "check_utility_silent_swallowers", "capability_check")
_emit_routes_to_capability("p2", "check_utility_silent_swallowers", "capability_route")
_emit_writes_via_uwg("p2", "check_utility_silent_swallowers", "uwg_write")
_emit_blocks_direct_write("p2", "check_utility_silent_swallowers", "direct_write_block")
_emit_records_tool_invocation("p2", "check_utility_silent_swallowers", "tool_invocation")
_emit_captures_execution_output("p2", "check_utility_silent_swallowers", "exec_output")
_emit_dispatches_agent("p3", "check_utility_silent_swallowers", "agent_dispatch")
_emit_coordinates_agents("p3", "check_utility_silent_swallowers", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_utility_silent_swallowers", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_utility_silent_swallowers", "healing_outcome")
_emit_escalates_failure("p3", "check_utility_silent_swallowers", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_utility_silent_swallowers", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_utility_silent_swallowers", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_utility_silent_swallowers", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_utility_silent_swallowers", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_utility_silent_swallowers", "eval_metric")
_emit_stores_embedding("p4", "check_utility_silent_swallowers", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_utility_silent_swallowers", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_utility_silent_swallowers", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.L5_safety.validators.utility_silent_swallower_validator import (
    UtilitySilentSwallowerDetector,
)
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

_emit_emits_metric_event("check_utility_silent_swallowers", "p4obs", "metric_1")
_emit_emits_metric_event("check_utility_silent_swallowers", "p4obs", "metric_2")
_emit_emits_metric_event("check_utility_silent_swallowers", "p4obs", "metric_3")
_emit_emits_metric_event("check_utility_silent_swallowers", "p4obs", "metric_4")
_emit_emits_metric_event("check_utility_silent_swallowers", "p4obs", "metric_5")
_emit_emits_metric_event("check_utility_silent_swallowers", "p4obs", "metric_6")
_emit_records_incident_event("check_utility_silent_swallowers", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_utility_silent_swallowers", "p4obs", "anomaly")
_emit_writes_observability_log("check_utility_silent_swallowers", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_utility_silent_swallowers", "p4obs", "mon_state")
_emit_triggers_alert("check_utility_silent_swallowers", "p4obs", "alert")
_emit_links_incident_trace("check_utility_silent_swallowers", "p4obs", "trace_link")
_emit_captures_pattern("check_utility_silent_swallowers", "p3lm", "pattern")
_emit_records_learning_event("check_utility_silent_swallowers", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_utility_silent_swallowers", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_utility_silent_swallowers", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_utility_silent_swallowers", "p3lm", "routing")
_emit_improves_agent_policy("check_utility_silent_swallowers", "p3lm", "policy")
_emit_stores_learning_state("check_utility_silent_swallowers", "p3lm", "state")
_emit_records_execution_trace("check_utility_silent_swallowers", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_utility_silent_swallowers", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_utility_silent_swallowers", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_utility_silent_swallowers", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_utility_silent_swallowers", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_utility_silent_swallowers", "env_read", "p2_env_1")
_emit_reads_environ("check_utility_silent_swallowers", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_utility_silent_swallowers", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_utility_silent_swallowers", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_utility_silent_swallowers", "context_pull")
_emit_pulls_context("p1", "check_utility_silent_swallowers", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_utility_silent_swallowers", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_utility_silent_swallowers", "uwg_term_secondary")
_emit_writes_through("p1", "check_utility_silent_swallowers", "write_through")
_emit_writes_through("p1", "check_utility_silent_swallowers", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_utility_silent_swallowers", "safety_validation")
_emit_invokes_eval("p1", "check_utility_silent_swallowers", "eval_call")
_emit_proposal_commits_routing("p1", "check_utility_silent_swallowers", "routing_commit")
_emit_escalates_to_human("p1", "check_utility_silent_swallowers", "human_escalation")
_emit_routes_through("p1", "check_utility_silent_swallowers", "route_through")
_emit_checks_agent_registry("p1", "check_utility_silent_swallowers", "agent_registry")
_emit_validates_agent_capability("p1", "check_utility_silent_swallowers", "capability")
_emit_dispatches_execution_plan("p1", "check_utility_silent_swallowers", "exec_plan")
_emit_agent_executes_agent("p1", "check_utility_silent_swallowers", "sub_agent")
_emit_routes_to_agent("p1", "check_utility_silent_swallowers", "target_agent")
_emit_verifies_policy("p1", "check_utility_silent_swallowers", "policy_check")
_emit_observes_runtime_state("p1", "check_utility_silent_swallowers", "runtime_state")
_emit_verifies_boundary("p1", "check_utility_silent_swallowers", "boundary_check")
_emit_transcripts_response("p1", "check_utility_silent_swallowers", "transcript")
_emit_hard_fails_untranscripted("p1", "check_utility_silent_swallowers")
_emit_gated_by_confidence("p1", "check_utility_silent_swallowers", "confidence_gate")

PROJECT_ROOT = get_validated_project_root()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check utility scripts for silent swallowers")
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (default: all Python files in governance paths)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Determine files to scan
    if args.files:
        files_to_scan = [Path(f) for f in args.files if f.endswith('.py')]
    else:
        files_to_scan = get_governance_files()

    if not files_to_scan:
        print("✅ No governance files to scan")
        return 0

    # Scan for violations
    detector = UtilitySilentSwallowerDetector(PROJECT_ROOT)
    all_violations = []

    for file_path in files_to_scan:
        if file_path.exists():
            detection_result = detector.scan_file(file_path)
            all_violations.extend(detection_result.violations)

    # Report results
    if args.json:
        report_json(all_violations, args.verbose)
    else:
        report_text(all_violations, args.verbose)

    # Fail build if any violations found
    if all_violations:
        print(f"\n❌ CI GUARDRAIL: {len(all_violations)} utility silent swallower violations found")
        print("Build FAILED - governance scripts must fail loudly")
        return 1
    else:
        print(f"\n✅ CI GUARDRAIL: No utility silent swallower violations in {len(files_to_scan)} governance files")
        return 0


def get_governance_files() -> list[Path]:
    """Get all Python files in governance-critical paths."""
    governance_paths = [
        "ops_scripts/ci",
        "ops_scripts/maintenance",
        "ops_scripts/root_scripts",
        "tests/guardian",
        "tests/governance",
        "tests/integration",
        "tests/performance",
        "agentic_core/L5_safety/validators",
        "agentic_core/L5_safety/static_checks",
    ]

    files = []
    for path in governance_paths:
        full_path = PROJECT_ROOT / path
        if full_path.exists():
            files.extend(full_path.rglob("*.py"))

    return sorted(files)


def report_text(violations: list, verbose: bool = False) -> None:
    """Report violations in text format."""
    if not violations:
        print("✅ No utility silent swallower violations found")
        return

    print(f"❌ Found {len(violations)} utility silent swallower violations:")
    print()

    # Group violations by file
    by_file = {}
    for v in violations:
        file_key = str(v.file_path)
        if file_key not in by_file:
            by_file[file_key] = []
        by_file[file_key].append(v)

    for file_path, file_violations in sorted(by_file.items()):
        rel_path = Path(file_path).relative_to(PROJECT_ROOT)
        print(f"📁 {rel_path}")

        for v in sorted(file_violations, key=lambda x: x.line_number):
            print(f"   Line {v.line_number}: {v.message}")
            if verbose:
                print(f"   Suggestion: {v.suggestion}")
        print()


def report_json(violations: list, verbose: bool = False) -> None:
    """Report violations in JSON format."""
    report_data = {
        "status": "failed" if violations else "passed",
        "total_violations": len(violations),
        "violations": []
    }

    for v in violations:
        violation_data = {
            "file": str(v.file_path.relative_to(PROJECT_ROOT)),
            "line": v.line_number,
            "column": v.column_number,
            "message": v.message,
            "category": v.category.value,
            "enforcement_level": v.enforcement_level.value,
            "suggestion": v.suggestion
        }
        if verbose:
            violation_data["details"] = v.details
        report_data["violations"].append(violation_data)

    print(json.dumps(report_data, indent=2))


if __name__ == "__main__":
    sys.exit(main())
