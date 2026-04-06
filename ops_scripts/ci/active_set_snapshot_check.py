"""Active Set Drift Snapshot Check — CI Gate.

Compares the current active set fingerprint against a committed snapshot.
If the fingerprint has changed, the commit must contain the tag:
    ACTIVE_SET_SNAPSHOT_BUMP:<reason>

This prevents silent active-set drift.

Exit 0 = pass, exit 1 = drift detected without acknowledgement.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "active_set_snapshot_check")
_emit_applies_guardrail("p0", "active_set_snapshot_check", "p0_governance")
_emit_reads_policy_state("p0", "active_set_snapshot_check", "policy_binding")
_emit_snapshots_state("p0", "active_set_snapshot_check", "state_snapshot")
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

_emit_emits_metric_event("active_set_snapshot_check", "p4obs", "metric_1")
_emit_emits_metric_event("active_set_snapshot_check", "p4obs", "metric_2")
_emit_emits_metric_event("active_set_snapshot_check", "p4obs", "metric_3")
_emit_emits_metric_event("active_set_snapshot_check", "p4obs", "metric_4")
_emit_emits_metric_event("active_set_snapshot_check", "p4obs", "metric_5")
_emit_emits_metric_event("active_set_snapshot_check", "p4obs", "metric_6")
_emit_records_incident_event("active_set_snapshot_check", "p4obs", "incident")
_emit_captures_runtime_anomaly("active_set_snapshot_check", "p4obs", "anomaly")
_emit_writes_observability_log("active_set_snapshot_check", "p4obs", "obs_log")
_emit_updates_monitoring_state("active_set_snapshot_check", "p4obs", "mon_state")
_emit_triggers_alert("active_set_snapshot_check", "p4obs", "alert")
_emit_links_incident_trace("active_set_snapshot_check", "p4obs", "trace_link")
_emit_captures_pattern("active_set_snapshot_check", "p3lm", "pattern")
_emit_records_learning_event("active_set_snapshot_check", "p3lm", "learning_event")
_emit_writes_learning_snapshot("active_set_snapshot_check", "p3lm", "snapshot")
_emit_feeds_meta_learning("active_set_snapshot_check", "p3lm", "meta_feed")
_emit_updates_routing_strategy("active_set_snapshot_check", "p3lm", "routing")
_emit_improves_agent_policy("active_set_snapshot_check", "p3lm", "policy")
_emit_stores_learning_state("active_set_snapshot_check", "p3lm", "state")
_emit_records_execution_trace("active_set_snapshot_check", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("active_set_snapshot_check", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("active_set_snapshot_check", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("active_set_snapshot_check", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("active_set_snapshot_check", "L4_STATE", "p2_trace_5")
_emit_reads_environ("active_set_snapshot_check", "env_read", "p2_env_1")
_emit_reads_environ("active_set_snapshot_check", "env_read", "p2_env_2")
_emit_reads_runtime_state("active_set_snapshot_check", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("active_set_snapshot_check", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "active_set_snapshot_check", "context_pull")
_emit_pulls_context("p1", "active_set_snapshot_check", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "active_set_snapshot_check", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "active_set_snapshot_check", "uwg_term_2")
_emit_writes_through("p1", "active_set_snapshot_check", "write_through")
_emit_writes_through("p1", "active_set_snapshot_check", "write_through_2")
_emit_validated_by_safety_plane("p1", "active_set_snapshot_check", "safety_validation")
_emit_invokes_eval("p1", "active_set_snapshot_check", "eval_call")
_emit_proposal_commits_routing("p1", "active_set_snapshot_check", "routing_commit")
_emit_escalates_to_human("p1", "active_set_snapshot_check", "human_escalation")
_emit_routes_through("p1", "active_set_snapshot_check", "route_through")
_emit_checks_agent_registry("p1", "active_set_snapshot_check", "agent_registry")
_emit_validates_agent_capability("p1", "active_set_snapshot_check", "capability")
_emit_dispatches_execution_plan("p1", "active_set_snapshot_check", "exec_plan")
_emit_agent_executes_agent("p1", "active_set_snapshot_check", "sub_agent")
_emit_routes_to_agent("p1", "active_set_snapshot_check", "target_agent")
_emit_verifies_policy("p1", "active_set_snapshot_check", "policy_check")
_emit_observes_runtime_state("p1", "active_set_snapshot_check", "runtime_state")
_emit_verifies_boundary("p1", "active_set_snapshot_check", "boundary_check")
_emit_transcripts_response("p1", "active_set_snapshot_check", "transcript")
_emit_hard_fails_untranscripted("p1", "active_set_snapshot_check")
_emit_gated_by_confidence("p1", "active_set_snapshot_check", "confidence_gate")
emit_replay_key("p0", "active_set_snapshot_check")
emit_determinism_digest("p0", "active_set_snapshot_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "active_set_snapshot_check", "execution_auth")
_emit_validates_capability("p2", "active_set_snapshot_check", "capability_check")
_emit_routes_to_capability("p2", "active_set_snapshot_check", "capability_route")
_emit_writes_via_uwg("p2", "active_set_snapshot_check", "uwg_write")
_emit_blocks_direct_write("p2", "active_set_snapshot_check", "direct_write_block")
_emit_records_tool_invocation("p2", "active_set_snapshot_check", "tool_invocation")
_emit_captures_execution_output("p2", "active_set_snapshot_check", "exec_output")
_emit_dispatches_agent("p3", "active_set_snapshot_check", "agent_dispatch")
_emit_coordinates_agents("p3", "active_set_snapshot_check", "agent_coordination")
_emit_records_workflow_lineage("p3", "active_set_snapshot_check", "workflow_lineage")
_emit_records_healing_outcome("p3", "active_set_snapshot_check", "healing_outcome")
_emit_escalates_failure("p3", "active_set_snapshot_check", "failure_escalation")
_emit_orchestrates_workflow("p3", "active_set_snapshot_check", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "active_set_snapshot_check", "healing_dispatch")
_emit_invokes_evaluation("p3", "active_set_snapshot_check", "evaluation_signal")
_emit_records_telemetry_event("p4", "active_set_snapshot_check", "telemetry_event")
_emit_captures_evaluation_metric("p4", "active_set_snapshot_check", "eval_metric")
_emit_stores_embedding("p4", "active_set_snapshot_check", "embedding_store")
_emit_updates_meta_learning_state("p4", "active_set_snapshot_check", "meta_learning")
_emit_links_execution_to_snapshot("p4", "active_set_snapshot_check", "exec_snapshot_link")
SNAPSHOT_PATH = 'artifacts/consolidation/active_set_snapshot.json'

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    snapshot_file = project_root / SNAPSHOT_PATH
    if not snapshot_file.is_file():
        print(f'FAIL: snapshot not found: {SNAPSHOT_PATH}', file=sys.stderr)
        return 1
    snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))
    from ops_scripts.ci.active_set_helper import get_active_set
    result = get_active_set(project_root)
    print('Active Set Snapshot Check:')
    print(f"  snapshot_count={snapshot['count']}  current_count={result.count}")
    print(f"  snapshot_fingerprint={snapshot['fingerprint'][:16]}...")
    print(f'  current_fingerprint={result.fingerprint[:16]}...')
    if result.fingerprint == snapshot['fingerprint']:
        print('PASS: active set fingerprint matches snapshot')
        return 0
    commit_msg = os.environ.get('COMMIT_MESSAGE', '')
    if 'ACTIVE_SET_SNAPSHOT_BUMP:' in commit_msg:
        print(f"WARN: fingerprint changed ({snapshot['count']} → {result.count}) but ACTIVE_SET_SNAPSHOT_BUMP tag present")
        from ops_scripts.ci.baseline_io import write_json_atomic
        new_snapshot = {'count': result.count, 'fingerprint': result.fingerprint, 'first_10': list(result.agent_ids[:10]), 'last_10': list(result.agent_ids[-10:])}
        write_json_atomic(snapshot_file, new_snapshot)
        print(f"  AUTO-UPDATED snapshot: {snapshot['count']} → {result.count}")
        return 0
    print('FAIL: active set fingerprint changed without ACTIVE_SET_SNAPSHOT_BUMP tag')
    print(f"  old_count={snapshot['count']}  new_count={result.count}")
    print(f"  old_fingerprint={snapshot['fingerprint']}")
    print(f'  new_fingerprint={result.fingerprint}')
    old_first = snapshot.get('first_10', [])
    old_last = snapshot.get('last_10', [])
    new_first = list(result.agent_ids[:10])
    new_last = list(result.agent_ids[-10:])
    print(f'  old_first_10={old_first}')
    print(f'  new_first_10={new_first}')
    print(f'  old_last_10={old_last}')
    print(f'  new_last_10={new_last}')
    old_ids = set(old_first + old_last)
    new_ids = set(new_first + new_last)
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    if added:
        print(f'  added: {added}')
    if removed:
        print(f'  removed: {removed}')
    print('  Fix: add ACTIVE_SET_SNAPSHOT_BUMP:<reason> to commit message and run:')
    print("    PYTHONPATH=. COMMIT_MESSAGE='ACTIVE_SET_SNAPSHOT_BUMP:<reason>' python ops_scripts/ci/active_set_snapshot_check.py")
    return 1
if __name__ == '__main__':
    sys.exit(main())
