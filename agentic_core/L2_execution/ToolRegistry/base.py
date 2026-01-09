"""
Base classes for L2 Execution ToolRegistry.

Provides foundational classes for tool registration and execution.
"""
from typing import Any, Dict, List, Optional, Callable
import logging

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


class ToolRegistry:
    """Registry for managing tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")
    
    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
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


class BaseAgent:
    """Base class for agents using the tool registry."""
    
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.registry = ToolRegistry()
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool with this agent."""
        self.registry.register(tool)
    
    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Execute a registered tool."""
        return self.registry.execute(name, *args, **kwargs)


# Aliases for backwards compatibility
Tool = BaseTool
Registry = ToolRegistry

__all__ = ['BaseTool', 'ToolRegistry', 'BaseAgent', 'SubAtomicAgent', 'Tool', 'Registry']
