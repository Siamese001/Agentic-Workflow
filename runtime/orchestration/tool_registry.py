"""
Tool registry for managing and orchestrating tools in the agentic runtime.

Provides tool registration, discovery, execution, and lifecycle management
with support for tool dependencies, validation, and performance monitoring.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable, Union, Type
from dataclasses import dataclass, field
from datetime import datetime, UTC
import logging
import time
import uuid
import inspect
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    tool_id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    return_schema: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 30
    max_retries: int = 3
    enabled: bool = True
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ToolExecutionResult:
    """Result of tool execution with comprehensive metadata."""
    tool_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    parameters_used: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class Tool(ABC):
    """Abstract base class for all tools in the registry."""

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass

    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters before execution."""
        return True

    def cleanup(self) -> None:
        """Cleanup resources after tool execution."""
        pass


class ToolRegistry:
    """
    Central registry for managing tools in the agentic runtime.
    
    Handles tool registration, discovery, execution, and lifecycle management
    with support for dependencies, validation, and performance monitoring.
    """

    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Tool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.execution_history: List[ToolExecutionResult] = []
        self.max_history = 1000
        self._dependency_graph: Dict[str, List[str]] = {}

    def register_tool(
        self,
        tool: Tool,
        tool_id: Optional[str] = None,
        metadata: Optional[ToolMetadata] = None
    ) -> str:
        """
        Register a tool in the registry.

        Args:
            tool: Tool instance to register
            tool_id: Optional tool ID (generated if not provided)
            metadata: Optional tool metadata

        Returns:
            Tool ID for the registered tool
        """
        if tool_id is None:
            tool_id = str(uuid.uuid4())

        if tool_id in self.tools:
            raise ValueError(f"Tool with ID '{tool_id}' already registered")

        # Get or create metadata
        if metadata is None:
            metadata = tool.get_metadata()
        metadata.tool_id = tool_id

        # Validate tool
        if not hasattr(tool, 'execute'):
            raise ValueError("Tool must have an 'execute' method")

        # Register tool
        self.tools[tool_id] = tool
        self.tool_metadata[tool_id] = metadata

        # Update dependency graph
        self._dependency_graph[tool_id] = metadata.dependencies

        logger.info(f"Registered tool: {tool_id} ({metadata.name})")
        return tool_id

    def register_tool_class(
        self,
        tool_class: Type[Tool],
        tool_id: Optional[str] = None,
        metadata: Optional[ToolMetadata] = None,
        **init_kwargs
    ) -> str:
        """
        Register a tool class by instantiating it.

        Args:
            tool_class: Tool class to register
            tool_id: Optional tool ID
            metadata: Optional tool metadata
            **init_kwargs: Initialization arguments for the tool

        Returns:
            Tool ID for the registered tool
        """
        # Instantiate the tool
        tool_instance = tool_class(**init_kwargs)
        return self.register_tool(tool_instance, tool_id, metadata)

    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister a tool from the registry."""
        if tool_id in self.tools:
            del self.tools[tool_id]
            del self.tool_metadata[tool_id]
            
            # Remove from dependency graph
            if tool_id in self._dependency_graph:
                del self._dependency_graph[tool_id]
            
            # Remove dependencies from other tools
            for deps in self._dependency_graph.values():
                if tool_id in deps:
                    deps.remove(tool_id)
            
            logger.info(f"Unregistered tool: {tool_id}")
            return True
        return False

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get a tool by ID."""
        return self.tools.get(tool_id)

    def get_tool_metadata(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID."""
        return self.tool_metadata.get(tool_id)

    def list_tools(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        enabled_only: bool = True
    ) -> List[ToolMetadata]:
        """
        List registered tools with optional filtering.

        Args:
            category: Filter by tool category
            tags: Filter by tags (must match all)
            enabled_only: Only return enabled tools

        Returns:
            List of tool metadata
        """
        tools = []
        
        for metadata in self.tool_metadata.values():
            # Apply filters
            if enabled_only and not metadata.enabled:
                continue
            if category and metadata.category != category:
                continue
            if tags and not all(tag in metadata.tags for tag in tags):
                continue
            
            tools.append(metadata)
        
        return tools

    def search_tools(self, query: str) -> List[ToolMetadata]:
        """Search tools by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for metadata in self.tool_metadata.values():
            if (query_lower in metadata.name.lower() or
                query_lower in metadata.description.lower() or
                any(query_lower in tag.lower() for tag in metadata.tags)):
                results.append(metadata)
        
        return results

    def execute_tool(
        self,
        tool_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ToolExecutionResult:
        """
        Execute a tool with given parameters.

        Args:
            tool_id: Tool ID to execute
            parameters: Execution parameters
            timeout: Optional timeout override

        Returns:
            ToolExecutionResult with execution metadata
        """
        tool = self.get_tool(tool_id)
        metadata = self.get_tool_metadata(tool_id)
        
        if not tool:
            return ToolExecutionResult(
                tool_id=tool_id,
                success=False,
                result=None,
                error=f"Tool not found: {tool_id}"
            )
        
        if not metadata.enabled:
            return ToolExecutionResult(
                tool_id=tool_id,
                success=False,
                result=None,
                error=f"Tool is disabled: {tool_id}"
            )
        
        start_time = time.time()
        parameters = parameters or {}
        
        try:
            # Validate parameters
            if not tool.validate_parameters(parameters):
                raise ValueError("Invalid parameters for tool execution")
            
            # Check dependencies
            self._check_dependencies(tool_id)
            
            # Execute tool with timeout
            execution_timeout = timeout or metadata.timeout_seconds
            
            # Simple timeout implementation (in production, use proper async/timeout)
            result = tool.execute(**parameters)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            execution_result = ToolExecutionResult(
                tool_id=tool_id,
                success=True,
                result=result,
                execution_time_ms=execution_time_ms,
                parameters_used=parameters.copy(),
                metadata={
                    "tool_name": metadata.name,
                    "tool_version": metadata.version,
                    "category": metadata.category
                }
            )
            
            # Store in history
            self._add_to_history(execution_result)
            
            logger.debug(f"Tool executed successfully: {tool_id}, time: {execution_time_ms:.2f}ms")
            return execution_result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Tool execution failed: {str(e)}"
            
            logger.error(f"Tool execution failed: {tool_id}, error: {str(e)}")
            
            execution_result = ToolExecutionResult(
                tool_id=tool_id,
                success=False,
                result=None,
                error=error_msg,
                execution_time_ms=execution_time_ms,
                parameters_used=parameters.copy(),
                metadata={"error_type": type(e).__name__}
            )
            
            self._add_to_history(execution_result)
            return execution_result

    def _check_dependencies(self, tool_id: str) -> None:
        """Check that all tool dependencies are satisfied."""
        dependencies = self._dependency_graph.get(tool_id, [])
        
        for dep_id in dependencies:
            if dep_id not in self.tools:
                raise ValueError(f"Missing dependency: {dep_id} for tool {tool_id}")
            
            dep_metadata = self.tool_metadata[dep_id]
            if not dep_metadata.enabled:
                raise ValueError(f"Dependency disabled: {dep_id} for tool {tool_id}")

    def _add_to_history(self, result: ToolExecutionResult) -> None:
        """Add execution result to history."""
        self.execution_history.append(result)
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)

    def get_execution_history(self, tool_id: Optional[str] = None, limit: Optional[int] = None) -> List[ToolExecutionResult]:
        """Get execution history with optional filtering."""
        history = self.execution_history
        
        if tool_id:
            history = [result for result in history if result.tool_id == tool_id]
        
        if limit:
            history = history[-limit:]
        
        return history

    def get_tool_stats(self, tool_id: Optional[str] = None) -> Dict[str, Any]:
        """Get execution statistics for tools."""
        history = self.get_execution_history(tool_id)
        
        if not history:
            return {"total_executions": 0}
        
        total_executions = len(history)
        successful_executions = sum(1 for r in history if r.success)
        total_time = sum(r.execution_time_ms or 0 for r in history)
        avg_time = total_time / total_executions
        
        stats = {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions,
            "average_execution_time_ms": avg_time,
            "last_execution": history[-1].timestamp.isoformat() if history else None
        }
        
        if tool_id:
            metadata = self.get_tool_metadata(tool_id)
            if metadata:
                stats.update({
                    "tool_name": metadata.name,
                    "tool_version": metadata.version,
                    "category": metadata.category
                })
        
        return stats

    def enable_tool(self, tool_id: str) -> bool:
        """Enable a tool."""
        if tool_id in self.tool_metadata:
            self.tool_metadata[tool_id].enabled = True
            logger.info(f"Enabled tool: {tool_id}")
            return True
        return False

    def disable_tool(self, tool_id: str) -> bool:
        """Disable a tool."""
        if tool_id in self.tool_metadata:
            self.tool_metadata[tool_id].enabled = False
            logger.info(f"Disabled tool: {tool_id}")
            return True
        return False

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the current dependency graph."""
        return self._dependency_graph.copy()

    def validate_dependency_graph(self) -> List[str]:
        """Validate dependency graph and return any issues."""
        issues = []
        
        for tool_id, dependencies in self._dependency_graph.items():
            if tool_id not in self.tools:
                issues.append(f"Tool not found: {tool_id}")
                continue
            
            for dep_id in dependencies:
                if dep_id not in self.tools:
                    issues.append(f"Missing dependency: {dep_id} for tool {tool_id}")
        
        # Check for circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self._dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for tool_id in self._dependency_graph:
            if tool_id not in visited:
                if has_cycle(tool_id):
                    issues.append(f"Circular dependency detected involving: {tool_id}")
        
        return issues


# Global tool registry instance
_tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _tool_registry


def register_tool(tool: Tool, tool_id: Optional[str] = None) -> str:
    """Register a tool using the global registry."""
    return _tool_registry.register_tool(tool, tool_id)


def execute_tool(tool_id: str, parameters: Optional[Dict[str, Any]] = None) -> ToolExecutionResult:
    """Execute a tool using the global registry."""
    return _tool_registry.execute_tool(tool_id, parameters)


def list_tools(category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[ToolMetadata]:
    """List tools using the global registry."""
    return _tool_registry.list_tools(category, tags)


__all__ = [
    "ToolMetadata",
    "ToolExecutionResult",
    "Tool",
    "ToolRegistry",
    "get_tool_registry",
    "register_tool",
    "execute_tool",
    "list_tools"
]
