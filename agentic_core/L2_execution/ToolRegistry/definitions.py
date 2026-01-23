"""
Tool Registry Definitions - Phase 21.1 Restoration

Provides Pydantic models for tool argument validation.
These are used by the ToolRegistry to validate tool calls.
"""

from pydantic import BaseModel, Field


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
