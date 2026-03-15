"""
Tools module for L2 Execution tool_registry.

Provides common tool implementations.
"""

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

from .base import tool_registry

_emit_records_execution_trace("p0", "evidence", "function_tool")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "function_tool", "p0_governance")
_emit_snapshots_state("p0", "function_tool", "state_snapshot")

__all__ = ["tool_registry", "FunctionTool"]


class FunctionTool(BaseTool):
    """A tool that wraps a callable function."""

    def __init__(self, name: str, func: callable, description: str = ""):
        super().__init__(name, description)
        self._func = func

    def execute(self, *args, **kwargs) -> Any:
        """Execute the wrapped function."""
        return self._func(*args, **kwargs)
