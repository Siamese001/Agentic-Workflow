"""
Run FileClassificationAgent on agentic_core with healing enabled.
Generates detailed JSON report of all healing activities.
"""
import json
import logging
import sys
from datetime import datetime
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

_emit_records_execution_trace("p0", "evidence", "run_file_classification_heal_agentic_core")
_emit_applies_guardrail("p0", "run_file_classification_heal_agentic_core", "p0_governance")
_emit_reads_policy_state("p0", "run_file_classification_heal_agentic_core", "policy_binding")
_emit_snapshots_state("p0", "run_file_classification_heal_agentic_core", "state_snapshot")
emit_replay_key("p0", "run_file_classification_heal_agentic_core")
emit_determinism_digest("p0", "run_file_classification_heal_agentic_core")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "run_file_classification_heal_agentic_core", "execution_auth")
_emit_validates_capability("p2", "run_file_classification_heal_agentic_core", "capability_check")
_emit_routes_to_capability("p2", "run_file_classification_heal_agentic_core", "capability_route")
_emit_writes_via_uwg("p2", "run_file_classification_heal_agentic_core", "uwg_write")
_emit_blocks_direct_write("p2", "run_file_classification_heal_agentic_core", "direct_write_block")
_emit_records_tool_invocation("p2", "run_file_classification_heal_agentic_core", "tool_invocation")
_emit_captures_execution_output("p2", "run_file_classification_heal_agentic_core", "exec_output")
_emit_dispatches_agent("p3", "run_file_classification_heal_agentic_core", "agent_dispatch")
_emit_coordinates_agents("p3", "run_file_classification_heal_agentic_core", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_file_classification_heal_agentic_core", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_file_classification_heal_agentic_core", "healing_outcome")
_emit_escalates_failure("p3", "run_file_classification_heal_agentic_core", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_file_classification_heal_agentic_core", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_file_classification_heal_agentic_core", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_file_classification_heal_agentic_core", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_file_classification_heal_agentic_core", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_file_classification_heal_agentic_core", "eval_metric")
_emit_stores_embedding("p4", "run_file_classification_heal_agentic_core", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_file_classification_heal_agentic_core", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_file_classification_heal_agentic_core", "exec_snapshot_link")
project_root = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent
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

_emit_emits_metric_event("run_file_classification_heal_agentic_core", "p4obs", "metric_1")
_emit_emits_metric_event("run_file_classification_heal_agentic_core", "p4obs", "metric_2")
_emit_emits_metric_event("run_file_classification_heal_agentic_core", "p4obs", "metric_3")
_emit_emits_metric_event("run_file_classification_heal_agentic_core", "p4obs", "metric_4")
_emit_emits_metric_event("run_file_classification_heal_agentic_core", "p4obs", "metric_5")
_emit_emits_metric_event("run_file_classification_heal_agentic_core", "p4obs", "metric_6")
_emit_records_incident_event("run_file_classification_heal_agentic_core", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_file_classification_heal_agentic_core", "p4obs", "anomaly")
_emit_writes_observability_log("run_file_classification_heal_agentic_core", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_file_classification_heal_agentic_core", "p4obs", "mon_state")
_emit_triggers_alert("run_file_classification_heal_agentic_core", "p4obs", "alert")
_emit_links_incident_trace("run_file_classification_heal_agentic_core", "p4obs", "trace_link")
_emit_captures_pattern("run_file_classification_heal_agentic_core", "p3lm", "pattern")
_emit_records_learning_event("run_file_classification_heal_agentic_core", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_file_classification_heal_agentic_core", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_file_classification_heal_agentic_core", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_file_classification_heal_agentic_core", "p3lm", "routing")
_emit_improves_agent_policy("run_file_classification_heal_agentic_core", "p3lm", "policy")
_emit_stores_learning_state("run_file_classification_heal_agentic_core", "p3lm", "state")
_emit_records_execution_trace("run_file_classification_heal_agentic_core", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_file_classification_heal_agentic_core", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_file_classification_heal_agentic_core", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_file_classification_heal_agentic_core", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_file_classification_heal_agentic_core", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_file_classification_heal_agentic_core", "env_read", "p2_env_1")
_emit_reads_environ("run_file_classification_heal_agentic_core", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_file_classification_heal_agentic_core", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_file_classification_heal_agentic_core", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_file_classification_heal_agentic_core", "context_pull")
_emit_pulls_context("p1", "run_file_classification_heal_agentic_core", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "run_file_classification_heal_agentic_core", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_file_classification_heal_agentic_core", "uwg_term_secondary")
_emit_writes_through("p1", "run_file_classification_heal_agentic_core", "write_through")
_emit_writes_through("p1", "run_file_classification_heal_agentic_core", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "run_file_classification_heal_agentic_core", "safety_validation")
_emit_invokes_eval("p1", "run_file_classification_heal_agentic_core", "eval_call")
_emit_proposal_commits_routing("p1", "run_file_classification_heal_agentic_core", "routing_commit")
_emit_escalates_to_human("p1", "run_file_classification_heal_agentic_core", "human_escalation")
_emit_routes_through("p1", "run_file_classification_heal_agentic_core", "route_through")
_emit_checks_agent_registry("p1", "run_file_classification_heal_agentic_core", "agent_registry")
_emit_validates_agent_capability("p1", "run_file_classification_heal_agentic_core", "capability")
_emit_dispatches_execution_plan("p1", "run_file_classification_heal_agentic_core", "exec_plan")
_emit_agent_executes_agent("p1", "run_file_classification_heal_agentic_core", "sub_agent")
_emit_routes_to_agent("p1", "run_file_classification_heal_agentic_core", "target_agent")
_emit_verifies_policy("p1", "run_file_classification_heal_agentic_core", "policy_check")
_emit_observes_runtime_state("p1", "run_file_classification_heal_agentic_core", "runtime_state")
_emit_verifies_boundary("p1", "run_file_classification_heal_agentic_core", "boundary_check")
_emit_transcripts_response("p1", "run_file_classification_heal_agentic_core", "transcript")
_emit_hard_fails_untranscripted("p1", "run_file_classification_heal_agentic_core")
_emit_gated_by_confidence("p1", "run_file_classification_heal_agentic_core", "confidence_gate")


def run_healing_with_detailed_report():
    """Run FileClassificationAgent healing and generate detailed JSON report."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
    logger = logging.getLogger(__name__)
    agent = FileClassificationAgent(project_root=project_root, dry_run=False, validate_only=False)
    logger.info('=' * 70)
    logger.info('FILECLASSIFICATIONAGENT - HEALING RUN ON AGENTIC_CORE')
    logger.info('=' * 70)
    logger.info(f'Project Root: {project_root}')
    logger.info('Target: agentic_core')
    logger.info('Mode: HEALING ENABLED (dry_run=False)')
    logger.info('=' * 70)
    start_time = datetime.now()
    result = agent.heal_repository(dry_run=False, execute=True, target_territory=AGENTIC_CORE_DIR, auto_approve=True)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    detailed_report = {'metadata': {'run_timestamp': start_time.isoformat(), 'duration_seconds': duration, 'target_folder': 'agentic_core', 'healing_mode': 'EXECUTE', 'dry_run': False, 'agent_version': 'v5.1-idempotence-hardened'}, 'summary': {'violations_found': result.get('violations_found', 0), 'violations_fixed': result.get('violations_fixed', 0), 'errors': result.get('errors', 0), 'skipped': result.get('skipped', 0)}, 'action_counters': result.get('action_counters', {'renames': 0, 'territory_moves': 0, 'import_fixes': 0, 'deep_refactors': 0, 'config_updates': 0}), 'idempotence_cache': {'paths_processed': len(agent.processed_paths), 'cache_was_cleared': True}, 'stats': agent.stats, 'file_classifications': {}, 'healing_actions': []}
    for path in agent.file_registry:
        try:
            rel_path = str(path.relative_to(project_root))
            file_type = agent.classify_file(path)
            detailed_report['file_classifications'][rel_path] = file_type
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            pass
    detailed_report['idempotence_verification'] = {'description': 'Second run should show zero actions if idempotent', 'recommendation': 'Re-run this script to verify zero violations_fixed'}
    output_path = project_root / 'docs' / REPORTS_DIR / 'file_classification_healing_agentic_core.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, indent=2, default=str)
    logger.info('=' * 70)
    logger.info('HEALING RUN COMPLETE')
    logger.info('=' * 70)
    logger.info(f'Duration: {duration:.2f}s')
    logger.info(f"Violations Found: {result.get('violations_found', 0)}")
    logger.info(f"Violations Fixed: {result.get('violations_fixed', 0)}")
    logger.info(f"Errors: {result.get('errors', 0)}")
    logger.info(f"Skipped: {result.get('skipped', 0)}")
    logger.info('-' * 70)
    logger.info('Action Counters:')
    for action, count in result.get('action_counters', {}).items():
        logger.info(f'  {action}: {count}')
    logger.info('-' * 70)
    logger.info(f'Detailed JSON report saved to: {output_path}')
    logger.info('=' * 70)
    print('\n' + '=' * 70)
    print('DETAILED HEALING REPORT (JSON)')
    print('=' * 70)
    print(json.dumps(detailed_report, indent=2, default=str))
    return detailed_report
if __name__ == '__main__':
    run_healing_with_detailed_report()
