"""
Telemetry sanitizer - canonical re-export shim.

The implementation lives in agentic_core.L4_state.utils.sanitize_telemetry_util.
This module re-exports for callers using
``from agentic_core.L4_state.utils.telemetry_sanitizer import sanitize_tool_output``.
"""

from agentic_core.L4_state.utils.sanitize_telemetry_util import (  # noqa: F401
    sanitize_tool_output,
)

__all__ = ["sanitize_tool_output"]
