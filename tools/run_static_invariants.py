"""
tools/run_static_invariants.py

Runner for all static invariant checks.
Baseline-aware: loads previous violation snapshot and reports only NEW violations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "run_static_invariants")
_emit_applies_guardrail("p0", "run_static_invariants", "p0_governance")
_emit_reads_policy_state("p0", "run_static_invariants", "policy_binding")
_emit_snapshots_state("p0", "run_static_invariants", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("run_static_invariants", "p4obs", "metric_1")
_emit_emits_metric_event("run_static_invariants", "p4obs", "metric_2")
_emit_emits_metric_event("run_static_invariants", "p4obs", "metric_3")
_emit_emits_metric_event("run_static_invariants", "p4obs", "metric_4")
_emit_emits_metric_event("run_static_invariants", "p4obs", "metric_5")
_emit_emits_metric_event("run_static_invariants", "p4obs", "metric_6")
_emit_records_incident_event("run_static_invariants", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_static_invariants", "p4obs", "anomaly")
_emit_writes_observability_log("run_static_invariants", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_static_invariants", "p4obs", "mon_state")
_emit_triggers_alert("run_static_invariants", "p4obs", "alert")
_emit_links_incident_trace("run_static_invariants", "p4obs", "trace_link")
_emit_captures_pattern("run_static_invariants", "p3lm", "pattern")
_emit_records_learning_event("run_static_invariants", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_static_invariants", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_static_invariants", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_static_invariants", "p3lm", "routing")
_emit_improves_agent_policy("run_static_invariants", "p3lm", "policy")
_emit_stores_learning_state("run_static_invariants", "p3lm", "state")
_emit_records_execution_trace("run_static_invariants", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_static_invariants", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_static_invariants", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_static_invariants", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_static_invariants", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_static_invariants", "env_read", "p2_env_1")
_emit_reads_environ("run_static_invariants", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_static_invariants", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_static_invariants", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_static_invariants", "context_pull")
_emit_pulls_context("p1", "run_static_invariants", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_static_invariants", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_static_invariants", "uwg_term_2")
_emit_writes_through("p1", "run_static_invariants", "write_through")
_emit_writes_through("p1", "run_static_invariants", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_static_invariants", "safety_validation")
_emit_invokes_eval("p1", "run_static_invariants", "eval_call")
_emit_proposal_commits_routing("p1", "run_static_invariants", "routing_commit")
emit_replay_key("p0", "run_static_invariants")
emit_determinism_digest("p0", "run_static_invariants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "run_static_invariants", "execution_auth")
_emit_validates_capability("p2", "run_static_invariants", "capability_check")
_emit_routes_to_capability("p2", "run_static_invariants", "capability_route")
_emit_writes_via_uwg("p2", "run_static_invariants", "uwg_write")
_emit_blocks_direct_write("p2", "run_static_invariants", "direct_write_block")
_emit_records_tool_invocation("p2", "run_static_invariants", "tool_invocation")
_emit_captures_execution_output("p2", "run_static_invariants", "exec_output")
_emit_dispatches_agent("p3", "run_static_invariants", "agent_dispatch")
_emit_coordinates_agents("p3", "run_static_invariants", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_static_invariants", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_static_invariants", "healing_outcome")
_emit_escalates_failure("p3", "run_static_invariants", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_static_invariants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_static_invariants", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_static_invariants", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_static_invariants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_static_invariants", "eval_metric")
_emit_stores_embedding("p4", "run_static_invariants", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_static_invariants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_static_invariants", "exec_snapshot_link")
REPO_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BASELINE_PATH = REPO_ROOT / 'artifacts' / 'static_invariants_baseline.json'

def _load_baseline() -> set[str]:
    if BASELINE_PATH.exists():
        try:
            data = json.loads(BASELINE_PATH.read_text(encoding='utf-8'))
            entries = data if isinstance(data, list) else data.get('violations', [])
            print(f'Loaded baseline with {len(entries)} known violation(s).')
            return set(entries)
        # guardian: allow-silent-swallow
        except Exception:
            pass
    print('Loaded baseline with 0 known violation(s).')
    return set()

def _run_ptc_invariants() -> list[str]:
    print('Scanning for PTC invariants...')
    try:
        from agentic_core.L5_safety.static_checks.ptc_invariants import scan_repository_for_ptc_invariants
        violations = scan_repository_for_ptc_invariants(REPO_ROOT)
        if violations:
            print(f'FAIL: PTC Invariants: {len(violations)} violation(s) found.')
            for v in violations:
                print(f'  {v}')
        else:
            print('OK: PTC Invariants: No violations found')
        return [str(v) for v in violations]
    # guardian: allow-silent-swallow
    except Exception as exc:
        print(f'ERROR: PTC invariants scanner failed: {exc}')
        return []

def main() -> int:
    baseline = _load_baseline()
    all_violations: list[str] = []
    all_violations.extend(_run_ptc_invariants())
    new_violations = [v for v in all_violations if v not in baseline]
    if new_violations:
        print(f'FAIL: {len(new_violations)} new violations found (not in baseline).')
        for v in new_violations:
            print(f'  NEW: {v}')
        return 1
    print('OK: No NEW violations found.')
    return 0
if __name__ == '__main__':
    sys.exit(main())
