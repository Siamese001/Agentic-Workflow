"""
surgical_context_types - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.types.surgical_context_types.
This module re-exports for relative imports inside ``agentic_core.L5_safety.utils.*``.
"""

from agentic_core.L5_safety.types.surgical_context_types import (  # noqa: F401
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "surgical_context_types_util")
_emit_applies_guardrail("p0", "surgical_context_types_util", "p0_governance")
_emit_snapshots_state("p0", "surgical_context_types_util", "state_snapshot")

__all__ = [
    "ASTCoordinate",
    "SurgicalContext",
    "ViolationConstraint",
]
