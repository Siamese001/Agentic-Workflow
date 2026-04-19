"""Compatibility shim for execution-trace contract authority.

Selected authority is `agentic_core.runtime.types.execution_trace`.
This module remains as an import-stable facade and re-exports authority APIs.
"""

from agentic_core.runtime.types.execution_trace import (  # noqa: F401
    ExecutionTrace,
    ExecutionTraceManager,
    bind_determinism_to_trace,
    get_active_execution_trace,
    get_execution_trace_manager,
    start_execution_trace,
)

__all__ = [
    "ExecutionTrace",
    "ExecutionTraceManager",
    "start_execution_trace",
    "bind_determinism_to_trace",
    "get_active_execution_trace",
    "get_execution_trace_manager",
]
