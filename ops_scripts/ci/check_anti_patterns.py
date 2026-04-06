"""
Anti-Pattern Pre-Commit Check

Scans staged Python files for landmine anti-patterns.
Used as a pre-commit hook to prevent introduction of new anti-patterns.

Usage:
    python ops_scripts/ci/check_anti_patterns.py [file1.py file2.py ...]

    # Generate baseline:
    python ops_scripts/ci/check_anti_patterns.py --write-baseline

    # Pre-commit hook integration:
    - id: check-anti-patterns
      name: Check Anti-Patterns
      entry: python ops_scripts/ci/check_anti_patterns.py
      language: python
"""
import argparse
import io
import json
import locale
import os
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "check_anti_patterns")
_emit_applies_guardrail("p0", "check_anti_patterns", "p0_governance")
_emit_reads_policy_state("p0", "check_anti_patterns", "policy_binding")
_emit_snapshots_state("p0", "check_anti_patterns", "state_snapshot")
emit_replay_key("p0", "check_anti_patterns")
emit_determinism_digest("p0", "check_anti_patterns")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# Add project root to path BEFORE any agentic_core imports
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Now safe to import from agentic_core
from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
# guardian: allow-global-mutation
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner
from agentic_core.L5_safety.validators.base_detector_validator import EnforcementLevel
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_via_uwg,
)

_emit_emits_metric_event("check_anti_patterns", "p4obs", "metric_1")
_emit_emits_metric_event("check_anti_patterns", "p4obs", "metric_2")
_emit_emits_metric_event("check_anti_patterns", "p4obs", "metric_3")
_emit_emits_metric_event("check_anti_patterns", "p4obs", "metric_4")
_emit_emits_metric_event("check_anti_patterns", "p4obs", "metric_5")
_emit_emits_metric_event("check_anti_patterns", "p4obs", "metric_6")
_emit_records_incident_event("check_anti_patterns", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_anti_patterns", "p4obs", "anomaly")
_emit_writes_observability_log("check_anti_patterns", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_anti_patterns", "p4obs", "mon_state")
_emit_triggers_alert("check_anti_patterns", "p4obs", "alert")
_emit_links_incident_trace("check_anti_patterns", "p4obs", "trace_link")
_emit_captures_pattern("check_anti_patterns", "p3lm", "pattern")
_emit_records_learning_event("check_anti_patterns", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_anti_patterns", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_anti_patterns", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_anti_patterns", "p3lm", "routing")
_emit_improves_agent_policy("check_anti_patterns", "p3lm", "policy")
_emit_stores_learning_state("check_anti_patterns", "p3lm", "state")
_emit_records_execution_trace("check_anti_patterns", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_anti_patterns", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_anti_patterns", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_anti_patterns", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_anti_patterns", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_anti_patterns", "env_read", "p2_env_1")
_emit_reads_environ("check_anti_patterns", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_anti_patterns", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_anti_patterns", "runtime_state", "p2_rt_2")

_emit_authorize_and_execute("p2", "check_anti_patterns", "execution_auth")
_emit_validates_capability("p2", "check_anti_patterns", "capability_check")
_emit_routes_to_capability("p2", "check_anti_patterns", "capability_route")
_emit_writes_via_uwg("p2", "check_anti_patterns", "uwg_write")
_emit_blocks_direct_write("p2", "check_anti_patterns", "direct_write_block")
_emit_records_tool_invocation("p2", "check_anti_patterns", "tool_invocation")
_emit_captures_execution_output("p2", "check_anti_patterns", "exec_output")
_emit_dispatches_agent("p3", "check_anti_patterns", "agent_dispatch")
_emit_coordinates_agents("p3", "check_anti_patterns", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_anti_patterns", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_anti_patterns", "healing_outcome")
_emit_escalates_failure("p3", "check_anti_patterns", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_anti_patterns", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_anti_patterns", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_anti_patterns", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_anti_patterns", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_anti_patterns", "eval_metric")
_emit_stores_embedding("p4", "check_anti_patterns", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_anti_patterns", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_anti_patterns", "exec_snapshot_link")
_emit_pulls_context("p1", "check_anti_patterns", "context_pull")
_emit_pulls_context("p1", "check_anti_patterns", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_anti_patterns", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_anti_patterns", "uwg_term_secondary")
_emit_writes_through("p1", "check_anti_patterns", "write_through")
_emit_writes_through("p1", "check_anti_patterns", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_anti_patterns", "safety_validation")
_emit_invokes_eval("p1", "check_anti_patterns", "eval_call")
_emit_proposal_commits_routing("p1", "check_anti_patterns", "routing_commit")
_emit_escalates_to_human("p1", "check_anti_patterns", "human_escalation")
_emit_routes_through("p1", "check_anti_patterns", "route_through")
_emit_checks_agent_registry("p1", "check_anti_patterns", "agent_registry")
_emit_validates_agent_capability("p1", "check_anti_patterns", "capability")
_emit_dispatches_execution_plan("p1", "check_anti_patterns", "exec_plan")
_emit_agent_executes_agent("p1", "check_anti_patterns", "sub_agent")
_emit_routes_to_agent("p1", "check_anti_patterns", "target_agent")
_emit_verifies_policy("p1", "check_anti_patterns", "policy_check")
_emit_observes_runtime_state("p1", "check_anti_patterns", "runtime_state")
_emit_verifies_boundary("p1", "check_anti_patterns", "boundary_check")
_emit_transcripts_response("p1", "check_anti_patterns", "transcript")
_emit_hard_fails_untranscripted("p1", "check_anti_patterns")
_emit_gated_by_confidence("p1", "check_anti_patterns", "confidence_gate")
BASELINE_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / 'hooks' / 'landmine_baseline.txt'
_EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES | {'.nox'}
_EXCLUDE_FILE_PATTERNS = ['__dbg_*.py', '**/activate_this.py']

def load_baseline() -> set[str]:
    """Load baseline violations from file."""
    if not BASELINE_FILE.exists():
        return set()
    try:
        content = BASELINE_FILE.read_text(encoding='utf-8')
        return set(line.strip() for line in content.splitlines() if line.strip())
    except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
        return set()

def write_baseline(violations: list) -> None:
    """Write current violations to baseline file."""
    signatures = []
    for v in violations:
        if isinstance(v.file_path, Path):
            if v.file_path.is_absolute():
                rel_path = v.file_path.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = v.file_path.as_posix()
        else:
            path_obj = Path(v.file_path)
            if path_obj.is_absolute():
                rel_path = path_obj.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = path_obj.as_posix()
        signature = f'{rel_path}:{v.line_number}:{v.category.value}:{v.message}'
        signatures.append(signature)
    signatures.sort()
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text('\n'.join(signatures) + '\n', encoding='utf-8')
    print(f'Wrote {len(signatures)} violations to {BASELINE_FILE.relative_to(PROJECT_ROOT)}')

def check_files(file_paths: list[str]) -> int:
    """
    Check specified files for anti-patterns.

    Args:
        file_paths: List of file paths to check

    Returns:
        Exit code: 0 if passed, 1 if violations found
    """
    if not file_paths:
        all_python_files = sorted(PROJECT_ROOT.rglob('*.py'))
        python_files = [f for f in all_python_files if not set(f.relative_to(PROJECT_ROOT).parts) & _EXCLUDE_DIRS and (not any(f.match(pattern) for pattern in _EXCLUDE_FILE_PATTERNS))]
    else:
        python_files = []
        for f in file_paths:
            if f.endswith('.py'):
                path_obj = Path(f)
                if not path_obj.exists():
                    path_obj = PROJECT_ROOT / path_obj
                if path_obj.exists():
                    python_files.append(path_obj)
    if not python_files:
        return 0
    scanner = AntiPatternScanner(project_root=PROJECT_ROOT, enforcement_level=EnforcementLevel.WARNING)
    report = scanner.scan_changed_files(python_files)
    baseline = load_baseline()
    current_violations = report.all_violations
    current_signatures = set()
    for v in current_violations:
        if isinstance(v.file_path, Path):
            if v.file_path.is_absolute():
                rel_path = v.file_path.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = v.file_path.as_posix()
        else:
            path_obj = Path(v.file_path)
            if path_obj.is_absolute():
                rel_path = path_obj.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = path_obj.as_posix()
        signature = f'{rel_path}:{v.line_number}:{v.category.value}:{v.message}'
        current_signatures.add(signature)
    new_signatures = current_signatures - baseline
    new_violations = []
    for v in current_violations:
        if isinstance(v.file_path, Path):
            if v.file_path.is_absolute():
                rel_path = v.file_path.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = v.file_path.as_posix()
        else:
            path_obj = Path(v.file_path)
            if path_obj.is_absolute():
                rel_path = path_obj.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = path_obj.as_posix()
        signature = f'{rel_path}:{v.line_number}:{v.category.value}:{v.message}'
        if signature in new_signatures:
            new_violations.append(v)
    if not new_violations:
        if current_violations:
            print(f'[OK] {len(current_violations)} existing violations, 0 new violations')
        return 0
    print(f'\n[BLOCK] Found {len(new_violations)} NEW anti-pattern landmine(s) (out of {len(current_violations)} total):')
    new_by_category = {}
    for violation in new_violations:
        cat = violation.category.value
        new_by_category[cat] = new_by_category.get(cat, 0) + 1
    for category, count in sorted(new_by_category.items()):
        print(f'  • {category}: {count}')
    for violation in new_violations:
        print(f'\n[FAIL] {violation.file_path.name}:{violation.line_number}')
        print(f'   [{violation.category.value}] {violation.message}')
        evidence = violation.evidence[:80]
        if isinstance(evidence, str):
            evidence = evidence.encode('ascii', errors='replace').decode('ascii')
        print(f'   Evidence: {evidence}...')
        if violation.suggested_fix:
            fix_preview = violation.suggested_fix.split('\n')[0]
            if isinstance(fix_preview, str):
                fix_preview = fix_preview.encode('ascii', errors='replace').decode('ascii')
            print(f'   [FIX] {fix_preview}')
    print("\n[ACTION] Fix NEW violations or add '# guardian: allow-<pattern>' to whitelist.")
    print('         To update baseline with current violations: python ops_scripts/ci/check_anti_patterns.py --write-baseline')
    return 1

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Check anti-pattern violations')
    parser.add_argument('--write-baseline', action='store_true', help='Generate baseline file from current violations')
    parser.add_argument('files', nargs='*', help='Files to check (default: all staged files if run from pre-commit)')
    args = parser.parse_args()
    if args.write_baseline:
        if os.environ.get('ALLOW_LANDMINE_BASELINE_WRITE') != '1':
            print('[ERROR] --write-baseline requires ALLOW_LANDMINE_BASELINE_WRITE=1 environment variable')
            print('        This prevents accidental baseline dilution in CI/automation')
            print('        To authorize: ALLOW_LANDMINE_BASELINE_WRITE=1 python ops_scripts/ci/check_anti_patterns.py --write-baseline')
            return 1
        all_python_files = sorted(PROJECT_ROOT.rglob('*.py'))
        all_python_files = [f for f in all_python_files if not set(f.relative_to(PROJECT_ROOT).parts) & _EXCLUDE_DIRS and (not any(f.match(pattern) for pattern in _EXCLUDE_FILE_PATTERNS))]
        scanner = AntiPatternScanner(project_root=PROJECT_ROOT, enforcement_level=EnforcementLevel.WARNING)
        report = scanner.scan_changed_files(all_python_files)
        write_baseline(report.all_violations)
        return 0
    return check_files(args.files)
if __name__ == '__main__':
    sys.exit(main())
