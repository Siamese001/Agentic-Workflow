"""Test fixer directly on the specific file."""
import sys

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

_emit_records_execution_trace("p0", "evidence", "_test_fixer")
_emit_applies_guardrail("p0", "_test_fixer", "p0_governance")
_emit_reads_policy_state("p0", "_test_fixer", "policy_binding")
_emit_snapshots_state("p0", "_test_fixer", "state_snapshot")
emit_replay_key("p0", "_test_fixer")
emit_determinism_digest("p0", "_test_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_test_fixer", "execution_auth")
_emit_validates_capability("p2", "_test_fixer", "capability_check")
_emit_routes_to_capability("p2", "_test_fixer", "capability_route")
_emit_writes_via_uwg("p2", "_test_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "_test_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "_test_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "_test_fixer", "exec_output")
_emit_dispatches_agent("p3", "_test_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "_test_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "_test_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "_test_fixer", "healing_outcome")
_emit_escalates_failure("p3", "_test_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "_test_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_test_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "_test_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "_test_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_test_fixer", "eval_metric")
_emit_stores_embedding("p4", "_test_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "_test_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_test_fixer", "exec_snapshot_link")
# guardian: allow-global-mutation
sys.path.insert(0, '.')
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
from ops_scripts.ci._fix_hardcoded_ssot_literals import process_file

file_path = Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py')
dry_run = True
fixes = process_file(file_path, str(file_path), dry_run=dry_run)
print(f'Found {len(fixes)} fixes:')
for fix in fixes:
    print(f'  {fix}')
