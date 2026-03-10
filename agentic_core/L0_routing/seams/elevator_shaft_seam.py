"""
Elevator Shaft Seam - Pure JIT Context Loading

Contains ZERO routing or decision logic.
Only provides context loading functionality for L0 routing.
"""

from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def load_context_jit(intent_id: str) -> dict[str, Any]:
    """
    Load context just-in-time for given intent ID.

    Stub implementation returns deterministic empty dict.
    JIT loading is implemented at the caller layer, not in the seam.

    Args:
        intent_id: Intent identifier for context loading

    Returns:
        Dictionary with loaded context data (currently empty)
    """
    return {}
