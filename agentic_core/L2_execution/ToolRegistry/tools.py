"""
Tools module for L2 Execution ToolRegistry.

Provides common tool implementations.
"""
from typing import Any, Dict, List, Optional
from .base import BaseTool, ToolRegistry

__all__ = ['BaseTool', 'ToolRegistry', 'FunctionTool']


class FunctionTool(BaseTool):
    """A tool that wraps a callable function."""
    
    def __init__(self, name: str, func: callable, description: str = ""):
        super().__init__(name, description)
        self._func = func
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the wrapped function."""
        return self._func(*args, **kwargs)
