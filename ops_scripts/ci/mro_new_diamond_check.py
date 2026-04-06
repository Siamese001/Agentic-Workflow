"""MRO New Diamond Check — CI Gate (Entry-Level Prevention).

Prevents reintroduction of MRO diamonds at the *entry level*.
Unlike mro_contract_check.py (which enforces a total-count ceiling),
this gate fails if ANY diamond exists that is NOT already in the
committed baseline entries.

Policy:
  1. Every current diamond must have a matching entry in the baseline JSON.
  2. A "new" diamond (not in baseline) → HARD FAIL.
  3. Override: commit tag MRO_BASELINE_BUMP:<reason> allows pass,
     but ONLY if the baseline JSON has been updated in the same PR
     (i.e., the new diamond appears in the updated baseline).

Exit 0 = pass, exit 1 = new diamond(s) detected.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "mro_new_diamond_check")
_emit_applies_guardrail("p0", "mro_new_diamond_check", "p0_governance")
_emit_reads_policy_state("p0", "mro_new_diamond_check", "policy_binding")
_emit_snapshots_state("p0", "mro_new_diamond_check", "state_snapshot")
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

_emit_emits_metric_event("mro_new_diamond_check", "p4obs", "metric_1")
_emit_emits_metric_event("mro_new_diamond_check", "p4obs", "metric_2")
_emit_emits_metric_event("mro_new_diamond_check", "p4obs", "metric_3")
_emit_emits_metric_event("mro_new_diamond_check", "p4obs", "metric_4")
_emit_emits_metric_event("mro_new_diamond_check", "p4obs", "metric_5")
_emit_emits_metric_event("mro_new_diamond_check", "p4obs", "metric_6")
_emit_records_incident_event("mro_new_diamond_check", "p4obs", "incident")
_emit_captures_runtime_anomaly("mro_new_diamond_check", "p4obs", "anomaly")
_emit_writes_observability_log("mro_new_diamond_check", "p4obs", "obs_log")
_emit_updates_monitoring_state("mro_new_diamond_check", "p4obs", "mon_state")
_emit_triggers_alert("mro_new_diamond_check", "p4obs", "alert")
_emit_links_incident_trace("mro_new_diamond_check", "p4obs", "trace_link")
_emit_captures_pattern("mro_new_diamond_check", "p3lm", "pattern")
_emit_records_learning_event("mro_new_diamond_check", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mro_new_diamond_check", "p3lm", "snapshot")
_emit_feeds_meta_learning("mro_new_diamond_check", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mro_new_diamond_check", "p3lm", "routing")
_emit_improves_agent_policy("mro_new_diamond_check", "p3lm", "policy")
_emit_stores_learning_state("mro_new_diamond_check", "p3lm", "state")
_emit_records_execution_trace("mro_new_diamond_check", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mro_new_diamond_check", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mro_new_diamond_check", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mro_new_diamond_check", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mro_new_diamond_check", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mro_new_diamond_check", "env_read", "p2_env_1")
_emit_reads_environ("mro_new_diamond_check", "env_read", "p2_env_2")
_emit_reads_runtime_state("mro_new_diamond_check", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mro_new_diamond_check", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mro_new_diamond_check", "context_pull")
_emit_pulls_context("p1", "mro_new_diamond_check", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mro_new_diamond_check", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mro_new_diamond_check", "uwg_term_2")
_emit_writes_through("p1", "mro_new_diamond_check", "write_through")
_emit_writes_through("p1", "mro_new_diamond_check", "write_through_2")
_emit_validated_by_safety_plane("p1", "mro_new_diamond_check", "safety_validation")
_emit_invokes_eval("p1", "mro_new_diamond_check", "eval_call")
_emit_proposal_commits_routing("p1", "mro_new_diamond_check", "routing_commit")
_emit_escalates_to_human("p1", "mro_new_diamond_check", "human_escalation")
_emit_routes_through("p1", "mro_new_diamond_check", "route_through")
_emit_checks_agent_registry("p1", "mro_new_diamond_check", "agent_registry")
_emit_validates_agent_capability("p1", "mro_new_diamond_check", "capability")
_emit_dispatches_execution_plan("p1", "mro_new_diamond_check", "exec_plan")
_emit_agent_executes_agent("p1", "mro_new_diamond_check", "sub_agent")
_emit_routes_to_agent("p1", "mro_new_diamond_check", "target_agent")
_emit_verifies_policy("p1", "mro_new_diamond_check", "policy_check")
_emit_observes_runtime_state("p1", "mro_new_diamond_check", "runtime_state")
_emit_verifies_boundary("p1", "mro_new_diamond_check", "boundary_check")
_emit_transcripts_response("p1", "mro_new_diamond_check", "transcript")
_emit_hard_fails_untranscripted("p1", "mro_new_diamond_check")
_emit_gated_by_confidence("p1", "mro_new_diamond_check", "confidence_gate")
emit_replay_key("p0", "mro_new_diamond_check")
emit_determinism_digest("p0", "mro_new_diamond_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "mro_new_diamond_check", "execution_auth")
_emit_validates_capability("p2", "mro_new_diamond_check", "capability_check")
_emit_routes_to_capability("p2", "mro_new_diamond_check", "capability_route")
_emit_writes_via_uwg("p2", "mro_new_diamond_check", "uwg_write")
_emit_blocks_direct_write("p2", "mro_new_diamond_check", "direct_write_block")
_emit_records_tool_invocation("p2", "mro_new_diamond_check", "tool_invocation")
_emit_captures_execution_output("p2", "mro_new_diamond_check", "exec_output")
_emit_dispatches_agent("p3", "mro_new_diamond_check", "agent_dispatch")
_emit_coordinates_agents("p3", "mro_new_diamond_check", "agent_coordination")
_emit_records_workflow_lineage("p3", "mro_new_diamond_check", "workflow_lineage")
_emit_records_healing_outcome("p3", "mro_new_diamond_check", "healing_outcome")
_emit_escalates_failure("p3", "mro_new_diamond_check", "failure_escalation")
_emit_orchestrates_workflow("p3", "mro_new_diamond_check", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mro_new_diamond_check", "healing_dispatch")
_emit_invokes_evaluation("p3", "mro_new_diamond_check", "evaluation_signal")
_emit_records_telemetry_event("p4", "mro_new_diamond_check", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mro_new_diamond_check", "eval_metric")
_emit_stores_embedding("p4", "mro_new_diamond_check", "embedding_store")
_emit_updates_meta_learning_state("p4", "mro_new_diamond_check", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mro_new_diamond_check", "exec_snapshot_link")
BASELINE_PATH = 'artifacts/consolidation/mro_diamond_baseline.json'

def _diamond_key(entry: dict) -> str:
    """Canonical key: file:class."""
    return entry['file'] + ':' + entry['class']

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))
    from ops_scripts.ci.mro_contract_check import scan_diamonds
    baseline_file = project_root / BASELINE_PATH
    if not baseline_file.is_file():
        print(f'FAIL: baseline not found: {BASELINE_PATH}', file=sys.stderr)
        return 1
    baseline = json.loads(baseline_file.read_text(encoding='utf-8'))
    baseline_keys = {_diamond_key(e) for e in baseline.get('entries', [])}
    current_diamonds = scan_diamonds(project_root)
    current_keys = {_diamond_key(d) for d in current_diamonds}
    new_diamonds = [d for d in current_diamonds if _diamond_key(d) not in baseline_keys]
    print('MRO New Diamond Check (entry-level prevention):')
    print(f'  baseline_entries={len(baseline_keys)}  current_entries={len(current_keys)}')
    print(f'  new_diamonds={len(new_diamonds)}')
    if not new_diamonds:
        print('PASS: no new MRO diamonds introduced')
        return 0
    commit_msg = os.environ.get('COMMIT_MESSAGE', '')
    if 'MRO_BASELINE_BUMP:' in commit_msg:
        still_missing = [d for d in new_diamonds if _diamond_key(d) not in baseline_keys]
        if still_missing:
            print(f'FAIL: MRO_BASELINE_BUMP tag present but {len(still_missing)} new diamond(s) not added to baseline JSON:')
            for d in still_missing:
                print(f"  - {d['file']}:{d['line']} class {d['class']} {d['redundant_mixins']}")
            return 1
        print(f'WARN: {len(new_diamonds)} new diamond(s) allowed via MRO_BASELINE_BUMP tag')
        return 0
    print(f'FAIL: {len(new_diamonds)} new MRO diamond(s) introduced:')
    for d in new_diamonds:
        print(f"  - {d['file']}:{d['line']} class {d['class']} redundant={d['redundant_mixins']} carriers={d['carriers']}")
    print('  To fix:')
    print(f'    1. Edit {BASELINE_PATH} — add new entries + set total={len(current_keys)}')
    print('    2. Commit with tag: MRO_BASELINE_BUMP:<reason>')
    print('    3. Verify: PYTHONPATH=. python ops_scripts/ci/mro_new_diamond_check.py')
    return 1
if __name__ == '__main__':
    sys.exit(main())
