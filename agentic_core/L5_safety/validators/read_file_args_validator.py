from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "read_file_args_validator", "L5")
_emit_routes_through("p1", "read_file_args_validator", "L5")
_emit_escalates_to_human("p1", "read_file_args_validator", "L5")
_emit_reads_policy_state("p1", "read_file_args_validator", "L5")

_emit_applies_guardrail("p0", "read_file_args_validator", "p0_governance")
_emit_snapshots_state("p0", "read_file_args_validator", "state_snapshot")

"\nTool Arguments schema\n====================\nDefines the Pydantic models for all tool-calling arguments within the\nSovereign system. These models enforce strict path validation and\nexecution guardrails.\n"
import uuid
from pathlib import Path

from pydantic import BaseModel, Field, validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_validated_by_safety_plane,
)


class ReadFileArgs(BaseModel):
    """Arguments for reading a file."""

    path: str = Field(..., description="Relative path to the file to read")

    @validator("path")
    def validate_path(cls, v):
        _emit_validated_by_safety_plane(str(uuid.uuid4()), "ReadFileArgs.validate_path", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ReadFileArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReadFileArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class WriteFileArgs(BaseModel):
    """Arguments for writing to a file."""

    path: str = Field(..., description="Relative path to the file to write")
    content: str = Field(..., description="Content to write to the file")
    create_dirs: bool = Field(default=True, description="Create parent directories if they don't exist")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "WriteFileArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteFileArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class MoveFileArgs(BaseModel):
    """Arguments for moving/renaming a file."""

    source: str = Field(..., description="Relative path to the source file")
    destination: str = Field(..., description="Relative path to the destination")
    overwrite: bool = Field(default=False, description="Overwrite destination if it exists")

    @validator("source", "destination")
    def validate_paths(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "MoveFileArgs.validate_paths")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MoveFileArgs.validate_paths".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Paths must be relative to project root")
        return v


class ListFilesArgs(BaseModel):
    """Arguments for listing files in a directory."""

    path: str = Field(default=".", description="Relative path to the directory to list")
    pattern: str | None = Field(default=None, description="Glob pattern to filter files (e.g., '*.py')")
    recursive: bool = Field(default=False, description="Recursively list subdirectories")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ListFilesArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ListFilesArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class DeleteFileArgs(BaseModel):
    """Arguments for deleting a file."""

    path: str = Field(..., description="Relative path to the file to delete")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "DeleteFileArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DeleteFileArgs.validate_path".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class CreateDirectoryArgs(BaseModel):
    """Arguments for creating a directory."""

    path: str = Field(..., description="Relative path to the directory to create")
    parents: bool = Field(default=True, description="Create parent directories if they don't exist")

    @validator("path")
    def validate_path(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "CreateDirectoryArgs.validate_path")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CreateDirectoryArgs.validate_path".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class ExecuteCommandArgs(BaseModel):
    """Arguments for executing a shell command."""

    command: str = Field(..., description="Command to execute")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    cwd: str | None = Field(default=None, description="Working directory (relative to project root)")
    timeout: int = Field(default=30, description="Timeout in seconds (max 300)")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")

    @validator("timeout")
    def validate_timeout(cls, v):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ExecuteCommandArgs.validate_timeout"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecuteCommandArgs.validate_timeout".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds to prevent livelocks")
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v

    @validator("cwd")
    def validate_cwd(cls, v):
        if v and Path(v).is_absolute():
            raise ValueError("Working directory must be relative to project root")
        return v
