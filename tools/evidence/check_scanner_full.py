"""Full scanner violation dump for all buckets."""
from pathlib import Path

from agentic_core.L5_safety.static_checks.system_invariant_scanner import scan_repository_for_bypasses
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

_emit_records_execution_trace("p0", "evidence", "check_scanner_full")
_emit_applies_guardrail("p0", "check_scanner_full", "p0_governance")
_emit_reads_policy_state("p0", "check_scanner_full", "policy_binding")
_emit_snapshots_state("p0", "check_scanner_full", "state_snapshot")
emit_replay_key("p0", "check_scanner_full")
emit_determinism_digest("p0", "check_scanner_full")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_scanner_full", "execution_auth")
_emit_validates_capability("p2", "check_scanner_full", "capability_check")
_emit_routes_to_capability("p2", "check_scanner_full", "capability_route")
_emit_writes_via_uwg("p2", "check_scanner_full", "uwg_write")
_emit_blocks_direct_write("p2", "check_scanner_full", "direct_write_block")
_emit_records_tool_invocation("p2", "check_scanner_full", "tool_invocation")
_emit_captures_execution_output("p2", "check_scanner_full", "exec_output")
_emit_dispatches_agent("p3", "check_scanner_full", "agent_dispatch")
_emit_coordinates_agents("p3", "check_scanner_full", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_scanner_full", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_scanner_full", "healing_outcome")
_emit_escalates_failure("p3", "check_scanner_full", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_scanner_full", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_scanner_full", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_scanner_full", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_scanner_full", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_scanner_full", "eval_metric")
_emit_stores_embedding("p4", "check_scanner_full", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_scanner_full", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_scanner_full", "exec_snapshot_link")
root = Path(__file__).resolve().parents[2]
for bucket_rel in [L2_EXECUTION_DIR, L5_SAFETY_DIR, 'tests/sovereign_hardening']:
    bucket = (root / bucket_rel).resolve()
    violations = scan_repository_for_bypasses(bucket)
    prefix = str(bucket)
    filtered = [v for v in violations if str(Path(v.file_path).resolve()).startswith(prefix)]
    py_files = [f for f in bucket.rglob('*.py') if '__pycache__' not in f.parts]
    print(f'\n=== {bucket_rel}: {len(py_files)} files, {len(filtered)} violations ===')
    for v in filtered:
        print(f'  {Path(v.file_path).name}:{v.line} [{v.rule_id}]')
