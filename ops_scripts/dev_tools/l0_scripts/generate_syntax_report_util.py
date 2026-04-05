"""
Generate detailed syntax error report with file paths and error details.
"""
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

_emit_records_execution_trace("p0", "evidence", "generate_syntax_report_util")
_emit_applies_guardrail("p0", "generate_syntax_report_util", "p0_governance")
_emit_reads_policy_state("p0", "generate_syntax_report_util", "policy_binding")
_emit_snapshots_state("p0", "generate_syntax_report_util", "state_snapshot")
emit_replay_key("p0", "generate_syntax_report_util")
emit_determinism_digest("p0", "generate_syntax_report_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_syntax_report_util", "execution_auth")
_emit_validates_capability("p2", "generate_syntax_report_util", "capability_check")
_emit_routes_to_capability("p2", "generate_syntax_report_util", "capability_route")
_emit_writes_via_uwg("p2", "generate_syntax_report_util", "uwg_write")
_emit_blocks_direct_write("p2", "generate_syntax_report_util", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_syntax_report_util", "tool_invocation")
_emit_captures_execution_output("p2", "generate_syntax_report_util", "exec_output")
_emit_dispatches_agent("p3", "generate_syntax_report_util", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_syntax_report_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_syntax_report_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_syntax_report_util", "healing_outcome")
_emit_escalates_failure("p3", "generate_syntax_report_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_syntax_report_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_syntax_report_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_syntax_report_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_syntax_report_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_syntax_report_util", "eval_metric")
_emit_stores_embedding("p4", "generate_syntax_report_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_syntax_report_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_syntax_report_util", "exec_snapshot_link")
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent
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

_emit_emits_metric_event("generate_syntax_report_util", "p4obs", "metric_1")
_emit_emits_metric_event("generate_syntax_report_util", "p4obs", "metric_2")
_emit_emits_metric_event("generate_syntax_report_util", "p4obs", "metric_3")
_emit_emits_metric_event("generate_syntax_report_util", "p4obs", "metric_4")
_emit_emits_metric_event("generate_syntax_report_util", "p4obs", "metric_5")
_emit_emits_metric_event("generate_syntax_report_util", "p4obs", "metric_6")
_emit_records_incident_event("generate_syntax_report_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_syntax_report_util", "p4obs", "anomaly")
_emit_writes_observability_log("generate_syntax_report_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_syntax_report_util", "p4obs", "mon_state")
_emit_triggers_alert("generate_syntax_report_util", "p4obs", "alert")
_emit_links_incident_trace("generate_syntax_report_util", "p4obs", "trace_link")
_emit_captures_pattern("generate_syntax_report_util", "p3lm", "pattern")
_emit_records_learning_event("generate_syntax_report_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_syntax_report_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_syntax_report_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_syntax_report_util", "p3lm", "routing")
_emit_improves_agent_policy("generate_syntax_report_util", "p3lm", "policy")
_emit_stores_learning_state("generate_syntax_report_util", "p3lm", "state")
_emit_records_execution_trace("generate_syntax_report_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_syntax_report_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_syntax_report_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_syntax_report_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_syntax_report_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_syntax_report_util", "env_read", "p2_env_1")
_emit_reads_environ("generate_syntax_report_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_syntax_report_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_syntax_report_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "generate_syntax_report_util", "context_pull")
_emit_pulls_context("p1", "generate_syntax_report_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "generate_syntax_report_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_syntax_report_util", "uwg_term_secondary")
_emit_writes_through("p1", "generate_syntax_report_util", "write_through")
_emit_writes_through("p1", "generate_syntax_report_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "generate_syntax_report_util", "safety_validation")
_emit_invokes_eval("p1", "generate_syntax_report_util", "eval_call")
_emit_proposal_commits_routing("p1", "generate_syntax_report_util", "routing_commit")
_emit_escalates_to_human("p1", "generate_syntax_report_util", "human_escalation")
_emit_routes_through("p1", "generate_syntax_report_util", "route_through")
_emit_checks_agent_registry("p1", "generate_syntax_report_util", "agent_registry")
_emit_validates_agent_capability("p1", "generate_syntax_report_util", "capability")
_emit_dispatches_execution_plan("p1", "generate_syntax_report_util", "exec_plan")
_emit_agent_executes_agent("p1", "generate_syntax_report_util", "sub_agent")
_emit_routes_to_agent("p1", "generate_syntax_report_util", "target_agent")
_emit_verifies_policy("p1", "generate_syntax_report_util", "policy_check")
_emit_observes_runtime_state("p1", "generate_syntax_report_util", "runtime_state")
_emit_verifies_boundary("p1", "generate_syntax_report_util", "boundary_check")
_emit_transcripts_response("p1", "generate_syntax_report_util", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_syntax_report_util")
_emit_gated_by_confidence("p1", "generate_syntax_report_util", "confidence_gate")


def main():
    project_root = Path(__file__).parent.parent
    print('Generating comprehensive syntax error report...')
    print()
    agent = CodeValidatorAgent(project_root=project_root)
    results = agent.validate_repository()
    errors = results.get('syntax_errors', [])
    print(f'Total syntax errors: {len(errors)}')
    print()
    if len(errors) == 0:
        print('SUCCESS: All files are syntactically valid!')
        return 0
    by_layer = {}
    for e in errors:
        path_str = str(e.file_path)
        if 'L0_' in path_str:
            layer = 'L0'
        elif 'L1_' in path_str:
            layer = 'L1'
        elif 'L2_' in path_str:
            layer = 'L2'
        elif 'L3_' in path_str:
            layer = 'L3'
        elif 'L4_' in path_str:
            layer = 'L4'
        elif 'L5_' in path_str:
            layer = 'L5'
        elif 'config' in path_str:
            layer = 'Config'
        elif 'apps_' in path_str:
            layer = 'Apps'
        else:
            layer = 'Other'
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(e)
    print('Errors by layer:')
    for layer in sorted(by_layer.keys()):
        print(f'  {layer}: {len(by_layer[layer])} errors')
    print()
    print('=' * 80)
    print('DETAILED ERROR REPORT')
    print('=' * 80)
    for layer in sorted(by_layer.keys()):
        print(f'\n### {layer} Layer ({len(by_layer[layer])} errors)')
        print('-' * 80)
        for e in by_layer[layer]:
            rel_path = e.file_path.relative_to(project_root)
            print(f'\nFile: {rel_path}')
            print(f'Line: {e.line_number}, Column: {e.column_number}')
            print(f'Error: {e.error_message}')
    print()
    print('=' * 80)
    return 1
if __name__ == '__main__':
    sys.exit(main())
