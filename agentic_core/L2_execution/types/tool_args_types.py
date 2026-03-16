"""
Tool Registry Definitions - Phase 21.1 Restoration

Provides Pydantic models for tool argument validation.
These are used by the tool_registry to validate tool calls.
"""

from pydantic import BaseModel, Field

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

emit_replay_key("p0", "tool_args_types")
emit_determinism_digest("p0", "tool_args_types")

_emit_dispatches_healing_run("p1", "tool_args_types", "L2")
_emit_routes_through("p1", "tool_args_types", "L2")
_emit_escalates_to_human("p1", "tool_args_types", "L2")
_emit_reads_policy_state("p1", "tool_args_types", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "tool_args_types")
_emit_applies_guardrail("p0", "tool_args_types", "p0_governance")
_emit_snapshots_state("p0", "tool_args_types", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_args_types", "execution_auth")
_emit_validates_capability("p2", "tool_args_types", "capability_check")
_emit_routes_to_capability("p2", "tool_args_types", "capability_route")
_emit_writes_via_uwg("p2", "tool_args_types", "uwg_write")
_emit_blocks_direct_write("p2", "tool_args_types", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_args_types", "tool_invocation")
_emit_captures_execution_output("p2", "tool_args_types", "exec_output")
_emit_dispatches_agent("p3", "tool_args_types", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_args_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_args_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_args_types", "healing_outcome")
_emit_escalates_failure("p3", "tool_args_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_args_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_args_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_args_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_args_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_args_types", "eval_metric")
_emit_stores_embedding("p4", "tool_args_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_args_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_args_types", "exec_snapshot_link")


class ReadFileArgs(BaseModel):
    """Arguments for reading a file."""

    path: str = Field(..., description="Path to the file to read")


class WriteFileArgs(BaseModel):
    """Arguments for writing to a file."""

    path: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")


class ListFilesArgs(BaseModel):
    """Arguments for listing files in a directory."""

    directory: str = Field(..., description="Directory to list files from")
    pattern: str | None = Field(None, description="Optional glob pattern to filter files")


class MoveFileArgs(BaseModel):
    """Arguments for moving/renaming a file."""

    source: str = Field(..., description="Source file path")
    destination: str = Field(..., description="Destination file path")


class DeleteFileArgs(BaseModel):
    """Arguments for deleting a file."""

    path: str = Field(..., description="Path to the file to delete")


class CreateDirectoryArgs(BaseModel):
    """Arguments for creating a directory."""

    path: str = Field(..., description="Path to the directory to create")


class ExecuteCommandArgs(BaseModel):
    """Arguments for executing a shell command."""

    command: str = Field(..., description="Shell command to execute")
    cwd: str | None = Field(None, description="Working directory for the command")
