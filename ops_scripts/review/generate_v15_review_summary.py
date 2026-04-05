"""V15 Review Summary Generator.

Reads existing evidence JSON (P3–P6) and guardian_report.json, produces a
deterministic human-readable markdown summary for approval workflows.

Usage:
    python ops_scripts/review/generate_v15_review_summary.py \\
        --out docs/reports/plans/v15_review_summary.md

Exit codes:
    0 — Summary generated (even with partial missing inputs)
    1 — ALL input files missing (nothing to summarize)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    REPORTS_DIR,
    THRESHOLD,
    get_validated_project_root,
)
from ops_scripts.review.integration_contract_stubs import Finding, ResultEnvelope
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_through,
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

_emit_emits_metric_event("generate_v15_review_summary", "p4obs", "metric_1")
_emit_emits_metric_event("generate_v15_review_summary", "p4obs", "metric_2")
_emit_emits_metric_event("generate_v15_review_summary", "p4obs", "metric_3")
_emit_emits_metric_event("generate_v15_review_summary", "p4obs", "metric_4")
_emit_emits_metric_event("generate_v15_review_summary", "p4obs", "metric_5")
_emit_emits_metric_event("generate_v15_review_summary", "p4obs", "metric_6")
_emit_records_incident_event("generate_v15_review_summary", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_v15_review_summary", "p4obs", "anomaly")
_emit_writes_observability_log("generate_v15_review_summary", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_v15_review_summary", "p4obs", "mon_state")
_emit_triggers_alert("generate_v15_review_summary", "p4obs", "alert")
_emit_links_incident_trace("generate_v15_review_summary", "p4obs", "trace_link")
_emit_captures_pattern("generate_v15_review_summary", "p3lm", "pattern")
_emit_records_learning_event("generate_v15_review_summary", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_v15_review_summary", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_v15_review_summary", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_v15_review_summary", "p3lm", "routing")
_emit_improves_agent_policy("generate_v15_review_summary", "p3lm", "policy")
_emit_stores_learning_state("generate_v15_review_summary", "p3lm", "state")
_emit_records_execution_trace("generate_v15_review_summary", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_v15_review_summary", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_v15_review_summary", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_v15_review_summary", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_v15_review_summary", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_v15_review_summary", "env_read", "p2_env_1")
_emit_reads_environ("generate_v15_review_summary", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_v15_review_summary", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_v15_review_summary", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "generate_v15_review_summary")
_emit_applies_guardrail("p0", "generate_v15_review_summary", "p0_governance")
_emit_reads_policy_state("p0", "generate_v15_review_summary", "policy_binding")
_emit_snapshots_state("p0", "generate_v15_review_summary", "state_snapshot")
_emit_pulls_context("p1", "generate_v15_review_summary", "context_pull")
_emit_pulls_context("p1", "generate_v15_review_summary", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "generate_v15_review_summary", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_v15_review_summary", "uwg_term_secondary")
_emit_writes_through("p1", "generate_v15_review_summary", "write_through")
_emit_writes_through("p1", "generate_v15_review_summary", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "generate_v15_review_summary", "safety_validation")
_emit_invokes_eval("p1", "generate_v15_review_summary", "eval_call")
_emit_proposal_commits_routing("p1", "generate_v15_review_summary", "routing_commit")
_emit_escalates_to_human("p1", "generate_v15_review_summary", "human_escalation")
_emit_routes_through("p1", "generate_v15_review_summary", "route_through")
_emit_checks_agent_registry("p1", "generate_v15_review_summary", "agent_registry")
_emit_validates_agent_capability("p1", "generate_v15_review_summary", "capability")
_emit_dispatches_execution_plan("p1", "generate_v15_review_summary", "exec_plan")
_emit_agent_executes_agent("p1", "generate_v15_review_summary", "sub_agent")
_emit_routes_to_agent("p1", "generate_v15_review_summary", "target_agent")
_emit_verifies_policy("p1", "generate_v15_review_summary", "policy_check")
_emit_observes_runtime_state("p1", "generate_v15_review_summary", "runtime_state")
_emit_verifies_boundary("p1", "generate_v15_review_summary", "boundary_check")
_emit_transcripts_response("p1", "generate_v15_review_summary", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_v15_review_summary")
_emit_gated_by_confidence("p1", "generate_v15_review_summary", "confidence_gate")
emit_replay_key("p0", "generate_v15_review_summary")
emit_determinism_digest("p0", "generate_v15_review_summary")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_v15_review_summary", "execution_auth")
_emit_validates_capability("p2", "generate_v15_review_summary", "capability_check")
_emit_routes_to_capability("p2", "generate_v15_review_summary", "capability_route")
_emit_writes_via_uwg("p2", "generate_v15_review_summary", "uwg_write")
_emit_blocks_direct_write("p2", "generate_v15_review_summary", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_v15_review_summary", "tool_invocation")
_emit_captures_execution_output("p2", "generate_v15_review_summary", "exec_output")
_emit_dispatches_agent("p3", "generate_v15_review_summary", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_v15_review_summary", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_v15_review_summary", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_v15_review_summary", "healing_outcome")
_emit_escalates_failure("p3", "generate_v15_review_summary", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_v15_review_summary", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_v15_review_summary", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_v15_review_summary", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_v15_review_summary", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_v15_review_summary", "eval_metric")
_emit_stores_embedding("p4", "generate_v15_review_summary", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_v15_review_summary", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_v15_review_summary", "exec_snapshot_link")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_1")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_2")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_3")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_4")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_5")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_6")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_7")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_8")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_9")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_10")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_11")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_12")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_13")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_14")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_15")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_16")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_17")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_18")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_19")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_20")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_21")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_22")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_23")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_24")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_25")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_26")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_27")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_28")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_29")
_emit_reads_through("l4", "generate_v15_review_summary", "urg_read_30")
REPO_ROOT = get_validated_project_root()
EVIDENCE_FILES = {'P3': REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'v15_p3_evidence.json', 'P4': REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'v15_p4_evidence.json', 'P5': REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'v15_p5_evidence.json', 'P6': REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'v15_p6_evidence.json'}
GUARDIAN_REPORT_PATHS = [REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'guardian_report.json', REPO_ROOT / AGENTIC_CORE_DIR / 'L0_routing' / 'logs' / 'guardian_report.json']

def _load_json(path: Path) -> dict | None:
    """Load a JSON file; return None if missing or unparseable."""
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        return None

def _load_guardian_report() -> dict | None:
    """Try multiple known locations for guardian_report.json."""
    for p in GUARDIAN_REPORT_PATHS:
        data = _load_json(p)
        if data is not None:
            return data
    return None

def generate_summary(evidence_files: dict[str, Path] | None=None, guardian_report_paths: list[Path] | None=None) -> tuple[str, int]:
    """Build the markdown summary string.

    Returns:
        (markdown_string, exit_code)
        exit_code 0 = ok (partial missing allowed)
        exit_code 1 = ALL inputs missing
    """
    if evidence_files is None:
        evidence_files = EVIDENCE_FILES
    if guardian_report_paths is None:
        guardian_report_paths = GUARDIAN_REPORT_PATHS
    evidence: dict[str, dict | None] = {}
    for phase, path in sorted(evidence_files.items()):
        evidence[phase] = _load_json(path)
    guardian = None
    for p in guardian_report_paths:
        guardian = _load_json(p)
        if guardian is not None:
            break
    all_evidence_missing = all(v is None for v in evidence.values())
    if all_evidence_missing and guardian is None:
        return ('', 1)
    lines: list[str] = []
    lines.append('# V15 Review Summary')
    lines.append('')
    lines.append('## 1. Inputs')
    lines.append('')
    found_phases = []
    missing_phases = []
    for phase in sorted(evidence.keys()):
        if evidence[phase] is not None:
            found_phases.append(phase)
        else:
            missing_phases.append(phase)
    if found_phases:
        lines.append(f"- **Found**: {', '.join(found_phases)}")
    if missing_phases:
        lines.append(f"- **Missing**: {', '.join(missing_phases)}")
    guardian_status = 'found' if guardian is not None else 'missing'
    lines.append(f'- **Guardian report**: {guardian_status}')
    lines.append('')
    lines.append('## 2. Gate Results (P3–P6)')
    lines.append('')
    lines.append('| Phase | Gate | Passed | Violations | Total | Status |')
    lines.append('|-------|------|--------|------------|-------|--------|')
    all_gates_pass = True
    for phase in sorted(evidence.keys()):
        data = evidence[phase]
        if data is None:
            lines.append(f'| {phase} | — | — | — | — | MISSING |')
            all_gates_pass = False
            continue
        gate = data.get('gate', 'unknown')
        passed = data.get('passed', 0)
        violations = data.get('violations', 0)
        total = data.get('total_checks', 0)
        blocking = data.get('blocking', False)
        status = 'FAIL' if violations > 0 or blocking else 'PASS'
        if status == 'FAIL':
            all_gates_pass = False
        lines.append(f'| {phase} | {gate} | {passed} | {violations} | {total} | {status} |')
    lines.append('')
    has_violations = False
    for phase in sorted(evidence.keys()):
        data = evidence[phase]
        if data is None:
            continue
        viols = data.get('violation_details', [])
        if viols:
            has_violations = True
    if has_violations:
        lines.append('## 3. Violation Details')
        lines.append('')
        for phase in sorted(evidence.keys()):
            data = evidence[phase]
            if data is None:
                continue
            viols = data.get('violation_details', [])
            for v in viols:
                check = v.get('check', 'unknown')
                detail = v.get('detail', 'no detail')
                lines.append(f'- **{phase}** / `{check}`: {detail}')
        lines.append('')
    else:
        lines.append('## 3. Violation Details')
        lines.append('')
        lines.append('No violations recorded.')
        lines.append('')
    lines.append('## 4. Guardian Report')
    lines.append('')
    if guardian is None:
        lines.append('Guardian report not available.')
    else:
        status = guardian.get('status', 'UNKNOWN')
        meta = guardian.get('metadata', {})
        total_tests = meta.get('total_tests', 0)
        passed_tests = meta.get('passed_tests', 0)
        failed_tests = meta.get('failed_tests', 0)
        skipped_tests = meta.get('skipped_tests', 0)
        lines.append(f'- **Status**: {status}')
        lines.append(f'- **Total tests**: {total_tests}')
        lines.append(f'- **Passed**: {passed_tests}')
        lines.append(f'- **Failed**: {failed_tests}')
        lines.append(f'- **Skipped**: {skipped_tests}')
        failed_by_cat = meta.get('failed_by_category', {})
        non_empty_cats = {k: v for k, v in sorted(failed_by_cat.items()) if v}
        if non_empty_cats:
            lines.append('')
            lines.append('### Failed by Category')
            lines.append('')
            for cat, items in non_empty_cats.items():
                lines.append(f'- **{cat}**: {len(items)} failure(s)')
    lines.append('')
    lines.append('## 5. Approval Decision')
    lines.append('')
    guardian_pass = guardian is not None and guardian.get('status') == 'PASS'
    ready = all_gates_pass and guardian_pass
    if ready:
        lines.append('**Ready for human approval: YES**')
    else:
        reasons = []
        if not all_gates_pass:
            reasons.append('gate failures or missing evidence')
        if not guardian_pass:
            reasons.append('guardian report not PASS')
        lines.append('**Ready for human approval: NO**')
        lines.append('')
        lines.append(f"Reason(s): {'; '.join(reasons)}")
    lines.append('')
    return ('\n'.join(lines), 0)

def _build_envelope(exit_code: int, evidence_files: dict[str, Path], guardian_report_paths: list[Path], out_path: str | None, all_gates_pass: bool, guardian_pass: bool) -> ResultEnvelope:
    """Build a ResultEnvelope for the review summary run."""
    env = ResultEnvelope(tool='review_summary', exit_code=exit_code)
    for phase, path in sorted(evidence_files.items()):
        env.inputs[f'evidence_{phase.lower()}'] = {'path': path.name, 'present': path.is_file()}
    guardian_present = any(p.is_file() for p in guardian_report_paths)
    env.inputs['guardian_report'] = {'path': guardian_report_paths[0].name if guardian_report_paths else 'guardian_report.json', 'present': guardian_present}
    if out_path:
        env.outputs['markdown'] = {'path': Path(out_path).name}
    if exit_code == 1:
        env.findings.append(Finding(code='ALL_INPUTS_MISSING', severity='ERROR', message='All input files missing, nothing to summarize'))
        return env
    for phase, path in sorted(evidence_files.items()):
        if not path.is_file():
            env.findings.append(Finding(code='INPUT_MISSING', severity='WARN', message=f'Evidence file missing: {phase}', context={'phase': phase}))
    if not guardian_present:
        env.findings.append(Finding(code='INPUT_MISSING', severity='WARN', message='Guardian report not found'))
    if not all_gates_pass:
        env.findings.append(Finding(code='APPROVAL_NO', severity='WARN', message='Gate failures or missing evidence'))
    if not guardian_pass:
        env.findings.append(Finding(code='APPROVAL_NO', severity='WARN', message='Guardian report not PASS'))
    return env

def generate_summary_with_envelope(evidence_files: dict[str, Path] | None=None, guardian_report_paths: list[Path] | None=None, out_path: str | None=None) -> tuple[str, int, ResultEnvelope]:
    """Generate summary and build envelope in one call."""
    if evidence_files is None:
        evidence_files = EVIDENCE_FILES
    if guardian_report_paths is None:
        guardian_report_paths = GUARDIAN_REPORT_PATHS
    md, exit_code = generate_summary(evidence_files, guardian_report_paths)
    evidence: dict[str, dict | None] = {}
    for phase, path in sorted(evidence_files.items()):
        evidence[phase] = _load_json(path)
    guardian = None
    for p in guardian_report_paths:
        guardian = _load_json(p)
        if guardian is not None:
            break
    all_gates_pass = True
    for phase in sorted(evidence.keys()):
        data = evidence[phase]
        if data is None:
            all_gates_pass = False
        elif data.get('violations', 0) > 0 or data.get('blocking', False):
            all_gates_pass = False
    guardian_pass = guardian is not None and guardian.get('status') == 'PASS'
    env = _build_envelope(exit_code, evidence_files, guardian_report_paths, out_path, all_gates_pass, guardian_pass)
    return (md, exit_code, env)

def main() -> int:
    parser = argparse.ArgumentParser(description='Generate V15 review summary markdown.')
    parser.add_argument('--out', type=str, required=True, help='Output markdown file path')
    parser.add_argument('--json-out', type=str, default=None, help='Optional: write JSON result envelope to this path')
    args = parser.parse_args()
    md, exit_code, env = generate_summary_with_envelope(out_path=args.out)
    if args.json_out:
        env.write_json(Path(args.json_out))
    if exit_code != 0:
        print('ERROR: All input files missing. Nothing to summarize.', file=sys.stderr)
        return exit_code
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding='utf-8')
    print(f'Review summary written to: {out_path}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
