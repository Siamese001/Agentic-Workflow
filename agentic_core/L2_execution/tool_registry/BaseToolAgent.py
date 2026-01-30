"""
Base classes for L2 Execution tool_registry.

Provides foundational classes for tool registration and execution.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseTool:
    """Base class for all tools in the registry."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._enabled = True

    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")

    def is_enabled(self) -> bool:
        """Check if tool is enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable the tool."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the tool."""
        self._enabled = False


class tool_registry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")

    def get(self, name: str) -> BaseTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def execute(self, name: str, *args, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")
        if not tool.is_enabled():
            raise ValueError(f"Tool is disabled: {name}")
        return tool.execute(*args, **kwargs)


class SubAtomicAgent:
    """Base class for subatomic agents."""

    def __init__(self, name: str = "SubAtomicAgent"):
        self.name = name

    def execute(self, *args, **kwargs):
        raise NotImplementedError()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by SubAtomicAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        file_path = violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        # Default implementation - SubAtomicAgent manages sub-atomic operations
        try:
            return {
                "status": "skipped",
                "details": f"SubAtomicAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"SubAtomicAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


class BaseAgent:
    """Base class for agents using the tool registry."""

    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.registry = tool_registry()

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool with this agent."""
        self.registry.register(tool)

    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Execute a registered tool."""
        return self.registry.execute(name, *args, **kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by BaseAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        file_path = violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        # Default implementation - BaseAgent manages tool registry
        try:
            return {
                "status": "skipped",
                "details": f"BaseAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"BaseAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


# Aliases for backwards compatibility
Tool = BaseTool
Registry = tool_registry

__all__ = ["BaseTool", "tool_registry", "BaseAgent", "SubAtomicAgent", "Tool", "Registry"]
