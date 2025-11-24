"""
L2 - Pure Execution and Tools Layer

This layer contains only tool execution logic with no reasoning or state management.
No planning, orchestration, or state writes are allowed here.
"""
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from dataclasses import dataclass

@runtime_checkable
class Tool(Protocol):
    """Protocol that all L2 tools must implement."""
    
    @property
    def name(self) -> str:
        """Unique name of the tool."""
        ...
        
    @property
    def description(self) -> str:
        """Description of what the tool does."""
        ...
        
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with the given arguments."""
        ...

@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class ToolExecutor:
    """Executes tools in a sandboxed environment."""
    
    def __init__(self, tools: List[Tool]):
        self.tools = {tool.name: tool for tool in tools}
    
    def execute(self, tool_name: str, **kwargs: Any) -> ToolResult:
        """Execute a tool by name with the given arguments."""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool '{tool_name}' not found"
            )
            
        try:
            result = self.tools[tool_name].execute(**kwargs)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )

# Re-export public interfaces
__all__ = [
    'Tool',
    'ToolResult',
    'ToolExecutor',
]
