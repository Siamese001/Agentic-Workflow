"""
L1 Execution Intent - Pure transformation without side effects.

L1 modules must return ExecutionIntent objects instead of performing mutations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionIntent:
    """Pure execution intent that L1 can return without side effects."""

    tool_name: str
    args: dict[str, Any]
    metadata: dict[str, Any]
    requires_commit: bool = True


@dataclass
class L1Result:
    """Standard L1 result containing either pure output or execution intents."""

    success: bool
    output: Any
    execution_intents: list[ExecutionIntent] | None = None
    error: str | None = None


# Global mutation guard for L1 purity enforcement
MUTATION_GUARD = 0


def assert_l1_purity(instance: Any) -> None:
    """Runtime assertion that L1 instance has no mutation capabilities."""
    assert not hasattr(instance, "redis"), "L1 instance cannot have redis client"
    assert not hasattr(instance, "pinecone"), "L1 instance cannot have pinecone client"
    assert not hasattr(instance, "subprocess"), "L1 instance cannot have subprocess access"
    assert not hasattr(instance, "filesystem"), "L1 instance cannot have direct filesystem access"


def increment_mutation_guard() -> None:
    """Increment global mutation guard - should only be called in L2.2."""
    global MUTATION_GUARD
    MUTATION_GUARD += 1


def get_mutation_count() -> int:
    """Get current mutation count."""
    return MUTATION_GUARD


def reset_mutation_guard() -> None:
    """Reset mutation guard (for testing only)."""
    global MUTATION_GUARD
    MUTATION_GUARD = 0
