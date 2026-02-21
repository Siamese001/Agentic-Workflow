"""
Elevator Shaft Seam - Pure JIT Context Loading

Contains ZERO routing or decision logic.
Only provides context loading functionality for L0 routing.
"""

from typing import Any


def load_context_jit(intent_id: str) -> dict[str, Any]:
    """
    Load context just-in-time for given intent ID.

    Stub implementation returns deterministic empty dict.

    Args:
        intent_id: Intent identifier for context loading

    Returns:
        Dictionary with loaded context data (currently empty)
    """
    # Stub implementation - no business logic
    # Future: Load context from appropriate sources
    return {}
