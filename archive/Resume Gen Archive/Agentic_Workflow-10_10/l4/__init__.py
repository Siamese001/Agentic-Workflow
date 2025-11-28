"""
State management layer for résumé processing workflow coordination.

Handles all state management operations for comprehensive résumé enhancement workflows without business logic.
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
from .triplet_store import (
    TemporalType,
    TripletStatus,
    Triplet,
    TripletQuery,
    TripletStore,
    create_triplet,
    PREDICATES,
)
from .entity_resolution import (
    EntityType,
    CanonicalEntity,
    EntityMention,
    ResolutionResult,
    EntityRegistry,
    create_entity,
    create_mention,
)


def _prune_memory(state: Any, *, max_items: int = 200) -> Any:
    """
    Bounds memory retention for résumé processing workflow state.

    Limits message and RAG history retention without mutating input state for efficient résumé enhancement.
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
    """
    Records correction events for résumé processing workflow state.

    Appends correction entries to maintain audit trail for résumé enhancement operations.
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
    """
    Applies L2 results as state patch for résumé processing workflows.
    
    Compatibility function that converts L2 execution results into state patch for résumé enhancement.
    
    Args:
        l2_results: L2ResultBundle with résumé processing execution results
        corrections: List of corrections to apply for résumé enhancement
        ctx: Execution context for résumé workflows
        safety_passed: Whether résumé enhancement safety checks passed
        
    Returns:
        dict: State patch with résumé processing results
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
    # State types
    "StateOperation",
    "StateEventType",
    "StatePath",
    "StateTransition",
    "StateSnapshot",
    "StateError",
    "StateValidationError",
    "StateRollbackError",
    "StateManager",
    # Pinecone
    "PineconeAdapter",
    "PineconeConfig",
    "VectorRecord",
    "VectorQueryResult",
    # Triplet store
    "TemporalType",
    "TripletStatus",
    "Triplet",
    "TripletQuery",
    "TripletStore",
    "create_triplet",
    "PREDICATES",
    # Entity resolution
    "EntityType",
    "CanonicalEntity",
    "EntityMention",
    "ResolutionResult",
    "EntityRegistry",
    "create_entity",
    "create_mention",
    # Utilities
    "_prune_memory",
    "record_correction_event",
    "apply_state_patch",
]



