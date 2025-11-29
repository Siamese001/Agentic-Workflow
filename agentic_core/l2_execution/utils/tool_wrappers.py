#!/usr/bin/env python3
"""
Tool Wrappers
Section 5: Tool Contracts - Wrapper classes for external tool integrations
"""

from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class ToolWrapper:
    """Base wrapper class for external tool integrations"""
    
    def __init__(self, tool_name: str, tool_config: Optional[Dict[str, Any]] = None):
        self.tool_name = tool_name
        self.tool_config = tool_config or {}
        self.is_available = True
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the wrapped tool with input data"""
        if not self.is_available:
            return {"error": f"Tool {self.tool_name} is not available"}
        
        try:
            result = self._execute_tool(input_data)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_tool(self, input_data: Dict[str, Any]) -> Any:
        """Override in subclasses to implement specific tool logic"""
        return f"Tool {self.tool_name} executed with: {input_data}"
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the tool"""
        return True
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the tool wrapper"""
        self.tool_config.update(config)

class PythonToolWrapper(ToolWrapper):
    """Wrapper for Python-based tools"""
    
    def __init__(self, tool_name: str, tool_function: Callable, tool_config: Optional[Dict[str, Any]] = None):
        super().__init__(tool_name, tool_config)
        self.tool_function = tool_function
    
    def _execute_tool(self, input_data: Dict[str, Any]) -> Any:
        """Execute Python function"""
        return self.tool_function(input_data)

class ExternalAPIToolWrapper(ToolWrapper):
    """Wrapper for external API tools"""
    
    def __init__(self, tool_name: str, api_endpoint: str, tool_config: Optional[Dict[str, Any]] = None):
        super().__init__(tool_name, tool_config)
        self.api_endpoint = api_endpoint
    
    def _execute_tool(self, input_data: Dict[str, Any]) -> Any:
        """Execute external API call (simplified implementation)"""
        return f"API call to {self.api_endpoint} with data: {input_data}"

# Re-export components
__all__ = [
    'ToolWrapper', 'PythonToolWrapper', 'ExternalAPIToolWrapper'
]
