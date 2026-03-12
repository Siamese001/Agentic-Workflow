"""
Tools module for L2 Execution tool_registry.

Provides common tool implementations.
"""
from typing import Any
from .base import tool_registry
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = ['tool_registry', 'FunctionTool']

class FunctionTool(BaseTool):
    """A tool that wraps a callable function."""

    def __init__(self, name: str, func: callable, description: str=''):
        super().__init__(name, description)
        self._func = func

    def execute(self, *args, **kwargs) -> Any:
        """Execute the wrapped function."""
        return self._func(*args, **kwargs)
