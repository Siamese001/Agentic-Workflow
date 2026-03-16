import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "_sample_violations")
_emit_applies_guardrail("p0", "_sample_violations", "p0_governance")
_emit_reads_policy_state("p0", "_sample_violations", "policy_binding")
_emit_snapshots_state("p0", "_sample_violations", "state_snapshot")
emit_replay_key("p0", "_sample_violations")
emit_determinism_digest("p0", "_sample_violations")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_sample_violations", "execution_auth")
_emit_validates_capability("p2", "_sample_violations", "capability_check")
_emit_routes_to_capability("p2", "_sample_violations", "capability_route")
_emit_writes_via_uwg("p2", "_sample_violations", "uwg_write")
_emit_blocks_direct_write("p2", "_sample_violations", "direct_write_block")
_emit_records_tool_invocation("p2", "_sample_violations", "tool_invocation")
_emit_captures_execution_output("p2", "_sample_violations", "exec_output")
_emit_dispatches_agent("p3", "_sample_violations", "agent_dispatch")
_emit_coordinates_agents("p3", "_sample_violations", "agent_coordination")
_emit_records_workflow_lineage("p3", "_sample_violations", "workflow_lineage")
_emit_records_healing_outcome("p3", "_sample_violations", "healing_outcome")
_emit_escalates_failure("p3", "_sample_violations", "failure_escalation")
_emit_orchestrates_workflow("p3", "_sample_violations", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_sample_violations", "healing_dispatch")
_emit_invokes_evaluation("p3", "_sample_violations", "evaluation_signal")
_emit_records_telemetry_event("p4", "_sample_violations", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_sample_violations", "eval_metric")
_emit_stores_embedding("p4", "_sample_violations", "embedding_store")
_emit_updates_meta_learning_state("p4", "_sample_violations", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_sample_violations", "exec_snapshot_link")
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

project_root = get_validated_project_root()
baseline = project_root / "ops_scripts/hooks/landmine_baseline.txt"

lines = [l.strip() for l in baseline.read_text(encoding='utf-8').splitlines() if l.strip()]

for cat in ['silent_swallower', 'magic_configuration', 'global_mutation']:
    cat_lines = [l for l in lines if f':{cat}:' in l]
    print(f'\n{cat} ({len(cat_lines)} total):')
    for s in cat_lines[:5]:
        print(f'  {s}')
