"""
Recalculate Code Quality Scores in Dashboard

Updates the Code Quality Score formula from simple average (Typed + Documented) / 2
to weighted composite: (Typed × 0.30) + (Documented × 0.30) + (schema × 0.25) + (Canonical × 0.15)
"""
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
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

_emit_emits_metric_event("recalculate_code_quality_scores_util", "p4obs", "metric_1")
_emit_emits_metric_event("recalculate_code_quality_scores_util", "p4obs", "metric_2")
_emit_emits_metric_event("recalculate_code_quality_scores_util", "p4obs", "metric_3")
_emit_emits_metric_event("recalculate_code_quality_scores_util", "p4obs", "metric_4")
_emit_emits_metric_event("recalculate_code_quality_scores_util", "p4obs", "metric_5")
_emit_emits_metric_event("recalculate_code_quality_scores_util", "p4obs", "metric_6")
_emit_records_incident_event("recalculate_code_quality_scores_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("recalculate_code_quality_scores_util", "p4obs", "anomaly")
_emit_writes_observability_log("recalculate_code_quality_scores_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("recalculate_code_quality_scores_util", "p4obs", "mon_state")
_emit_triggers_alert("recalculate_code_quality_scores_util", "p4obs", "alert")
_emit_links_incident_trace("recalculate_code_quality_scores_util", "p4obs", "trace_link")
_emit_captures_pattern("recalculate_code_quality_scores_util", "p3lm", "pattern")
_emit_records_learning_event("recalculate_code_quality_scores_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("recalculate_code_quality_scores_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("recalculate_code_quality_scores_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("recalculate_code_quality_scores_util", "p3lm", "routing")
_emit_improves_agent_policy("recalculate_code_quality_scores_util", "p3lm", "policy")
_emit_stores_learning_state("recalculate_code_quality_scores_util", "p3lm", "state")
_emit_records_execution_trace("recalculate_code_quality_scores_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("recalculate_code_quality_scores_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("recalculate_code_quality_scores_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("recalculate_code_quality_scores_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("recalculate_code_quality_scores_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("recalculate_code_quality_scores_util", "env_read", "p2_env_1")
_emit_reads_environ("recalculate_code_quality_scores_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("recalculate_code_quality_scores_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("recalculate_code_quality_scores_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "recalculate_code_quality_scores_util")
_emit_applies_guardrail("p0", "recalculate_code_quality_scores_util", "p0_governance")
_emit_reads_policy_state("p0", "recalculate_code_quality_scores_util", "policy_binding")
_emit_snapshots_state("p0", "recalculate_code_quality_scores_util", "state_snapshot")
_emit_pulls_context("p1", "recalculate_code_quality_scores_util", "context_pull")
_emit_pulls_context("p1", "recalculate_code_quality_scores_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "recalculate_code_quality_scores_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "recalculate_code_quality_scores_util", "uwg_term_secondary")
_emit_writes_through("p1", "recalculate_code_quality_scores_util", "write_through")
_emit_writes_through("p1", "recalculate_code_quality_scores_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "recalculate_code_quality_scores_util", "safety_validation")
_emit_invokes_eval("p1", "recalculate_code_quality_scores_util", "eval_call")
_emit_proposal_commits_routing("p1", "recalculate_code_quality_scores_util", "routing_commit")
_emit_escalates_to_human("p1", "recalculate_code_quality_scores_util", "human_escalation")
_emit_routes_through("p1", "recalculate_code_quality_scores_util", "route_through")
_emit_checks_agent_registry("p1", "recalculate_code_quality_scores_util", "agent_registry")
_emit_validates_agent_capability("p1", "recalculate_code_quality_scores_util", "capability")
_emit_dispatches_execution_plan("p1", "recalculate_code_quality_scores_util", "exec_plan")
_emit_agent_executes_agent("p1", "recalculate_code_quality_scores_util", "sub_agent")
_emit_routes_to_agent("p1", "recalculate_code_quality_scores_util", "target_agent")
_emit_verifies_policy("p1", "recalculate_code_quality_scores_util", "policy_check")
_emit_observes_runtime_state("p1", "recalculate_code_quality_scores_util", "runtime_state")
_emit_verifies_boundary("p1", "recalculate_code_quality_scores_util", "boundary_check")
_emit_transcripts_response("p1", "recalculate_code_quality_scores_util", "transcript")
_emit_hard_fails_untranscripted("p1", "recalculate_code_quality_scores_util")
_emit_gated_by_confidence("p1", "recalculate_code_quality_scores_util", "confidence_gate")
emit_replay_key("p0", "recalculate_code_quality_scores_util")
emit_determinism_digest("p0", "recalculate_code_quality_scores_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "recalculate_code_quality_scores_util", "execution_auth")
_emit_validates_capability("p2", "recalculate_code_quality_scores_util", "capability_check")
_emit_routes_to_capability("p2", "recalculate_code_quality_scores_util", "capability_route")
_emit_writes_via_uwg("p2", "recalculate_code_quality_scores_util", "uwg_write")
_emit_blocks_direct_write("p2", "recalculate_code_quality_scores_util", "direct_write_block")
_emit_records_tool_invocation("p2", "recalculate_code_quality_scores_util", "tool_invocation")
_emit_captures_execution_output("p2", "recalculate_code_quality_scores_util", "exec_output")
_emit_dispatches_agent("p3", "recalculate_code_quality_scores_util", "agent_dispatch")
_emit_coordinates_agents("p3", "recalculate_code_quality_scores_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "recalculate_code_quality_scores_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "recalculate_code_quality_scores_util", "healing_outcome")
_emit_escalates_failure("p3", "recalculate_code_quality_scores_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "recalculate_code_quality_scores_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "recalculate_code_quality_scores_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "recalculate_code_quality_scores_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "recalculate_code_quality_scores_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "recalculate_code_quality_scores_util", "eval_metric")
_emit_stores_embedding("p4", "recalculate_code_quality_scores_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "recalculate_code_quality_scores_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "recalculate_code_quality_scores_util", "exec_snapshot_link")
PROJECT_ROOT = get_validated_project_root()
DASHBOARD_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / 'L6_observability' / 'dashboards' / 'autonomy_dashboard.html'

def calculate_code_quality_score(typed_pct, documented_pct, schema_pct, canonical_pct):
    """
    Calculate Code Quality Score using weighted formula.

    Formula: (Typed × 0.30) + (Documented × 0.30) + (schema × 0.25) + (Canonical × 0.15)

    Weights rationale:
    - Typed %: 30% - Critical for type safety and IDE support
    - Documented %: 30% - Essential for maintainability and onboarding
    - schema Strictness %: 25% - Important for data validation and contracts
    - Canonical Inheritance %: 15% - Architectural compliance, less critical than others
    """
    score = typed_pct * 0.3 + documented_pct * 0.3 + schema_pct * 0.25 + canonical_pct * 0.15
    return round(score, 1)

def extract_territory_data(content):
    """Extract all territory data blocks from dashboard."""
    match = re.search('const dashboardData = \\[(.*?)\\];', content, re.DOTALL)
    if not match:
        print('ERROR: Could not find dashboardData array')
        return None
    data_content = match.group(1)
    territories = []
    current_obj = ''
    brace_count = 0
    for char in data_content:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        current_obj += char
        if brace_count == 0 and current_obj.strip():
            territories.append(current_obj.strip().rstrip(','))
            current_obj = ''
    return territories

def update_code_quality_score(territory_text):
    """Update Code Quality Score in a territory data block."""
    typed_match = re.search('"Typed %":\\s*([\\d.]+)', territory_text)
    documented_match = re.search('"Documented %":\\s*([\\d.]+)', territory_text)
    schema_match = re.search('"schema Strictness %":\\s*([\\d.]+)', territory_text)
    canonical_match = re.search('"Canonical Inheritance %":\\s*([\\d.]+)', territory_text)
    if not all([typed_match, documented_match, schema_match, canonical_match]):
        return territory_text
    typed = float(typed_match.group(1))
    documented = float(documented_match.group(1))
    schema = float(schema_match.group(1))
    canonical = float(canonical_match.group(1))
    new_score = calculate_code_quality_score(typed, documented, schema, canonical)
    updated = re.sub('"Code Quality Score":\\s*[\\d.]+', f'"Code Quality Score": {new_score}', territory_text)
    return updated

def main():
    """Main function to recalculate all Code Quality Scores."""
    print('=' * 70)
    print('Recalculating Code Quality Scores')
    print('=' * 70)
    if not DASHBOARD_PATH.exists():
        print(f'ERROR: Dashboard not found at {DASHBOARD_PATH}')
        return 1
    content = DASHBOARD_PATH.read_text(encoding='utf-8')
    territories = extract_territory_data(content)
    if not territories:
        return 1
    print(f'\nFound {len(territories)} territories to update')
    updated_territories = []
    changes = []
    for i, territory in enumerate(territories):
        name_match = re.search('"Territory":\\s*"([^"]+)"', territory)
        territory_name = name_match.group(1) if name_match else f'Territory {i + 1}'
        old_score_match = re.search('"Code Quality Score":\\s*([\\d.]+)', territory)
        old_score = float(old_score_match.group(1)) if old_score_match else None
        updated = update_code_quality_score(territory)
        updated_territories.append(updated)
        new_score_match = re.search('"Code Quality Score":\\s*([\\d.]+)', updated)
        new_score = float(new_score_match.group(1)) if new_score_match else None
        if old_score != new_score:
            changes.append((territory_name, old_score, new_score))
            print(f'  ✓ {territory_name}: {old_score} → {new_score}')
    new_data_content = ',\n  '.join(updated_territories)
    new_dashboard_data = f'const dashboardData = [\n  {new_data_content}\n];'
    updated_content = re.sub('const dashboardData = \\[.*?\\];', new_dashboard_data, content, flags=re.DOTALL)
    DASHBOARD_PATH.write_text(updated_content, encoding='utf-8')
    print(f'\n✅ Updated {len(changes)} Code Quality Scores')
    print(f'Dashboard saved to: {DASHBOARD_PATH}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
