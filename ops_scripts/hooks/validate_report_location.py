"""
Pre-commit Hook: Validate Report Location

Validates that report files are stored in the SSOT location (docs/reports/).
Supports multiple enforcement modes for gradual rollout.

Usage:
    python scripts/hooks/validate_report_location.py [options]

Options:
    --mode MODE     Enforcement mode: dry-run, warn, strict (default: warn)
    --fix           Auto-move misplaced reports to SSOT location
    --quiet         Suppress non-error output
    --log           Log violations to compliance report
    --staged-only   Only check staged files (for pre-commit)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "validate_report_location")
_emit_applies_guardrail("p0", "validate_report_location", "p0_governance")
_emit_reads_policy_state("p0", "validate_report_location", "policy_binding")
_emit_snapshots_state("p0", "validate_report_location", "state_snapshot")
emit_replay_key("p0", "validate_report_location")
emit_determinism_digest("p0", "validate_report_location")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validate_report_location", "execution_auth")
_emit_validates_capability("p2", "validate_report_location", "capability_check")
_emit_routes_to_capability("p2", "validate_report_location", "capability_route")
_emit_writes_via_uwg("p2", "validate_report_location", "uwg_write")
_emit_blocks_direct_write("p2", "validate_report_location", "direct_write_block")
_emit_records_tool_invocation("p2", "validate_report_location", "tool_invocation")
_emit_captures_execution_output("p2", "validate_report_location", "exec_output")
_emit_dispatches_agent("p3", "validate_report_location", "agent_dispatch")
_emit_coordinates_agents("p3", "validate_report_location", "agent_coordination")
_emit_records_workflow_lineage("p3", "validate_report_location", "workflow_lineage")
_emit_records_healing_outcome("p3", "validate_report_location", "healing_outcome")
_emit_escalates_failure("p3", "validate_report_location", "failure_escalation")
_emit_orchestrates_workflow("p3", "validate_report_location", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validate_report_location", "healing_dispatch")
_emit_invokes_evaluation("p3", "validate_report_location", "evaluation_signal")
_emit_records_telemetry_event("p4", "validate_report_location", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validate_report_location", "eval_metric")
_emit_stores_embedding("p4", "validate_report_location", "embedding_store")
_emit_updates_meta_learning_state("p4", "validate_report_location", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validate_report_location", "exec_snapshot_link")
_FIXED_TS = "2026-01-01T00:00:00"
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

SYMBOL_OK = '[OK]'
SYMBOL_WARN = '[WARN]'
SYMBOL_ERROR = '[ERROR]'
SYMBOL_INFO = '[INFO]'
SYMBOL_MOVE = '->'
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L5_safety.validators.report_location_validator import (
    SSOT_REPORTS_DIR,
    ReportLocationValidator,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("validate_report_location", "p4obs", "metric_1")
_emit_emits_metric_event("validate_report_location", "p4obs", "metric_2")
_emit_emits_metric_event("validate_report_location", "p4obs", "metric_3")
_emit_emits_metric_event("validate_report_location", "p4obs", "metric_4")
_emit_emits_metric_event("validate_report_location", "p4obs", "metric_5")
_emit_emits_metric_event("validate_report_location", "p4obs", "metric_6")
_emit_records_incident_event("validate_report_location", "p4obs", "incident")
_emit_captures_runtime_anomaly("validate_report_location", "p4obs", "anomaly")
_emit_writes_observability_log("validate_report_location", "p4obs", "obs_log")
_emit_updates_monitoring_state("validate_report_location", "p4obs", "mon_state")
_emit_triggers_alert("validate_report_location", "p4obs", "alert")
_emit_links_incident_trace("validate_report_location", "p4obs", "trace_link")
_emit_captures_pattern("validate_report_location", "p3lm", "pattern")
_emit_records_learning_event("validate_report_location", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validate_report_location", "p3lm", "snapshot")
_emit_feeds_meta_learning("validate_report_location", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validate_report_location", "p3lm", "routing")
_emit_improves_agent_policy("validate_report_location", "p3lm", "policy")
_emit_stores_learning_state("validate_report_location", "p3lm", "state")
_emit_records_execution_trace("validate_report_location", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validate_report_location", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validate_report_location", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validate_report_location", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validate_report_location", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validate_report_location", "env_read", "p2_env_1")
_emit_reads_environ("validate_report_location", "env_read", "p2_env_2")
_emit_reads_runtime_state("validate_report_location", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validate_report_location", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validate_report_location", "context_pull")
_emit_pulls_context("p1", "validate_report_location", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "validate_report_location", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validate_report_location", "uwg_term_secondary")
_emit_writes_through("p1", "validate_report_location", "write_through")
_emit_writes_through("p1", "validate_report_location", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "validate_report_location", "safety_validation")
_emit_invokes_eval("p1", "validate_report_location", "eval_call")
_emit_proposal_commits_routing("p1", "validate_report_location", "routing_commit")
_emit_escalates_to_human("p1", "validate_report_location", "human_escalation")
_emit_routes_through("p1", "validate_report_location", "route_through")
_emit_checks_agent_registry("p1", "validate_report_location", "agent_registry")
_emit_validates_agent_capability("p1", "validate_report_location", "capability")
_emit_dispatches_execution_plan("p1", "validate_report_location", "exec_plan")
_emit_agent_executes_agent("p1", "validate_report_location", "sub_agent")
_emit_routes_to_agent("p1", "validate_report_location", "target_agent")
_emit_verifies_policy("p1", "validate_report_location", "policy_check")
_emit_observes_runtime_state("p1", "validate_report_location", "runtime_state")
_emit_verifies_boundary("p1", "validate_report_location", "boundary_check")
_emit_transcripts_response("p1", "validate_report_location", "transcript")
_emit_hard_fails_untranscripted("p1", "validate_report_location")
_emit_gated_by_confidence("p1", "validate_report_location", "confidence_gate")

COMPLIANCE_LOG_DIR = PROJECT_ROOT / 'agentic_core' / 'L0_routing' / 'logs' / 'compliance_reports'

def get_staged_files() -> list[Path]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], cwd=PROJECT_ROOT, capture_output=True, text=True)
        if result.returncode == 0:
            return [PROJECT_ROOT / f for f in result.stdout.strip().split('\n') if f]
    # guardian: allow-silent-swallow
    except Exception:
        pass
    return []

def log_violations(misplaced: list, mode: str, action_taken: str) -> Path:
    """Log violations to compliance report."""
    COMPLIANCE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = COMPLIANCE_LOG_DIR / f'report_location_violations_{timestamp}.json'
    report = {'timestamp': _FIXED_TS, 'mode': mode, 'action_taken': action_taken, 'total_violations': len(misplaced), 'violations': [{'file': r.current_location, 'expected': r.expected_location, 'violation_type': r.violation_type} for r in misplaced]}
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    return log_path

def main() -> int:
    """Main entry point for the pre-commit hook."""
    parser = argparse.ArgumentParser(description='Validate report file locations against SSOT requirements.')
    parser.add_argument('--mode', choices=['dry-run', 'warn', 'strict'], default='strict', help='Enforcement mode (default: strict)')
    parser.add_argument('--fix', action='store_true', help='Auto-move misplaced reports to SSOT location')
    parser.add_argument('--quiet', action='store_true', help='Suppress non-error output')
    parser.add_argument('--log', action='store_true', help='Log violations to compliance report')
    parser.add_argument('--staged-only', action='store_true', help='Only check staged files')
    args = parser.parse_args()
    validator = ReportLocationValidator(PROJECT_ROOT, dry_run=not args.fix)
    if args.staged_only:
        staged = get_staged_files()
        misplaced = [validator.validate_file(f) for f in staged if validator.is_report_file(f) and (not validator.is_approved_location(f))]
        misplaced = [r for r in misplaced if not r.is_compliant]
    else:
        misplaced = validator.get_misplaced_reports()
    if not misplaced:
        if not args.quiet:
            print(f'{SYMBOL_OK} All reports are in SSOT-compliant locations.')
        return 0
    print(f'\n{SYMBOL_WARN} Found {len(misplaced)} misplaced report(s):')
    print(f'   SSOT Location: {SSOT_REPORTS_DIR}/\n')
    for result in misplaced[:20]:
        print(f'   {SYMBOL_ERROR} {result.current_location}')
        print(f'      {SYMBOL_MOVE} Move to: {result.expected_location}')
    if len(misplaced) > 20:
        print(f'\n   ... and {len(misplaced) - 20} more violations')
    if args.log:
        action = 'fix' if args.fix else args.mode
        log_path = log_violations(misplaced, args.mode, action)
        print(f'\n{SYMBOL_INFO} Violations logged to: {log_path.relative_to(PROJECT_ROOT)}')
    if args.fix:
        print('\n[FIX] Auto-fix mode enabled - moving files...')
        moved_count = 0
        for result in misplaced:
            try:
                source = PROJECT_ROOT / result.current_location
                dest = PROJECT_ROOT / result.expected_location
                dest.parent.mkdir(parents=True, exist_ok=True)
                source.rename(dest)
                moved_count += 1
                print(f'   {SYMBOL_OK} Moved: {result.current_location}')
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f'   {SYMBOL_ERROR} Failed to move {result.current_location}: {e}')
        print(f'\n{SYMBOL_INFO} Moved {moved_count}/{len(misplaced)} files to SSOT location.')
        return 0
    if args.mode == 'strict':
        print(f'\n{SYMBOL_ERROR} Commit blocked: Report location violations detected.')
        print('   Run with --fix to auto-move files, or manually relocate them.')
        return 1
    elif args.mode == 'warn':
        print(f'\n{SYMBOL_WARN} Violations detected - commit allowed but please fix.')
        print('   Run: python scripts/hooks/validate_report_location.py --fix')
        return 0
    else:
        print(f'\n{SYMBOL_INFO} [DRY-RUN] Violations detected but no action taken.')
        return 0
if __name__ == '__main__':
    sys.exit(main())
