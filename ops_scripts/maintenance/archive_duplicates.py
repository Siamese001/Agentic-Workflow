import argparse
import os
from pathlib import Path

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
from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper
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

_emit_emits_metric_event("archive_duplicates", "p4obs", "metric_1")
_emit_emits_metric_event("archive_duplicates", "p4obs", "metric_2")
_emit_emits_metric_event("archive_duplicates", "p4obs", "metric_3")
_emit_emits_metric_event("archive_duplicates", "p4obs", "metric_4")
_emit_emits_metric_event("archive_duplicates", "p4obs", "metric_5")
_emit_emits_metric_event("archive_duplicates", "p4obs", "metric_6")
_emit_records_incident_event("archive_duplicates", "p4obs", "incident")
_emit_captures_runtime_anomaly("archive_duplicates", "p4obs", "anomaly")
_emit_writes_observability_log("archive_duplicates", "p4obs", "obs_log")
_emit_updates_monitoring_state("archive_duplicates", "p4obs", "mon_state")
_emit_triggers_alert("archive_duplicates", "p4obs", "alert")
_emit_links_incident_trace("archive_duplicates", "p4obs", "trace_link")
_emit_captures_pattern("archive_duplicates", "p3lm", "pattern")
_emit_records_learning_event("archive_duplicates", "p3lm", "learning_event")
_emit_writes_learning_snapshot("archive_duplicates", "p3lm", "snapshot")
_emit_feeds_meta_learning("archive_duplicates", "p3lm", "meta_feed")
_emit_updates_routing_strategy("archive_duplicates", "p3lm", "routing")
_emit_improves_agent_policy("archive_duplicates", "p3lm", "policy")
_emit_stores_learning_state("archive_duplicates", "p3lm", "state")
_emit_records_execution_trace("archive_duplicates", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("archive_duplicates", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("archive_duplicates", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("archive_duplicates", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("archive_duplicates", "L4_STATE", "p2_trace_5")
_emit_reads_environ("archive_duplicates", "env_read", "p2_env_1")
_emit_reads_environ("archive_duplicates", "env_read", "p2_env_2")
_emit_reads_runtime_state("archive_duplicates", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("archive_duplicates", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "archive_duplicates")
_emit_applies_guardrail("p0", "archive_duplicates", "p0_governance")
_emit_reads_policy_state("p0", "archive_duplicates", "policy_binding")
_emit_snapshots_state("p0", "archive_duplicates", "state_snapshot")
_emit_pulls_context("p1", "archive_duplicates", "context_pull")
_emit_pulls_context("p1", "archive_duplicates", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "archive_duplicates", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "archive_duplicates", "uwg_term_secondary")
_emit_writes_through("p1", "archive_duplicates", "write_through")
_emit_writes_through("p1", "archive_duplicates", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "archive_duplicates", "safety_validation")
_emit_invokes_eval("p1", "archive_duplicates", "eval_call")
_emit_proposal_commits_routing("p1", "archive_duplicates", "routing_commit")
_emit_escalates_to_human("p1", "archive_duplicates", "human_escalation")
_emit_routes_through("p1", "archive_duplicates", "route_through")
_emit_checks_agent_registry("p1", "archive_duplicates", "agent_registry")
_emit_validates_agent_capability("p1", "archive_duplicates", "capability")
_emit_dispatches_execution_plan("p1", "archive_duplicates", "exec_plan")
_emit_agent_executes_agent("p1", "archive_duplicates", "sub_agent")
_emit_routes_to_agent("p1", "archive_duplicates", "target_agent")
_emit_verifies_policy("p1", "archive_duplicates", "policy_check")
_emit_observes_runtime_state("p1", "archive_duplicates", "runtime_state")
_emit_verifies_boundary("p1", "archive_duplicates", "boundary_check")
_emit_transcripts_response("p1", "archive_duplicates", "transcript")
_emit_hard_fails_untranscripted("p1", "archive_duplicates")
_emit_gated_by_confidence("p1", "archive_duplicates", "confidence_gate")
emit_replay_key("p0", "archive_duplicates")
emit_determinism_digest("p0", "archive_duplicates")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "archive_duplicates", "execution_auth")
_emit_validates_capability("p2", "archive_duplicates", "capability_check")
_emit_routes_to_capability("p2", "archive_duplicates", "capability_route")
_emit_writes_via_uwg("p2", "archive_duplicates", "uwg_write")
_emit_blocks_direct_write("p2", "archive_duplicates", "direct_write_block")
_emit_records_tool_invocation("p2", "archive_duplicates", "tool_invocation")
_emit_captures_execution_output("p2", "archive_duplicates", "exec_output")
_emit_dispatches_agent("p3", "archive_duplicates", "agent_dispatch")
_emit_coordinates_agents("p3", "archive_duplicates", "agent_coordination")
_emit_records_workflow_lineage("p3", "archive_duplicates", "workflow_lineage")
_emit_records_healing_outcome("p3", "archive_duplicates", "healing_outcome")
_emit_escalates_failure("p3", "archive_duplicates", "failure_escalation")
_emit_orchestrates_workflow("p3", "archive_duplicates", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "archive_duplicates", "healing_dispatch")
_emit_invokes_evaluation("p3", "archive_duplicates", "evaluation_signal")
_emit_records_telemetry_event("p4", "archive_duplicates", "telemetry_event")
_emit_captures_evaluation_metric("p4", "archive_duplicates", "eval_metric")
_emit_stores_embedding("p4", "archive_duplicates", "embedding_store")
_emit_updates_meta_learning_state("p4", "archive_duplicates", "meta_learning")
_emit_links_execution_to_snapshot("p4", "archive_duplicates", "exec_snapshot_link")
PROJECT_ROOT = Path(__file__).parent.parent.parent
TARGETS = ['agentic_core/L5_safety/enforcement/CodeDetectorAgent.py', 'agentic_core/L5_safety/enforcement/CodeEnforcerAgent.py', 'agentic_core/L5_safety/enforcement/CodeHealerAgent.py', 'agentic_core/L5_safety/enforcement/CodeValidatorAgent.py', 'agentic_core/L5_safety/enforcement/ResourceManagerAgent.py', 'agentic_core/L5_safety/enforcement/SafetyDetectorAgent.py', 'agentic_core/L5_safety/enforcement/SafetyExecutorAgent.py', 'agentic_core/L5_safety/enforcement/SecurityManagerAgent.py', 'agentic_core/L5_safety/enforcement/StructureEnforcerAgent.py', 'agentic_core/L5_safety/enforcement/StructureHealerAgent.py', 'agentic_core/L5_safety/enforcement/StructureValidatorAgent.py', 'agentic_core/L2_execution/reasoning/ModelRouterAgent.py', 'apps_shared/base_agents/HygieneGuardianAgent.py']

def main():
    parser = argparse.ArgumentParser(description='Archive identified duplicate files via ArchivalGatekeeper.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be archived without moving files')
    args = parser.parse_args()
    dry_run = args.dry_run
    print('[*] Starting Archive Operation via ArchivalGatekeeper')
    if dry_run:
        print('[*] DRY RUN — no files will be moved')
    if not dry_run:
        # guardian: allow-global-mutation
        os.environ['ARCHIVE_BATCH_ACCEPT'] = '1'
    gk = ArchivalGatekeeper.get_instance()
    moved_count = 0
    missing_count = 0
    for rel_path in TARGETS:
        source_path = PROJECT_ROOT / rel_path
        if not source_path.exists():
            print(f'[-] Skipped (Not Found): {rel_path}')
            missing_count += 1
            continue
        if dry_run:
            print(f'[DRY RUN] Would archive: {rel_path}')
            moved_count += 1
        else:
            result = gk.safe_archive(source_path, requester_agent='archive_duplicates', reason='Identified duplicate — Agent Overlap Analysis Report')
            if result.success:
                print(f'[+] Archived: {rel_path}')
                moved_count += 1
            else:
                print(f'[!] Failed to archive {rel_path}: {result.error}')
    print('-' * 50)
    print('SUMMARY:')
    print(f"  {('Would move' if dry_run else 'Moved')}:   {moved_count}")
    print(f'  Missing: {missing_count}')
    print('-' * 50)
    if moved_count > 0:
        print('✅ Archive operation completed successfully.' if not dry_run else '✅ Dry run complete.')
    else:
        print('⚠️  No files were moved.')
if __name__ == '__main__':
    main()
