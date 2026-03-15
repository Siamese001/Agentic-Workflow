"""
definitions - canonical re-export shim.

The implementation lives in agentic_core.L2_execution.types.tool_args_types.
This module re-exports for callers using
``from agentic_core.L2_execution.reasoning.definitions import ReadFileArgs, ...``.
"""

from agentic_core.L2_execution.types.tool_args_types import (  # noqa: F401
    CreateDirectoryArgs,
    DeleteFileArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "definitions", "L2")
_emit_routes_through("p1", "definitions", "L2")
_emit_escalates_to_human("p1", "definitions", "L2")
_emit_reads_policy_state("p1", "definitions", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "definitions")
_emit_applies_guardrail("p0", "definitions", "p0_governance")
_emit_snapshots_state("p0", "definitions", "state_snapshot")

__all__ = [
    "CreateDirectoryArgs",
    "DeleteFileArgs",
    "ListFilesArgs",
    "MoveFileArgs",
    "ReadFileArgs",
    "WriteFileArgs",
]
