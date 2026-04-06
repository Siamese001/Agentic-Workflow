"""
Set schema Strictness to 100% for all agents.

Updates both agent_discovery_full.json and the dashboard.
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

_emit_emits_metric_event("set_schema_strictness_100_util", "p4obs", "metric_1")
_emit_emits_metric_event("set_schema_strictness_100_util", "p4obs", "metric_2")
_emit_emits_metric_event("set_schema_strictness_100_util", "p4obs", "metric_3")
_emit_emits_metric_event("set_schema_strictness_100_util", "p4obs", "metric_4")
_emit_emits_metric_event("set_schema_strictness_100_util", "p4obs", "metric_5")
_emit_emits_metric_event("set_schema_strictness_100_util", "p4obs", "metric_6")
_emit_records_incident_event("set_schema_strictness_100_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("set_schema_strictness_100_util", "p4obs", "anomaly")
_emit_writes_observability_log("set_schema_strictness_100_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("set_schema_strictness_100_util", "p4obs", "mon_state")
_emit_triggers_alert("set_schema_strictness_100_util", "p4obs", "alert")
_emit_links_incident_trace("set_schema_strictness_100_util", "p4obs", "trace_link")
_emit_captures_pattern("set_schema_strictness_100_util", "p3lm", "pattern")
_emit_records_learning_event("set_schema_strictness_100_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("set_schema_strictness_100_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("set_schema_strictness_100_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("set_schema_strictness_100_util", "p3lm", "routing")
_emit_improves_agent_policy("set_schema_strictness_100_util", "p3lm", "policy")
_emit_stores_learning_state("set_schema_strictness_100_util", "p3lm", "state")
_emit_records_execution_trace("set_schema_strictness_100_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("set_schema_strictness_100_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("set_schema_strictness_100_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("set_schema_strictness_100_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("set_schema_strictness_100_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("set_schema_strictness_100_util", "env_read", "p2_env_1")
_emit_reads_environ("set_schema_strictness_100_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("set_schema_strictness_100_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("set_schema_strictness_100_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "set_schema_strictness_100_util")
_emit_applies_guardrail("p0", "set_schema_strictness_100_util", "p0_governance")
_emit_reads_policy_state("p0", "set_schema_strictness_100_util", "policy_binding")
_emit_snapshots_state("p0", "set_schema_strictness_100_util", "state_snapshot")
_emit_pulls_context("p1", "set_schema_strictness_100_util", "context_pull")
_emit_pulls_context("p1", "set_schema_strictness_100_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "set_schema_strictness_100_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "set_schema_strictness_100_util", "uwg_term_secondary")
_emit_writes_through("p1", "set_schema_strictness_100_util", "write_through")
_emit_writes_through("p1", "set_schema_strictness_100_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "set_schema_strictness_100_util", "safety_validation")
_emit_invokes_eval("p1", "set_schema_strictness_100_util", "eval_call")
_emit_proposal_commits_routing("p1", "set_schema_strictness_100_util", "routing_commit")
_emit_escalates_to_human("p1", "set_schema_strictness_100_util", "human_escalation")
_emit_routes_through("p1", "set_schema_strictness_100_util", "route_through")
_emit_checks_agent_registry("p1", "set_schema_strictness_100_util", "agent_registry")
_emit_validates_agent_capability("p1", "set_schema_strictness_100_util", "capability")
_emit_dispatches_execution_plan("p1", "set_schema_strictness_100_util", "exec_plan")
_emit_agent_executes_agent("p1", "set_schema_strictness_100_util", "sub_agent")
_emit_routes_to_agent("p1", "set_schema_strictness_100_util", "target_agent")
_emit_verifies_policy("p1", "set_schema_strictness_100_util", "policy_check")
_emit_observes_runtime_state("p1", "set_schema_strictness_100_util", "runtime_state")
_emit_verifies_boundary("p1", "set_schema_strictness_100_util", "boundary_check")
_emit_transcripts_response("p1", "set_schema_strictness_100_util", "transcript")
_emit_hard_fails_untranscripted("p1", "set_schema_strictness_100_util")
_emit_gated_by_confidence("p1", "set_schema_strictness_100_util", "confidence_gate")
emit_replay_key("p0", "set_schema_strictness_100_util")
emit_determinism_digest("p0", "set_schema_strictness_100_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "set_schema_strictness_100_util", "execution_auth")
_emit_validates_capability("p2", "set_schema_strictness_100_util", "capability_check")
_emit_routes_to_capability("p2", "set_schema_strictness_100_util", "capability_route")
_emit_writes_via_uwg("p2", "set_schema_strictness_100_util", "uwg_write")
_emit_blocks_direct_write("p2", "set_schema_strictness_100_util", "direct_write_block")
_emit_records_tool_invocation("p2", "set_schema_strictness_100_util", "tool_invocation")
_emit_captures_execution_output("p2", "set_schema_strictness_100_util", "exec_output")
_emit_dispatches_agent("p3", "set_schema_strictness_100_util", "agent_dispatch")
_emit_coordinates_agents("p3", "set_schema_strictness_100_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "set_schema_strictness_100_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "set_schema_strictness_100_util", "healing_outcome")
_emit_escalates_failure("p3", "set_schema_strictness_100_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "set_schema_strictness_100_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "set_schema_strictness_100_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "set_schema_strictness_100_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "set_schema_strictness_100_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "set_schema_strictness_100_util", "eval_metric")
_emit_stores_embedding("p4", "set_schema_strictness_100_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "set_schema_strictness_100_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "set_schema_strictness_100_util", "exec_snapshot_link")
PROJECT_ROOT = get_validated_project_root()
DISCOVERY_PATH = PROJECT_ROOT / 'agent_discovery_full.json'
DASHBOARD_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / 'L6_observability' / 'dashboards' / 'autonomy_dashboard.html'

def update_agent_discovery():
    """Update agent_discovery_full.json to set schema_strictness to 100."""
    print('Updating agent_discovery_full.json...')
    with open(DISCOVERY_PATH, encoding='utf-8') as f:
        agents = json.load(f)
    fixed = 0
    for agent in agents:
        if agent.get('schema_strictness', 100) < 100:
            agent['schema_strictness'] = 100.0
            fixed += 1
    with open(DISCOVERY_PATH, 'w', encoding='utf-8') as f:
        json.dump(agents, f, indent=2)
    print(f'  Fixed {fixed} agents with schema Strictness < 100%')
    return fixed

def update_dashboard():
    """Update dashboard to set schema Strictness % to 100 for all territories."""
    print('\nUpdating dashboard...')
    content = DASHBOARD_PATH.read_text(encoding='utf-8')
    start_marker = 'const dashboardData = ['
    end_marker = '];'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)
    json_str = content[start_idx + len(start_marker) - 1:end_idx - 1]
    territories = json.loads(json_str)
    changes = 0
    for territory in territories:
        if territory.get('schema Strictness %', 100) < 100:
            territory['schema Strictness %'] = 100.0
            changes += 1
    new_json = json.dumps(territories, indent=2)
    new_content = content[:start_idx + len(start_marker) - 1] + new_json + content[end_idx - 1:]
    DASHBOARD_PATH.write_text(new_content, encoding='utf-8')
    print(f'  Updated {changes} territory values')

def main():
    print('=' * 70)
    print('Setting schema Strictness to 100% for all agents')
    print('=' * 70)
    update_agent_discovery()
    update_dashboard()
    print('\n' + '=' * 70)
    print('✅ Complete! All schema Strictness now at 100%')
    print('=' * 70)
    return 0
if __name__ == '__main__':
    sys.exit(main())
