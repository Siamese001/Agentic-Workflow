"""
L4 - Pure State Management Layer

This layer handles all state management operations.
No business logic, tool execution, or orchestration is allowed here.
"""
from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Dict, Optional

from .types import (
    StateOperation,
    StateEventType,
    StatePath,
    StateTransition,
    StateSnapshot,
    StateError,
    StateValidationError,
    StateRollbackError,
)
from .manager import StateManager
from .pinecone_adapter import (
    PineconeAdapter,
    PineconeConfig,
    VectorRecord,
    VectorQueryResult,
)


def _prune_memory(state: Any, *, max_items: int = 200) -> Any:
    """Bound message and RAG history retention without mutating the input.

    Behavior (see tests/test_l4_state_adapter_v10_10.py):
    - If the state has neither `messages` nor `rag_history`, return it as-is.
    - If present and longer than `max_items`, truncate from the *front*,
      keeping the most recent entries.
    - For dataclass states, return a new instance with updated fields so the
      original object is never mutated in-place.
    """

    has_messages = hasattr(state, "messages")
    has_rag = hasattr(state, "rag_history")

    if not has_messages and not has_rag:
        return state

    if not is_dataclass(state):
        # Fallback: operate defensively and avoid surprising mutations for
        # non-dataclass objects by simply returning the original.
        return state

    updates: Dict[str, Any] = {}

    if has_messages:
        messages = getattr(state, "messages")
        if isinstance(messages, list) and len(messages) > max_items:
            updates["messages"] = messages[-max_items:]

    if has_rag:
        rag_history = getattr(state, "rag_history")
        if isinstance(rag_history, list) and len(rag_history) > max_items:
            updates["rag_history"] = rag_history[-max_items:]

    if not updates:
        return state

    return replace(state, **updates)


def record_correction_event(
    state: Any,
    *,
    surface: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
    ctx: Any = None,  # kept for signature compatibility; intentionally unused
) -> Any:
    """Append a correction entry to `correction_journal` if present.

    Contract from tests/test_l4_state_adapter_v10_10.py:
    - If the state has no `correction_journal` attribute, return it unchanged.
    - Otherwise, append a dict with keys `surface`, `message`, `metadata`.
    - Do not mutate the original instance; always inspect the returned one.
    """

    if not hasattr(state, "correction_journal"):
        return state

    journal = getattr(state, "correction_journal")
    if not isinstance(journal, list):
        return state

    if not is_dataclass(state):
        # Best-effort fallback for non-dataclass objects: mutate the journal
        # list but keep the state instance the same.
        entry = {
            "surface": surface,
            "message": message,
            "metadata": dict(metadata or {}),
        }
        journal.append(entry)
        return state

    new_journal = list(journal)
    new_journal.append(
        {
            "surface": surface,
            "message": message,
            "metadata": dict(metadata or {}),
        }
    )

    return replace(state, correction_journal=new_journal)


def apply_state_patch(
    l2_results: Any,
    corrections: Any,
    ctx: Any,
    *,
    safety_passed: bool = True
) -> Dict[str, Any]:
    """Apply L2 results as a state patch.
    
    This is a compatibility function for tests. It converts L2 execution
    results into a state patch dictionary.
    
    Args:
        l2_results: L2ResultBundle with execution results
        corrections: List of corrections to apply
        ctx: Execution context
        safety_passed: Whether safety checks passed
        
    Returns:
        dict: State patch with results
    """
    # Simple deterministic patch generation for testing
    patch = {
        "strategy": getattr(l2_results, "strategy", None),
        "rag": getattr(l2_results, "rag", None),
        "drafting": getattr(l2_results, "drafting", None),
        "qa": getattr(l2_results, "qa", None),
        "safety": getattr(l2_results, "safety", None),
        "corrections": list(corrections) if corrections else [],
        "safety_passed": safety_passed,
    }
    return patch


__all__ = [
    "StateOperation",
    "StateEventType",
    "StatePath",
    "StateTransition",
    "StateSnapshot",
    "StateError",
    "StateValidationError",
    "StateRollbackError",
    "StateManager",
    "PineconeAdapter",
    "PineconeConfig",
    "VectorRecord",
    "VectorQueryResult",
    "_prune_memory",
    "record_correction_event",
    "apply_state_patch",
]
