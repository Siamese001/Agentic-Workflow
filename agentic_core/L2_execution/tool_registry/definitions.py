"""
Tool Argument Definitions - Pydantic Models for Type-Safe Tool Calls
Fixes "23 validation errors" and "Extra inputs" crashes with Gemini 2.5/3.0.

Models migrated to SSOT: AgenticCore/schemas/models/core_contracts.py
"""
from AgenticCore.schemas.models.core_contracts import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    ExecuteCommandArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)
