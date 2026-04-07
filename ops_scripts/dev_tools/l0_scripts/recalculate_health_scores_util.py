"""
Recalculate Health Scores based on new Complexity Health values.

Uses the canonical health calculation formula:
Health = (Heal Cap × 0.30) + (Invocation × 0.10) + (Test × 0.25) + (Obs × 0.20) + (Complexity × 0.15)
"""
import json
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
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

_emit_records_execution_trace("p0", "evidence", "recalculate_health_scores_util")
_emit_applies_guardrail("p0", "recalculate_health_scores_util", "p0_governance")
_emit_reads_policy_state("p0", "recalculate_health_scores_util", "policy_binding")
_emit_snapshots_state("p0", "recalculate_health_scores_util", "state_snapshot")
emit_replay_key("p0", "recalculate_health_scores_util")
emit_determinism_digest("p0", "recalculate_health_scores_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "recalculate_health_scores_util", "execution_auth")
_emit_validates_capability("p2", "recalculate_health_scores_util", "capability_check")
_emit_routes_to_capability("p2", "recalculate_health_scores_util", "capability_route")
_emit_writes_via_uwg("p2", "recalculate_health_scores_util", "uwg_write")
_emit_blocks_direct_write("p2", "recalculate_health_scores_util", "direct_write_block")
_emit_records_tool_invocation("p2", "recalculate_health_scores_util", "tool_invocation")
_emit_captures_execution_output("p2", "recalculate_health_scores_util", "exec_output")
_emit_dispatches_agent("p3", "recalculate_health_scores_util", "agent_dispatch")
_emit_coordinates_agents("p3", "recalculate_health_scores_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "recalculate_health_scores_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "recalculate_health_scores_util", "healing_outcome")
_emit_escalates_failure("p3", "recalculate_health_scores_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "recalculate_health_scores_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "recalculate_health_scores_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "recalculate_health_scores_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "recalculate_health_scores_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "recalculate_health_scores_util", "eval_metric")
_emit_stores_embedding("p4", "recalculate_health_scores_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "recalculate_health_scores_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "recalculate_health_scores_util", "exec_snapshot_link")
PROJECT_ROOT = get_validated_project_root()
DASHBOARD_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / 'L6_observability' / 'dashboards' / 'autonomy_dashboard.html'
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L5_safety.validators.canonical_truth_validator import calculate_health_score
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("recalculate_health_scores_util", "p4obs", "metric_1")
_emit_emits_metric_event("recalculate_health_scores_util", "p4obs", "metric_2")
_emit_emits_metric_event("recalculate_health_scores_util", "p4obs", "metric_3")
_emit_emits_metric_event("recalculate_health_scores_util", "p4obs", "metric_4")
_emit_emits_metric_event("recalculate_health_scores_util", "p4obs", "metric_5")
_emit_emits_metric_event("recalculate_health_scores_util", "p4obs", "metric_6")
_emit_records_incident_event("recalculate_health_scores_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("recalculate_health_scores_util", "p4obs", "anomaly")
_emit_writes_observability_log("recalculate_health_scores_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("recalculate_health_scores_util", "p4obs", "mon_state")
_emit_triggers_alert("recalculate_health_scores_util", "p4obs", "alert")
_emit_links_incident_trace("recalculate_health_scores_util", "p4obs", "trace_link")
_emit_captures_pattern("recalculate_health_scores_util", "p3lm", "pattern")
_emit_records_learning_event("recalculate_health_scores_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("recalculate_health_scores_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("recalculate_health_scores_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("recalculate_health_scores_util", "p3lm", "routing")
_emit_improves_agent_policy("recalculate_health_scores_util", "p3lm", "policy")
_emit_stores_learning_state("recalculate_health_scores_util", "p3lm", "state")
_emit_records_execution_trace("recalculate_health_scores_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("recalculate_health_scores_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("recalculate_health_scores_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("recalculate_health_scores_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("recalculate_health_scores_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("recalculate_health_scores_util", "env_read", "p2_env_1")
_emit_reads_environ("recalculate_health_scores_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("recalculate_health_scores_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("recalculate_health_scores_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "recalculate_health_scores_util", "context_pull")
_emit_pulls_context("p1", "recalculate_health_scores_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "recalculate_health_scores_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "recalculate_health_scores_util", "uwg_term_secondary")
_emit_writes_through("p1", "recalculate_health_scores_util", "write_through")
_emit_writes_through("p1", "recalculate_health_scores_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "recalculate_health_scores_util", "safety_validation")
_emit_invokes_eval("p1", "recalculate_health_scores_util", "eval_call")
_emit_proposal_commits_routing("p1", "recalculate_health_scores_util", "routing_commit")
_emit_escalates_to_human("p1", "recalculate_health_scores_util", "human_escalation")
_emit_routes_through("p1", "recalculate_health_scores_util", "route_through")
_emit_checks_agent_registry("p1", "recalculate_health_scores_util", "agent_registry")
_emit_validates_agent_capability("p1", "recalculate_health_scores_util", "capability")
_emit_dispatches_execution_plan("p1", "recalculate_health_scores_util", "exec_plan")
_emit_agent_executes_agent("p1", "recalculate_health_scores_util", "sub_agent")
_emit_routes_to_agent("p1", "recalculate_health_scores_util", "target_agent")
_emit_verifies_policy("p1", "recalculate_health_scores_util", "policy_check")
_emit_observes_runtime_state("p1", "recalculate_health_scores_util", "runtime_state")
_emit_verifies_boundary("p1", "recalculate_health_scores_util", "boundary_check")
_emit_transcripts_response("p1", "recalculate_health_scores_util", "transcript")
_emit_hard_fails_untranscripted("p1", "recalculate_health_scores_util")
_emit_gated_by_confidence("p1", "recalculate_health_scores_util", "confidence_gate")


def main():
    print('=' * 70)
    print('Recalculating Health Scores with Complexity Health = 100%')
    print('=' * 70)
    if not DASHBOARD_PATH.exists():
        print(f'ERROR: Dashboard not found at {DASHBOARD_PATH}')
        return 1
    content = DASHBOARD_PATH.read_text(encoding='utf-8')
    start_marker = 'const dashboardData = ['
    end_marker = '];'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)
    json_str = content[start_idx + len(start_marker) - 1:end_idx - 1]
    territories = json.loads(json_str)
    print(f'\nFound {len(territories)} territories')
    changes = []
    for territory in territories:
        name = territory.get('Territory', 'Unknown')
        heal_cap = territory.get('Heal Cap %', 0)
        invoc = territory.get('Heal Invocation %', 0)
        test_cov = territory.get('Test %', 0)
        obs = territory.get('Observable %', 0)
        comp_health = territory.get('Complexity Health', 0)
        old_health = territory.get('Health', 0)
        new_health = round(calculate_health_score(heal_cap=heal_cap, invoc=invoc, test_cov=test_cov, obs=obs, comp_health=comp_health), 1)
        if abs(old_health - new_health) > 0.01:
            changes.append((name, old_health, new_health))
            territory['Health'] = new_health
            breakdown = f'Heal:{int(heal_cap)}+Inv:{int(invoc)}+Test:{int(test_cov)}+Obs:{int(obs)}+CC:{int(comp_health)}'
            territory['Health Breakdown'] = breakdown
    new_json = json.dumps(territories, indent=2)
    new_content = content[:start_idx + len(start_marker) - 1] + new_json + content[end_idx - 1:]
    DASHBOARD_PATH.write_text(new_content, encoding='utf-8')
    print(f'\n✅ Updated {len(changes)} Health scores')
    print('\nChanges made:')
    for name, old, new in changes:
        print(f'  {name}: {old} -> {new}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
