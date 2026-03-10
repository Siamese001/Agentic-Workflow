"""
Base classes for L2 Execution tool_registry.

Provides foundational classes for tool registration and execution.
"""

import logging
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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


# REMOVED: SubAtomicAgent duplicate class
# Use SubAtomicAgent from agentic_core.L3_orchestration.reasoning instead


# REMOVED: BaseAgent duplicate class
# Use SovereignBaseAgent from agentic_core.base_agents instead


# Aliases for backwards compatibility
Tool = BaseTool
Registry = tool_registry

__all__ = ["BaseTool", "tool_registry", "Tool", "Registry"]
