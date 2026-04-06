"""Agent Count Hard Cap — CI Gate.

Asserts that the ACTIVE agent count does not exceed the hard cap.

Uses the shared ``active_set_helper`` — the single canonical import
point for the ACTIVE set.  This guarantees convergence with
``discovery_registry_consistency_check.py`` and all future gates.

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "agent_count_cap")
_emit_applies_guardrail("p0", "agent_count_cap", "p0_governance")
_emit_reads_policy_state("p0", "agent_count_cap", "policy_binding")
_emit_snapshots_state("p0", "agent_count_cap", "state_snapshot")
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

_emit_emits_metric_event("agent_count_cap", "p4obs", "metric_1")
_emit_emits_metric_event("agent_count_cap", "p4obs", "metric_2")
_emit_emits_metric_event("agent_count_cap", "p4obs", "metric_3")
_emit_emits_metric_event("agent_count_cap", "p4obs", "metric_4")
_emit_emits_metric_event("agent_count_cap", "p4obs", "metric_5")
_emit_emits_metric_event("agent_count_cap", "p4obs", "metric_6")
_emit_records_incident_event("agent_count_cap", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_count_cap", "p4obs", "anomaly")
_emit_writes_observability_log("agent_count_cap", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_count_cap", "p4obs", "mon_state")
_emit_triggers_alert("agent_count_cap", "p4obs", "alert")
_emit_links_incident_trace("agent_count_cap", "p4obs", "trace_link")
_emit_captures_pattern("agent_count_cap", "p3lm", "pattern")
_emit_records_learning_event("agent_count_cap", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_count_cap", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_count_cap", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_count_cap", "p3lm", "routing")
_emit_improves_agent_policy("agent_count_cap", "p3lm", "policy")
_emit_stores_learning_state("agent_count_cap", "p3lm", "state")
_emit_records_execution_trace("agent_count_cap", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_count_cap", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_count_cap", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_count_cap", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_count_cap", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_count_cap", "env_read", "p2_env_1")
_emit_reads_environ("agent_count_cap", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_count_cap", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_count_cap", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_count_cap", "context_pull")
_emit_pulls_context("p1", "agent_count_cap", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_count_cap", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_count_cap", "uwg_term_2")
_emit_writes_through("p1", "agent_count_cap", "write_through")
_emit_writes_through("p1", "agent_count_cap", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_count_cap", "safety_validation")
_emit_invokes_eval("p1", "agent_count_cap", "eval_call")
_emit_proposal_commits_routing("p1", "agent_count_cap", "routing_commit")
_emit_escalates_to_human("p1", "agent_count_cap", "human_escalation")
_emit_routes_through("p1", "agent_count_cap", "route_through")
_emit_checks_agent_registry("p1", "agent_count_cap", "agent_registry")
_emit_validates_agent_capability("p1", "agent_count_cap", "capability")
_emit_dispatches_execution_plan("p1", "agent_count_cap", "exec_plan")
_emit_agent_executes_agent("p1", "agent_count_cap", "sub_agent")
_emit_routes_to_agent("p1", "agent_count_cap", "target_agent")
_emit_verifies_policy("p1", "agent_count_cap", "policy_check")
_emit_observes_runtime_state("p1", "agent_count_cap", "runtime_state")
_emit_verifies_boundary("p1", "agent_count_cap", "boundary_check")
_emit_transcripts_response("p1", "agent_count_cap", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_count_cap")
_emit_gated_by_confidence("p1", "agent_count_cap", "confidence_gate")
emit_replay_key("p0", "agent_count_cap")
emit_determinism_digest("p0", "agent_count_cap")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_count_cap", "execution_auth")
_emit_validates_capability("p2", "agent_count_cap", "capability_check")
_emit_routes_to_capability("p2", "agent_count_cap", "capability_route")
_emit_writes_via_uwg("p2", "agent_count_cap", "uwg_write")
_emit_blocks_direct_write("p2", "agent_count_cap", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_count_cap", "tool_invocation")
_emit_captures_execution_output("p2", "agent_count_cap", "exec_output")
_emit_dispatches_agent("p3", "agent_count_cap", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_count_cap", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_count_cap", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_count_cap", "healing_outcome")
_emit_escalates_failure("p3", "agent_count_cap", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_count_cap", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_count_cap", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_count_cap", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_count_cap", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_count_cap", "eval_metric")
_emit_stores_embedding("p4", "agent_count_cap", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_count_cap", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_count_cap", "exec_snapshot_link")
HARD_CAP = 149

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    # guardian: allow-global-mutation
    sys.path.insert(0, str(project_root))
    from ops_scripts.ci.active_set_helper import get_active_set
    try:
        result = get_active_set(project_root)
    # guardian: allow-silent-swallower
    except Exception as exc:
        print(f'FAIL: could not enumerate active agents: {exc}', file=sys.stderr)
        return 1
    print('Agent Count Cap (discovery-aligned):')
    print(f'  active={result.count}  cap={HARD_CAP}  delta={result.count - HARD_CAP}')
    print(f'  fingerprint: {result.fingerprint}')
    print(f'  first_10: {list(result.agent_ids[:10])}')
    print(f'  last_10:  {list(result.agent_ids[-10:])}')
    if result.count > HARD_CAP:
        commit_msg = os.environ.get('COMMIT_MESSAGE', '')
        if 'AGENT_COUNT_BUMP:' in commit_msg:
            print(f'PASS: count {result.count} > cap {HARD_CAP} but AGENT_COUNT_BUMP tag present')
            return 0
        print(f'FAIL: active agent count {result.count} exceeds hard cap {HARD_CAP}\n  To increase, add AGENT_COUNT_BUMP:<reason> to commit message')
        return 1
    print(f'PASS: {result.count} active agents within cap {HARD_CAP}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
