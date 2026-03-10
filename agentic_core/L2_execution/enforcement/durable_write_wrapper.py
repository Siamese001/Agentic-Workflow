"""
Durable Write Wrapper - Enforces sole mutation authority in L2.2.

All durable writes must go through this wrapper to track mutations.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)

# Global mutation tracking - imported from execution_gateway
from agentic_core.L0_routing.enforcement.execution_gateway import CURRENT_PHASE, MUTATION_COUNTER


def durable_write(operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Wrapper for all durable write operations.

    Args:
        operation: The actual write operation to perform
        *args: Arguments to pass to the operation
        **kwargs: Keyword arguments to pass to the operation

    Returns:
        Result of the operation

    Raises:
        AssertionError: If not in L2.2 phase
    """
    global CURRENT_PHASE, MUTATION_COUNTER

    # Enforce sole mutation point
    if CURRENT_PHASE != "L2.2":
        raise AssertionError(f"Durable write attempted in phase {CURRENT_PHASE}, only L2.2 allowed")

    # Track mutation
    MUTATION_COUNTER += 1
    Logger.info(f"[DURABLE_WRITE] Mutation #{MUTATION_COUNTER} in phase {CURRENT_PHASE}")

    # Execute the actual operation
    return operation(*args, **kwargs)


def reset_mutation_counter() -> None:
    """Reset mutation counter (for testing only)."""
    global MUTATION_COUNTER
    MUTATION_COUNTER = 0


def get_mutation_count() -> int:
    """Get current mutation count."""
    return MUTATION_COUNTER


def set_phase(phase: str) -> None:
    """Set current execution phase."""
    global CURRENT_PHASE
    CURRENT_PHASE = phase


def get_current_phase() -> str:
    """Get current execution phase."""
    return CURRENT_PHASE
