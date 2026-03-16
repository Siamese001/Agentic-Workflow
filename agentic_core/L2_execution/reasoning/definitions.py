"""
definitions - canonical re-export shim.

The implementation lives in agentic_core.L2_execution.types.tool_args_types.
This module re-exports for callers using
``from agentic_core.L2_execution.reasoning.definitions import ReadFileArgs, ...``.
"""

from agentic_core.L2_execution.types.tool_args_types import (  # noqa: F401
    CreateDirectoryArgs,
    DeleteFileArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "definitions")
emit_determinism_digest("p0", "definitions")

_emit_dispatches_healing_run("p1", "definitions", "L2")
_emit_routes_through("p1", "definitions", "L2")
_emit_escalates_to_human("p1", "definitions", "L2")
_emit_reads_policy_state("p1", "definitions", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "definitions")
_emit_applies_guardrail("p0", "definitions", "p0_governance")
_emit_snapshots_state("p0", "definitions", "state_snapshot")
_emit_authorize_and_execute("p2", "definitions", "execution_auth")
_emit_validates_capability("p2", "definitions", "capability_check")
_emit_routes_to_capability("p2", "definitions", "capability_route")
_emit_writes_via_uwg("p2", "definitions", "uwg_write")
_emit_blocks_direct_write("p2", "definitions", "direct_write_block")
_emit_records_tool_invocation("p2", "definitions", "tool_invocation")
_emit_captures_execution_output("p2", "definitions", "exec_output")
_emit_dispatches_agent("p3", "definitions", "agent_dispatch")
_emit_coordinates_agents("p3", "definitions", "agent_coordination")
_emit_records_workflow_lineage("p3", "definitions", "workflow_lineage")
_emit_records_healing_outcome("p3", "definitions", "healing_outcome")
_emit_escalates_failure("p3", "definitions", "failure_escalation")
_emit_orchestrates_workflow("p3", "definitions", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "definitions", "healing_dispatch")
_emit_invokes_evaluation("p3", "definitions", "evaluation_signal")
_emit_records_telemetry_event("p4", "definitions", "telemetry_event")
_emit_captures_evaluation_metric("p4", "definitions", "eval_metric")
_emit_stores_embedding("p4", "definitions", "embedding_store")
_emit_updates_meta_learning_state("p4", "definitions", "meta_learning")
_emit_links_execution_to_snapshot("p4", "definitions", "exec_snapshot_link")

__all__ = [
    "CreateDirectoryArgs",
    "DeleteFileArgs",
    "ListFilesArgs",
    "MoveFileArgs",
    "ReadFileArgs",
    "WriteFileArgs",
]
