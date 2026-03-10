"""
Telemetry sanitizer - canonical re-export shim.

The implementation lives in agentic_core.L4_state.utils.sanitize_telemetry_util.
This module re-exports for callers using
``from agentic_core.L4_state.utils.telemetry_sanitizer import sanitize_tool_output``.
"""

from agentic_core.L4_state.utils.sanitize_telemetry_util import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    sanitize_tool_output,
)

__all__ = ["sanitize_tool_output"]
