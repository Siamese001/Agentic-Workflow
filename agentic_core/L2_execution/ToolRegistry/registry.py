from __future__ import annotations

"""
Tool Registry - Type-Safe FunctionDeclaration Generation for Gemini 2.5/3.0
Automatically generates google.genai.types.FunctionDeclaration from Pydantic models.
"""
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

try:
    from google.genai import types
    GENAI_AVAILABLE: Any = True
except ImportError:
    GENAI_AVAILABLE: Any = False
    types: Any = None
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

# [SSOT IMPORT] Structure blueprint is the single source of truth


class ToolRegistry:
    """
    Registry for managing tools and generating FunctionDeclarations.
    Ensures Gemini always sees the exact tools available in Python.
    """

    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default filesystem and execution tools."""
        self.register_tool(name='read_file', description='Read the contents of a file', args_model=ReadFileArgs, function=read_file)
        self.register_tool(name='write_file', description='Write content to a file with sandbox validation and HealingLease verification', args_model=WriteFileArgs, function=write_file)
        self.register_tool(name='move_file', description='Move or rename a file with sandbox validation', args_model=MoveFileArgs, function=move_file)
        self.register_tool(name='list_files', description='List files in a directory with optional pattern filtering', args_model=ListFilesArgs, function=list_files)
        self.register_tool(name='delete_file', description='Delete a file with sandbox validation and HealingLease verification', args_model=DeleteFileArgs, function=delete_file)
        self.register_tool(name='create_directory', description='Create a directory with sandbox validation', args_model=CreateDirectoryArgs, function=create_directory)
        self.register_tool(name='execute_command', description='Execute a shell command with timeout protection (max 300s)', args_model=ExecuteCommandArgs, function=execute_command)

    def register_tool(self, name: str, description: str, args_model: type[BaseModel], function: Callable) -> Any:
        """
        Register a tool with its Pydantic model and function.

        Args:
            name: Tool name
            description: Tool description
            args_model: Pydantic model for tool arguments
            function: Python function to execute
        """
        self.tools[name] = {'description': description, 'args_model': args_model, 'function': function, 'schema': args_model.schema()}

    def get_function_declarations(self) -> list:
        """
        Generate google.genai.types.FunctionDeclaration for all registered tools.

        Returns:
            List of FunctionDeclaration objects for Gemini
        """
        if not GENAI_AVAILABLE:
            raise ImportError('google-genai not installed. Run: pip install google-genai')
        declarations: Any = []
        for name, tool_info in self.tools.items():
            schema: Any = tool_info['schema']
            parameters: Any = {'type': 'object', 'properties': {}, 'required': []}
            if 'properties' in schema:
                for prop_name, prop_info in schema['properties'].items():
                    param_def: Any = {'type': self._convert_type(prop_info.get('type')), 'description': prop_info.get('description', '')}
                    if 'enum' in prop_info:
                        param_def['enum'] = prop_info['enum']
                    if 'default' in prop_info:
                        param_def['default'] = prop_info['default']
                    if 'items' in prop_info:
                        param_def['items'] = {'type': self._convert_type(prop_info['items'].get('type'))}
                    parameters['properties'][prop_name] = param_def
                if 'required' in schema:
                    parameters['required'] = schema['required']
            declaration: Any = types.FunctionDeclaration(name=name, description=tool_info['description'], parameters=parameters)
            declarations.append(declaration)
        return declarations

    def _convert_type(self, pydantic_type: str | None) -> str:
        """
        Convert Pydantic type to JSON Schema type.

        Args:
            pydantic_type: Pydantic type string

        Returns:
            JSON Schema type string
        """
        if not pydantic_type:
            return 'string'
        type_mapping = {'string': 'string', 'integer': 'integer', 'number': 'number', 'boolean': 'boolean', 'array': 'array', 'object': 'object'}
        return type_mapping.get(pydantic_type, 'string')

    def execute_tool(self, name: str, args: dict[str, Any], **kwargs) -> Any:
        """
        Execute a registered tool with validated arguments.

        Args:
            name: Tool name
            args: Tool arguments as dictionary
            **kwargs: Additional keyword arguments (e.g., blackboard, agent_id)

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
            ValidationError: If arguments are invalid
        """
        if name not in self.tools:
            raise ValueError(f'Tool not found: {name}')
        tool_info: Any = self.tools[name]
        args_model: Any = tool_info['args_model']
        function: Any = tool_info['function']
        validated_args: Any = args_model(**args)
        return function(validated_args, **kwargs)

    def get_tool_names(self) -> list[str]:
        """Get list of registered tool names."""
        return list(self.tools.keys())

    def get_tool_info(self, name: str) -> dict[str, Any] | None:
        """Get information about a specific tool."""
        return self.tools.get(name)
_global_registry: ToolRegistry | None = None

def create_tool_registry() -> ToolRegistry:
    """
    Create or get the global tool registry.

    Returns:
        Global ToolRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry

def get_function_declarations() -> list:
    """
    Get FunctionDeclarations for all registered tools.

    Returns:
        List of FunctionDeclaration objects for Gemini
    """
    registry: Any = create_tool_registry()
    return registry.get_function_declarations()

def execute_tool_call(name: str, args: dict[str, Any], **kwargs) -> Any:
    """
    Execute a tool call from the global registry.

    Args:
        name: Tool name
        args: Tool arguments
        **kwargs: Additional keyword arguments

    Returns:
        Tool execution result
    """
    registry: Any = create_tool_registry()
    return registry.execute_tool(name, args, **kwargs)
