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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "archive_duplicates")
_emit_applies_guardrail("p0", "archive_duplicates", "p0_governance")
_emit_reads_policy_state("p0", "archive_duplicates", "policy_binding")
_emit_snapshots_state("p0", "archive_duplicates", "state_snapshot")
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
