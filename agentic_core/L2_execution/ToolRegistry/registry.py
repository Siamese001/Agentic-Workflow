from __future__ import annotations

"""
Tool Registry - Type-Safe FunctionDeclaration Generation.
[PHASE 16 REFACTOR] Decoupled from google.genai SDK. Returns pure dict schemas.
"""
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from agentic_core.L2_execution.ToolRegistry.definitions import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    ExecuteCommandArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)
from agentic_core.L2_execution.ToolRegistry.execution import execute_command
from agentic_core.L5_safety.validators.filesystem import (
    create_directory,
    delete_file,
    list_files,
    move_file,
    read_file,
    write_file,
)


class ToolRegistry:
    """
    Registry for managing tools and generating schemas.
    """

    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("read_file", ReadFileArgs, read_file, "Read file content")
        self.register("write_file", WriteFileArgs, write_file, "Write content to file")
        self.register("list_files", ListFilesArgs, list_files, "List files in directory")
        self.register("move_file", MoveFileArgs, move_file, "Move or rename file")
        self.register("delete_file", DeleteFileArgs, delete_file, "Delete file")
        self.register("create_directory", CreateDirectoryArgs, create_directory, "Create directory")
        self.register(
            "execute_command", ExecuteCommandArgs, execute_command, "Execute shell command"
        )

    def register(
        self, name: str, args_model: type[BaseModel], function: Callable, description: str
    ) -> None:
        self.tools[name] = {
            "args_model": args_model,
            "function": function,
            "description": description,
        }

    def get_function_declarations(self) -> list[dict[str, Any]]:
        """
        Get schemas for all registered tools.
        Returns list of dicts compatible with Gemini API.
        """
        declarations = []
        for name, tool in self.tools.items():
            schema = tool["args_model"].model_json_schema()
            decl = {
                "name": name,
                "description": tool["description"],
                "parameters": {
                    "type": "OBJECT",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            }
            declarations.append(decl)
        return declarations

    def execute_tool(self, name: str, args: dict[str, Any], **kwargs) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")

        tool_info = self.tools[name]
        args_model = tool_info["args_model"]
        function = tool_info["function"]

        validated_args = args_model(**args)
        return function(validated_args, **kwargs)

    def get_tool_names(self) -> list[str]:
        return list(self.tools.keys())


_global_registry = None


def create_tool_registry() -> ToolRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def get_function_declarations() -> list[dict[str, Any]]:
    return create_tool_registry().get_function_declarations()


def execute_tool_call(name: str, args: dict[str, Any], **kwargs) -> Any:
    return create_tool_registry().execute_tool(name, args, **kwargs)
