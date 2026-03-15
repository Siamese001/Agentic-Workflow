"""
Telemetry sanitizer - canonical re-export shim.

The implementation lives in agentic_core.L4_state.utils.sanitize_telemetry_util.
This module re-exports for callers using
``from agentic_core.L4_state.utils.telemetry_sanitizer import sanitize_tool_output``.
"""

from agentic_core.L4_state.utils.sanitize_telemetry_util import (  # noqa: F401
    sanitize_tool_output,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "telemetry_sanitizer_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "telemetry_sanitizer_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "telemetry_sanitizer_util")

__all__ = ["sanitize_tool_output"]
