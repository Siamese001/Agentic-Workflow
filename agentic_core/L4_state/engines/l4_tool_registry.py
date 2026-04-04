"""Dynamic Tool Registry for L4 Agentic Actions

Implements spec-compliant L4 Agentic Actions with:
- Dynamic tool registration
- Schema validation at runtime
- Tool discovery and listing
- Execution routing

Replaces hardcoded 3-tool limitation with extensible registry.
"""

from __future__ import annotations

import importlib
import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_validates_capability,
)

Logger = logging.getLogger(__name__)


@dataclass
class ToolSchema:
    """Schema definition for L4 Agentic Action tool."""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema format
    required: list[str]
    returns: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolInstance:
    """Registered tool instance with schema and handler."""
    schema: ToolSchema
    handler: Callable[..., Any]
    source_module: str
    registration_time: float


class ToolRegistry:
    """Dynamic registry for L4 Agentic Action tools.

    Provides:
    - Runtime tool registration
    - Schema validation
    - Tool discovery
    - Execution dispatch
    """

    def __init__(self):
        self._tools: dict[str, ToolInstance] = {}
        self._invocation_count = 0
        self._validation_failures = 0

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Any],
        description: str,
        parameters: dict[str, Any],
        required: list[str] | None = None,
        returns: dict[str, Any] | None = None,
        source_module: str = "unknown",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Register a new tool in the registry.

        Args:
            name: Tool name (must be unique)
            handler: Callable function/method
            description: Human-readable description
            parameters: JSON Schema for parameters
            required: List of required parameter names
            returns: JSON Schema for return value
            source_module: Module where tool is defined
            metadata: Additional tool metadata

        Returns:
            True if registration successful
        """
        _trace_id = f"register_{name}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ToolRegistry.register_tool")

        if name in self._tools:
            Logger.warning(f"Tool '{name}' already registered, overwriting")

        schema = ToolSchema(
            name=name,
            description=description,
            parameters=parameters,
            required=required or [],
            returns=returns or {"type": "object"},
            metadata=metadata or {},
        )

        import time
        tool_instance = ToolInstance(
            schema=schema,
            handler=handler,
            source_module=source_module,
            registration_time=time.time(),
        )

        self._tools[name] = tool_instance
        Logger.info(f"Registered tool: {name} from {source_module}")

        return True

    def unregister_tool(self, name: str) -> bool:
        """Remove a tool from the registry.

        Args:
            name: Tool name to remove

        Returns:
            True if tool was removed
        """
        if name in self._tools:
            del self._tools[name]
            Logger.info(f"Unregistered tool: {name}")
            return True
        return False

    def get_tool(self, name: str) -> ToolInstance | None:
        """Get tool instance by name.

        Args:
            name: Tool name

        Returns:
            ToolInstance if found, None otherwise
        """
        return self._tools.get(name)

    def get_tool_schema(self, name: str) -> ToolSchema | None:
        """Get schema for a tool.

        Args:
            name: Tool name

        Returns:
            ToolSchema if found, None otherwise
        """
        tool = self._tools.get(name)
        return tool.schema if tool else None

    def list_tools(self) -> list[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def list_tools_with_schemas(self) -> dict[str, ToolSchema]:
        """List all tools with their schemas.

        Returns:
            Dict mapping tool names to schemas
        """
        return {name: tool.schema for name, tool in self._tools.items()}

    def validate_parameters(self, tool_name: str, parameters: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters against tool schema.

        Args:
            tool_name: Name of tool
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        tool = self._tools.get(tool_name)
        if not tool:
            return False, [f"Tool '{tool_name}' not found"]

        schema = tool.schema
        errors = []

        # Check required parameters
        for req in schema.required:
            if req not in parameters:
                errors.append(f"Missing required parameter: {req}")

        # Validate parameter types (basic)
        for param_name, param_value in parameters.items():
            if param_name in schema.parameters:
                expected_type = schema.parameters[param_name].get("type")
                if expected_type:
                    type_valid = self._check_type(param_value, expected_type)
                    if not type_valid:
                        errors.append(
                            f"Parameter '{param_name}' has wrong type. "
                            f"Expected {expected_type}, got {type(param_value).__name__}"
                        )

        _emit_validates_capability(
            f"validate_{tool_name}", "ToolRegistry", f"valid_{not errors}"
        )

        return len(errors) == 0, errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON Schema type.

        Args:
            value: Value to check
            expected_type: JSON Schema type string

        Returns:
            True if types match
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, allow

        return isinstance(value, expected)

    def execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool with given parameters.

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters

        Returns:
            Execution result dict
        """
        _trace_id = f"exec_{tool_name}_{self._invocation_count}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ToolRegistry.execute_tool")

        # Validate
        is_valid, errors = self.validate_parameters(tool_name, parameters)
        if not is_valid:
            self._validation_failures += 1
            return {
                "success": False,
                "error": f"Parameter validation failed: {', '.join(errors)}",
                "tool": tool_name,
            }

        tool = self._tools.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "tool": tool_name,
            }

        # Execute
        try:
            _emit_records_tool_invocation(_trace_id, tool_name, str(parameters))

            result = tool.handler(**parameters)

            self._invocation_count += 1

            return {
                "success": True,
                "result": result,
                "tool": tool_name,
                "trace_id": _trace_id,
            }

        except Exception as e:
            Logger.error(f"Tool execution failed: {tool_name} - {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "trace_id": _trace_id,
            }

    def auto_discover_tools(self, module_path: str) -> list[str]:
        """Auto-discover tools in a module.

        Looks for functions with @tool decorator or tool_ prefix.

        Args:
            module_path: Python module path (e.g., 'my_package.tools')

        Returns:
            List of discovered tool names
        """
        discovered = []

        try:
            module = importlib.import_module(module_path)

            for name, obj in inspect.getmembers(module):
                # Check for @tool decorator (has _tool_schema attribute)
                if inspect.isfunction(obj) and hasattr(obj, "_tool_schema"):
                    schema = obj._tool_schema
                    self.register_tool(
                        name=schema.get("name", name),
                        handler=obj,
                        description=schema.get("description", ""),
                        parameters=schema.get("parameters", {}),
                        required=schema.get("required", []),
                        returns=schema.get("returns", {}),
                        source_module=module_path,
                    )
                    discovered.append(name)

                # Check for tool_ prefix
                elif name.startswith("tool_") and inspect.isfunction(obj):
                    tool_name = name[5:]  # Remove 'tool_' prefix

                    # Extract docstring as description
                    description = inspect.getdoc(obj) or f"Tool {tool_name}"

                    # Extract parameters from signature
                    sig = inspect.signature(obj)
                    parameters = {}
                    required = []

                    for param_name, param in sig.parameters.items():
                        param_type = "string"  # Default
                        if param.annotation != inspect.Parameter.empty:
                            if param.annotation == str:
                                param_type = "string"
                            elif param.annotation == int:
                                param_type = "integer"
                            elif param.annotation == float:
                                param_type = "number"
                            elif param.annotation == bool:
                                param_type = "boolean"

                        parameters[param_name] = {
                            "type": param_type,
                            "description": f"Parameter {param_name}",
                        }

                        if param.default == inspect.Parameter.empty:
                            required.append(param_name)

                    self.register_tool(
                        name=tool_name,
                        handler=obj,
                        description=description,
                        parameters=parameters,
                        required=required,
                        source_module=module_path,
                    )
                    discovered.append(tool_name)

            Logger.info(f"Auto-discovered {len(discovered)} tools in {module_path}")

        except Exception as e:
            Logger.error(f"Failed to auto-discover tools in {module_path}: {e}")

        return discovered

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        return {
            "registered_tools": len(self._tools),
            "invocation_count": self._invocation_count,
            "validation_failures": self._validation_failures,
            "success_rate": (
                (self._invocation_count - self._validation_failures) / self._invocation_count
                if self._invocation_count > 0 else 1.0
            ),
        }


def tool_decorator(
    name: str | None = None,
    description: str | None = None,
    parameters: dict[str, Any] | None = None,
    required: list[str] | None = None,
    returns: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to mark a function as an L4 Agentic Action tool.

    Usage:
        @tool_decorator(
            name="search_docs",
            description="Search documentation",
            parameters={"query": {"type": "string"}},
            required=["query"],
        )
        def search_docs(query: str) -> dict:
            ...

    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to docstring)
        parameters: JSON Schema for parameters
        required: List of required parameter names
        returns: JSON Schema for return value

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func_name = name or func.__name__
        func_description = description or inspect.getdoc(func) or f"Tool {func_name}"

        # Auto-extract parameters if not provided
        if parameters is None:
            sig = inspect.signature(func)
            auto_params = {}
            auto_required = []

            for param_name, param in sig.parameters.items():
                param_type = "string"
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == str:
                        param_type = "string"
                    elif param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"

                auto_params[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}",
                }

                if param.default == inspect.Parameter.empty:
                    auto_required.append(param_name)

            func_params = auto_params
            func_required = required or auto_required
        else:
            func_params = parameters
            func_required = required or []

        func._tool_schema = {
            "name": func_name,
            "description": func_description,
            "parameters": func_params,
            "required": func_required,
            "returns": returns or {"type": "object"},
        }

        return func

    return decorator


# Global registry
_global_tool_registry: ToolRegistry | None = None


def get_global_tool_registry() -> ToolRegistry:
    """Get or create global tool registry."""
    global _global_tool_registry
    if _global_tool_registry is None:
        _global_tool_registry = ToolRegistry()
        _register_default_tools(_global_tool_registry)
    return _global_tool_registry


def _register_default_tools(registry: ToolRegistry) -> None:
    """Register default tools for L4 Agentic Actions."""

    # 1. search_docs
    def search_docs(query: str, n_results: int = 5) -> dict[str, Any]:
        """Search documentation for relevant information."""
        from agentic_core.L4_state.engines.retrieval_layers import L3SemanticRAG

        l3 = L3SemanticRAG()
        results = l3.query_docs(query, n_results)

        return {
            "query": query,
            "results": results,
            "count": len(results),
        }

    registry.register_tool(
        name="search_docs",
        handler=search_docs,
        description="Search documentation for relevant information",
        parameters={
            "query": {"type": "string", "description": "Search query"},
            "n_results": {"type": "integer", "description": "Number of results", "default": 5},
        },
        required=["query"],
        source_module="agentic_core.L4_state.engines.tool_registry",
    )

    # 2. find_similar_traces
    def find_similar_traces(trace_id: str, n_results: int = 5) -> dict[str, Any]:
        """Find similar execution traces."""
        from agentic_core.L4_state.engines.retrieval_layers import L3SemanticRAG

        l3 = L3SemanticRAG()
        # Use trace_id as query to find similar
        results = l3.query_traces(trace_id, n_results)

        return {
            "trace_id": trace_id,
            "results": results,
            "count": len(results),
        }

    registry.register_tool(
        name="find_similar_traces",
        handler=find_similar_traces,
        description="Find similar execution traces",
        parameters={
            "trace_id": {"type": "string", "description": "Reference trace ID"},
            "n_results": {"type": "integer", "description": "Number of similar traces", "default": 5},
        },
        required=["trace_id"],
        source_module="agentic_core.L4_state.engines.tool_registry",
    )

    # 3. get_architecture_info
    def get_architecture_info(component: str) -> dict[str, Any]:
        """Get architecture documentation for a component."""
        valid_components = ["ADG", "L0", "L1", "L2", "L3", "L4", "L5", "L6"]

        if component.upper() not in valid_components:
            return {
                "error": f"Unknown component: {component}. Valid: {valid_components}",
            }

        # Query architecture docs
        query = f"{component} architecture design pattern"

        from agentic_core.L4_state.engines.retrieval_layers import L3SemanticRAG
        l3 = L3SemanticRAG()
        results = l3.query_docs(query, 3)

        return {
            "component": component,
            "documentation": results,
            "count": len(results),
        }

    registry.register_tool(
        name="get_architecture_info",
        handler=get_architecture_info,
        description="Get architecture documentation for a component",
        parameters={
            "component": {"type": "string", "description": "Component name (ADG, L0-L6)"},
        },
        required=["component"],
        source_module="agentic_core.L4_state.engines.tool_registry",
    )

    Logger.info("Registered 3 default tools in ToolRegistry")


# Convenience functions
def register_tool(
    name: str,
    handler: Callable[..., Any],
    description: str,
    parameters: dict[str, Any],
    required: list[str] | None = None,
) -> bool:
    """Register a tool in the global registry."""
    return get_global_tool_registry().register_tool(
        name=name,
        handler=handler,
        description=description,
        parameters=parameters,
        required=required,
    )


def execute_tool(tool_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool from the global registry."""
    return get_global_tool_registry().execute_tool(tool_name, parameters)


def list_tools() -> list[str]:
    """List all registered tools."""
    return get_global_tool_registry().list_tools()
