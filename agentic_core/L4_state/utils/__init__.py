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
