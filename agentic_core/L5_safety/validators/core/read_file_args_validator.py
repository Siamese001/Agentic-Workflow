from __future__ import annotations

"""
Tool Arguments schema
====================
Defines the Pydantic models for all tool-calling arguments within the
Sovereign system. These models enforce strict path validation and
execution guardrails.
"""

from pathlib import Path

from pydantic import BaseModel, Field, validator

# ==========================================
# File System Tool Arguments
# ==========================================


class ReadFileArgs(BaseModel):
    """Arguments for reading a file."""

    path: str = Field(..., description="Relative path to the file to read")

    @validator("path")
    def validate_path(cls, v):
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
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class DeleteFileArgs(BaseModel):
    """Arguments for deleting a file."""

    path: str = Field(..., description="Relative path to the file to delete")

    @validator("path")
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


class CreateDirectoryArgs(BaseModel):
    """Arguments for creating a directory."""

    path: str = Field(..., description="Relative path to the directory to create")
    parents: bool = Field(default=True, description="Create parent directories if they don't exist")

    @validator("path")
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


# ==========================================
# Execution Tool Arguments
# ==========================================


class ExecuteCommandArgs(BaseModel):
    """Arguments for executing a shell command."""

    command: str = Field(..., description="Command to execute")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    cwd: str | None = Field(default=None, description="Working directory (relative to project root)")
    timeout: int = Field(default=30, description="Timeout in seconds (max 300)")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")

    @validator("timeout")
    def validate_timeout(cls, v):
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
