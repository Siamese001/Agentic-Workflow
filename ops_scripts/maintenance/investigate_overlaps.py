import hashlib
import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_records_execution_trace("p0", "evidence", "investigate_overlaps")
_emit_applies_guardrail("p0", "investigate_overlaps", "p0_governance")
_emit_reads_policy_state("p0", "investigate_overlaps", "policy_binding")
_emit_snapshots_state("p0", "investigate_overlaps", "state_snapshot")
emit_replay_key("p0", "investigate_overlaps")
emit_determinism_digest("p0", "investigate_overlaps")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "investigate_overlaps", "execution_auth")
_emit_validates_capability("p2", "investigate_overlaps", "capability_check")
_emit_routes_to_capability("p2", "investigate_overlaps", "capability_route")
_emit_writes_via_uwg("p2", "investigate_overlaps", "uwg_write")
_emit_blocks_direct_write("p2", "investigate_overlaps", "direct_write_block")
_emit_records_tool_invocation("p2", "investigate_overlaps", "tool_invocation")
_emit_captures_execution_output("p2", "investigate_overlaps", "exec_output")
_emit_dispatches_agent("p3", "investigate_overlaps", "agent_dispatch")
_emit_coordinates_agents("p3", "investigate_overlaps", "agent_coordination")
_emit_records_workflow_lineage("p3", "investigate_overlaps", "workflow_lineage")
_emit_records_healing_outcome("p3", "investigate_overlaps", "healing_outcome")
_emit_escalates_failure("p3", "investigate_overlaps", "failure_escalation")
_emit_orchestrates_workflow("p3", "investigate_overlaps", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "investigate_overlaps", "healing_dispatch")
_emit_invokes_evaluation("p3", "investigate_overlaps", "evaluation_signal")
_emit_records_telemetry_event("p4", "investigate_overlaps", "telemetry_event")
_emit_captures_evaluation_metric("p4", "investigate_overlaps", "eval_metric")
_emit_stores_embedding("p4", "investigate_overlaps", "embedding_store")
_emit_updates_meta_learning_state("p4", "investigate_overlaps", "meta_learning")
_emit_links_execution_to_snapshot("p4", "investigate_overlaps", "exec_snapshot_link")
PROJECT_ROOT = get_validated_project_root()
GROUPS = {'Location': ['LocationAgent.py', 'LocationValidatorAgent.py', 'LocationHealerAgent.py'], 'Hierarchy': ['HierarchyAgent.py', 'HierarchyValidatorAgent.py'], 'Import': ['ImportAgent.py', 'ImportLockAgent.py'], 'Strategic': ['StrategicRecommendationAgent.py', 'StrategicPlannerAgent.py']}

def get_file_hash(path: Path):
    if not path.exists():
        return None
    return hashlib.md5(path.read_bytes()).hexdigest()

def investigate():
    print('[*] Investigating Potential Overlaps...')
    print(f'[*] Project Root: {PROJECT_ROOT}')
    for group_name, filenames in GROUPS.items():
        print(f'\n--- Group: {group_name} ---')
        found_files = []
        for root, dirs, files in os.walk(PROJECT_ROOT / AGENTIC_CORE_DIR):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for f in files:
                if f in filenames:
                    found_files.append(Path(root) / f)
        if not found_files:
            print('  No files found.')
            continue
        for f_path in found_files:
            f_hash = get_file_hash(f_path)
            rel_path = f_path.relative_to(PROJECT_ROOT)
            print(f'  Found: {rel_path} (MD5: {f_hash[:8]}...)')
        hashes = [get_file_hash(p) for p in found_files]
        unique_hashes = set(hashes)
        if len(unique_hashes) < len(hashes):
            print('  [!] WARNING: Identical MD5 hashes detected in this group. Consolidation required.')
        else:
            print('  [✓] Implementation patterns differ. Likely intentional separation.')
if __name__ == '__main__':
    investigate()
