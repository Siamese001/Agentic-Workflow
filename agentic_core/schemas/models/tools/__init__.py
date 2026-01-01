"""
Tool Argument Contracts - SSOT for all tool parameter schemas.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class read_file_args(BaseModel):
    """Arguments for reading a file."""
    path: str = Field(..., description="Relative path to the file to read")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

# Backward compat alias
ReadFileArgs = read_file_args


class write_file_args(BaseModel):
    """Arguments for writing to a file."""
    path: str = Field(..., description="Relative path to the file to write")
    content: str = Field(..., description="Content to write to the file")
    create_dirs: bool = Field(default=True, description="Create parent directories if they don't exist")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

# Backward compat alias
WriteFileArgs = write_file_args


class move_file_args(BaseModel):
    """Arguments for moving/renaming a file."""
    source: str = Field(..., description="Relative path to the source file")
    destination: str = Field(..., description="Relative path to the destination")
    overwrite: bool = Field(default=False, description="Overwrite destination if it exists")
    
    @validator('source', 'destination')
    def validate_paths(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Paths must be relative to project root")
        return v

# Backward compat alias
MoveFileArgs = move_file_args


class list_files_args(BaseModel):
    """Arguments for listing files in a directory."""
    path: str = Field(default=".", description="Relative path to the directory to list")
    pattern: Optional[str] = Field(default=None, description="Glob pattern to filter files (e.g., '*.py')")
    recursive: bool = Field(default=False, description="Recursively list subdirectories")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

# Backward compat alias
ListFilesArgs = list_files_args


class execute_command_args(BaseModel):
    """Arguments for executing a shell command."""
    command: str = Field(..., description="Command to execute")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    cwd: Optional[str] = Field(default=None, description="Working directory (relative to project root)")
    timeout: int = Field(default=30, description="Timeout in seconds (max 300)")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds to prevent livelocks")
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v
    
    @validator('cwd')
    def validate_cwd(cls, v):
        if v and Path(v).is_absolute():
            raise ValueError("Working directory must be relative to project root")
        return v

# Backward compat alias
ExecuteCommandArgs = execute_command_args


class delete_file_args(BaseModel):
    """Arguments for deleting a file."""
    path: str = Field(..., description="Relative path to the file to delete")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

# Backward compat alias
DeleteFileArgs = delete_file_args


class create_directory_args(BaseModel):
    """Arguments for creating a directory."""
    path: str = Field(..., description="Relative path to the directory to create")
    parents: bool = Field(default=True, description="Create parent directories if needed")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

# Backward compat alias
CreateDirectoryArgs = create_directory_args


# Public exports
__all__ = [
    # Snake case (canonical)
    "read_file_args",
    "write_file_args",
    "move_file_args",
    "list_files_args",
    "execute_command_args",
    "delete_file_args",
    "create_directory_args",
    # PascalCase aliases (backward compat)
    "ReadFileArgs",
    "WriteFileArgs",
    "MoveFileArgs",
    "ListFilesArgs",
    "ExecuteCommandArgs",
    "DeleteFileArgs",
    "CreateDirectoryArgs",
]
