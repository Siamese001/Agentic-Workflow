"""
Tool Invocation Engine Implementation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ToolInvocation:
    """Engine for invoking and managing tool execution"""
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.available_tools = {}
    
    def register_tool(self, name: str, tool_instance):
        """Register a tool for execution"""
        self.available_tools[name] = tool_instance
    
    def invoke_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Invoke a tool with given parameters"""
        start_time = datetime.now()
        
        if tool_name not in self.available_tools:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' not found",
                execution_time=0.0,
                timestamp=start_time
            )
        
        try:
            tool = self.available_tools[tool_name]
            result_data = tool(**kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = ToolResult(
                success=True,
                data=result_data,
                execution_time=execution_time,
                timestamp=start_time
            )
            
            self.execution_history.append({
                "tool_name": tool_name,
                "parameters": kwargs,
                "result": result,
                "timestamp": start_time
            })
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                timestamp=start_time
            )
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of tool executions"""
        return self.execution_history.copy()
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()
