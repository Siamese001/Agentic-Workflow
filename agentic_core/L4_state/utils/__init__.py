"""
L4 State Layer - Shared Utilities

SSOT for common functionality used across L5 agents:
- complexity_analyzer: McCabe cyclomatic complexity calculation
- layer_gravity: Layer hierarchy and gravity rule enforcement
- context_manager: Centralized state management for cross-agent learning

These utilities were extracted from L5 agents to eliminate code duplication.

Note: Use direct imports to avoid circular dependencies:
    from agentic_core.L4_state.utils.layer_gravity_util import is_gravity_violation
"""

from agentic_core.L4_state.utils.complexity_analyzer_util import (
    calculate_mccabe_complexity,
    check_function_complexity,
)
from agentic_core.L4_state.utils.layer_gravity_util import (
    GRAVITY_RULES,
    LAYER_ORDER,
    extract_layer_from_module,
    extract_layer_from_path,
    is_gravity_violation,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

try:
    from agentic_core.L4_state.utils.context_util import L4ContextManager, get_context_manager
except ImportError:
    L4ContextManager = None  # type: ignore[assignment,misc]
    get_context_manager = None  # type: ignore[assignment]

__all__ = [
    "calculate_mccabe_complexity",
    "check_function_complexity",
    "LAYER_ORDER",
    "GRAVITY_RULES",
    "extract_layer_from_path",
    "extract_layer_from_module",
    "is_gravity_violation",
    "L4ContextManager",
    "get_context_manager",
]
