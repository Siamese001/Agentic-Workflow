"""
L4 State Layer - Shared Utilities

SSOT for common functionality used across L5 agents:
- complexity_analyzer: McCabe cyclomatic complexity calculation
- layer_gravity: Layer hierarchy and gravity rule enforcement
- context_manager: Centralized state management for cross-agent learning

These utilities were extracted from L5 agents to eliminate code duplication.
"""

from agentic_core.L4_state.utils.context_manager import (
    L4ContextManager,
    get_context_manager,
)
from agentic_core.L4_state.utils.complexity_analyzer import (
    calculate_mccabe_complexity,
    check_function_complexity,
)
from agentic_core.L4_state.utils.layer_gravity import (
    GRAVITY_RULES,
    LAYER_ORDER,
    extract_layer_from_module,
    extract_layer_from_path,
    is_gravity_violation,
)

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
