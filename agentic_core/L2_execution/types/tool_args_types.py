"""
Tool Registry Definitions - Phase 21.1 Restoration

Provides Pydantic models for tool argument validation.
These are used by the tool_registry to validate tool calls.
"""

from pydantic import BaseModel, Field

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "tool_args_types")
_emit_applies_guardrail("p0", "tool_args_types", "p0_governance")
_emit_snapshots_state("p0", "tool_args_types", "state_snapshot")


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
