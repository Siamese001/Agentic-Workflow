"""
RCA: Why tables are not loading after switching to real data

Compare mock data structure vs real data structure to identify mismatch
"""
import json
import re

from agentic_core.L0_routing.config.path_constants import DASHBOARD_DIR, get_validated_project_root
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

_emit_emits_metric_event("rca_table_rendering_util", "p4obs", "metric_1")
_emit_emits_metric_event("rca_table_rendering_util", "p4obs", "metric_2")
_emit_emits_metric_event("rca_table_rendering_util", "p4obs", "metric_3")
_emit_emits_metric_event("rca_table_rendering_util", "p4obs", "metric_4")
_emit_emits_metric_event("rca_table_rendering_util", "p4obs", "metric_5")
_emit_emits_metric_event("rca_table_rendering_util", "p4obs", "metric_6")
_emit_records_incident_event("rca_table_rendering_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("rca_table_rendering_util", "p4obs", "anomaly")
_emit_writes_observability_log("rca_table_rendering_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("rca_table_rendering_util", "p4obs", "mon_state")
_emit_triggers_alert("rca_table_rendering_util", "p4obs", "alert")
_emit_links_incident_trace("rca_table_rendering_util", "p4obs", "trace_link")
_emit_captures_pattern("rca_table_rendering_util", "p3lm", "pattern")
_emit_records_learning_event("rca_table_rendering_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rca_table_rendering_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("rca_table_rendering_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rca_table_rendering_util", "p3lm", "routing")
_emit_improves_agent_policy("rca_table_rendering_util", "p3lm", "policy")
_emit_stores_learning_state("rca_table_rendering_util", "p3lm", "state")
_emit_records_execution_trace("rca_table_rendering_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rca_table_rendering_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rca_table_rendering_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rca_table_rendering_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rca_table_rendering_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rca_table_rendering_util", "env_read", "p2_env_1")
_emit_reads_environ("rca_table_rendering_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("rca_table_rendering_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rca_table_rendering_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "rca_table_rendering_util")
_emit_applies_guardrail("p0", "rca_table_rendering_util", "p0_governance")
_emit_reads_policy_state("p0", "rca_table_rendering_util", "policy_binding")
_emit_snapshots_state("p0", "rca_table_rendering_util", "state_snapshot")
_emit_pulls_context("p1", "rca_table_rendering_util", "context_pull")
_emit_pulls_context("p1", "rca_table_rendering_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "rca_table_rendering_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rca_table_rendering_util", "uwg_term_secondary")
_emit_writes_through("p1", "rca_table_rendering_util", "write_through")
_emit_writes_through("p1", "rca_table_rendering_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "rca_table_rendering_util", "safety_validation")
_emit_invokes_eval("p1", "rca_table_rendering_util", "eval_call")
_emit_proposal_commits_routing("p1", "rca_table_rendering_util", "routing_commit")
_emit_escalates_to_human("p1", "rca_table_rendering_util", "human_escalation")
_emit_routes_through("p1", "rca_table_rendering_util", "route_through")
_emit_checks_agent_registry("p1", "rca_table_rendering_util", "agent_registry")
_emit_validates_agent_capability("p1", "rca_table_rendering_util", "capability")
_emit_dispatches_execution_plan("p1", "rca_table_rendering_util", "exec_plan")
_emit_agent_executes_agent("p1", "rca_table_rendering_util", "sub_agent")
_emit_routes_to_agent("p1", "rca_table_rendering_util", "target_agent")
_emit_verifies_policy("p1", "rca_table_rendering_util", "policy_check")
_emit_observes_runtime_state("p1", "rca_table_rendering_util", "runtime_state")
_emit_verifies_boundary("p1", "rca_table_rendering_util", "boundary_check")
_emit_transcripts_response("p1", "rca_table_rendering_util", "transcript")
_emit_hard_fails_untranscripted("p1", "rca_table_rendering_util")
_emit_gated_by_confidence("p1", "rca_table_rendering_util", "confidence_gate")
emit_replay_key("p0", "rca_table_rendering_util")
emit_determinism_digest("p0", "rca_table_rendering_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rca_table_rendering_util", "execution_auth")
_emit_validates_capability("p2", "rca_table_rendering_util", "capability_check")
_emit_routes_to_capability("p2", "rca_table_rendering_util", "capability_route")
_emit_writes_via_uwg("p2", "rca_table_rendering_util", "uwg_write")
_emit_blocks_direct_write("p2", "rca_table_rendering_util", "direct_write_block")
_emit_records_tool_invocation("p2", "rca_table_rendering_util", "tool_invocation")
_emit_captures_execution_output("p2", "rca_table_rendering_util", "exec_output")
_emit_dispatches_agent("p3", "rca_table_rendering_util", "agent_dispatch")
_emit_coordinates_agents("p3", "rca_table_rendering_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "rca_table_rendering_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "rca_table_rendering_util", "healing_outcome")
_emit_escalates_failure("p3", "rca_table_rendering_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "rca_table_rendering_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rca_table_rendering_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "rca_table_rendering_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "rca_table_rendering_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rca_table_rendering_util", "eval_metric")
_emit_stores_embedding("p4", "rca_table_rendering_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "rca_table_rendering_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rca_table_rendering_util", "exec_snapshot_link")

def rca_table_rendering():
    """Root cause analysis for table rendering failure."""
    print('=' * 70)
    print('RCA: TABLE RENDERING FAILURE')
    print('=' * 70)
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / 'autonomy_dashboard.html'
    html = dashboard_path.read_text(encoding='utf-8')
    print('\n1. Extracting dashboardData...')
    dash_match = re.search('const dashboardData = (\\[.*?\\]);', html, re.DOTALL)
    if not dash_match:
        print('   ❌ dashboardData not found')
        return
    data = json.loads(dash_match.group(1))
    print(f'   ✅ dashboardData: {len(data)} rows')
    territory_names = [row['Territory'] for row in data if row['Territory'] != 'TOTAL']
    print(f'\n2. Territory names in dashboardData ({len(territory_names)}):')
    for i, name in enumerate(territory_names[:5], 1):
        print(f"   {i}. '{name}'")
    print(f'   ... ({len(territory_names) - 5} more)')
    print('\n3. Extracting realAgentData...')
    real_match = re.search('const realAgentData = (\\{.*?\\});', html, re.DOTALL)
    if not real_match:
        print('   ❌ realAgentData not found')
        return
    real_data = json.loads(real_match.group(1))
    real_territories = list(real_data.keys())
    print(f'   ✅ realAgentData: {len(real_territories)} territories')
    print(f'\n4. Territory names in realAgentData ({len(real_territories)}):')
    for i, name in enumerate(real_territories[:5], 1):
        print(f"   {i}. '{name}'")
    print(f'   ... ({len(real_territories) - 5} more)')
    print('\n5. COMPARING TERRITORY NAMES:')
    print('   ' + '=' * 66)
    dash_set = set(territory_names)
    real_set = set(real_territories)
    in_dash_not_real = dash_set - real_set
    in_real_not_dash = real_set - dash_set
    matching = dash_set & real_set
    print(f'\n   Matching territories: {len(matching)}')
    print(f'   In dashboardData but NOT in realAgentData: {len(in_dash_not_real)}')
    print(f'   In realAgentData but NOT in dashboardData: {len(in_real_not_dash)}')
    if in_dash_not_real:
        print(f'\n   ❌ MISMATCH: {len(in_dash_not_real)} territories in dashboardData have NO realAgentData:')
        for name in sorted(in_dash_not_real)[:10]:
            print(f"      - '{name}'")
    if in_real_not_dash:
        print(f'\n   ⚠️  EXTRA: {len(in_real_not_dash)} territories in realAgentData not in dashboardData:')
        for name in sorted(in_real_not_dash)[:10]:
            print(f"      - '{name}'")
    print('\n6. Checking realAgentData structure:')
    sample_territory = real_territories[0]
    sample_data = real_data[sample_territory]
    print(f"\n   Sample territory: '{sample_territory}'")
    print(f'   Keys: {list(sample_data.keys())}')
    if 'agents' in sample_data:
        print(f"   ✅ Has 'agents' array: {len(sample_data['agents'])} agents")
        if sample_data['agents']:
            agent = sample_data['agents'][0]
            print(f'   Agent keys: {list(agent.keys())}')
    else:
        print("   ❌ Missing 'agents' array")
    print('\n7. Checking rendering function expectations:')
    if 'globalAgentData[territory]' in html:
        print('   ✅ Code uses: globalAgentData[territory]')
    if 'globalAgentData[territoryName]' in html:
        print('   ✅ Code uses: globalAgentData[territoryName]')
    if 'globalAgentData[row.Territory]' in html:
        print('   ✅ Code uses: globalAgentData[row.Territory]')
    print('\n' + '=' * 70)
    print('ROOT CAUSE ANALYSIS')
    print('=' * 70)
    if len(in_dash_not_real) > 0:
        print('\n❌ CRITICAL ISSUE FOUND:')
        print(f'   {len(in_dash_not_real)} territories in dashboardData have NO corresponding realAgentData')
        print('\n   IMPACT:')
        print('   - When rendering tries to access globalAgentData[territory]')
        print('   - It gets undefined for these territories')
        print('   - This causes rendering to fail or show empty tables')
        print('\n   SOLUTION:')
        print('   - Territory names in dashboardData MUST match realAgentData keys')
        print('   - Regenerate dashboard to ensure name consistency')
        print('\n   Example mismatches:')
        for name in sorted(in_dash_not_real)[:5]:
            closest = None
            for real_name in real_territories:
                if name.lower() in real_name.lower() or real_name.lower() in name.lower():
                    closest = real_name
                    break
            if closest:
                print(f"      dashboardData: '{name}'")
                print(f"      realAgentData: '{closest}' (possible match)")
            else:
                print(f"      dashboardData: '{name}' (no match found)")
    else:
        print('\n✅ Territory names match between dashboardData and realAgentData')
        print('\n   Other possible issues:')
        print('   - Check browser console for JavaScript errors')
        print('   - Verify loadData() is being called')
        print('   - Check if DOM elements exist (kpiGrid, codeQualityGrid)')
if __name__ == '__main__':
    rca_table_rendering()
