# FILE: l4.py
"""
Unified L4 State Layer (v10_10) — STATE & MEMORY MANAGEMENT (HARDENED)

This module implements the "Memory" of the agent (Pillar 7, 4).
It is the ONLY component allowed to mutate the workflow state.

Responsibilities:
    1. Atomic Updates: Apply strict `StatePatch` objects.
    2. Context Budgeting: Prune history to prevent overflow (Pillar 7).
    3. History Tracking: Record phase transitions and episodic events.
    4. Serialization: Ensure state remains JSON-serializable for API output.

Refactor Highlights (v10_10):
    • Removed manual `validate_state` (Pydantic handles this).
    • Added `ContextBudget` logic to strictly cap message history.
    • Optimized for Pydantic model storage within state dicts.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Union

from models import (
    StatePatch,
    WorkflowPhase,
    WorkflowState,
    AgenticBaseModel
)

# =============================================================================
# MEMORY BUDGET ENGINE (Pillar 7)
# =============================================================================

class ContextBudget:
    """
    Enforces limits on conversation history and context size.
    """
    MAX_MESSAGES = 50
    MAX_RAG_ITEMS = 20
    
    @classmethod
    def prune_messages(cls, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keep only the most recent messages + system prompt.
        """
        if len(messages) <= cls.MAX_MESSAGES:
            return messages
        
        # Always preserve the first message (System Prompt usually)
        # and the last N messages.
        return [messages[0]] + messages[-(cls.MAX_MESSAGES - 1):]

    @classmethod
    def prune_rag(cls, items: List[Any]) -> List[Any]:
        """
        Keep only top-ranked evidence.
        """
        if len(items) <= cls.MAX_RAG_ITEMS:
            return items
        return items[:cls.MAX_RAG_ITEMS]


# =============================================================================
# STATE ADAPTER
# =============================================================================

class StateAdapter:
    """
    The unified interface for state mutation.
    """

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self._state: Dict[str, Any] = {}
        self._phase: WorkflowPhase = WorkflowPhase.INIT
        self._phase_history: List[WorkflowPhase] = []
        
        if initial_state:
            self.reset(initial_state)

    @property
    def state(self) -> Dict[str, Any]:
        """
        Return a deep copy of the state to prevent external mutation bugs.
        Converts internal Pydantic models to dicts for clean export.
        """
        # We do a serialization pass to ensure downstream consumers get pure JSON
        # This satisfies the API contract of WorkflowState.result
        serialized = {}
        for k, v in self._state.items():
            if isinstance(v, AgenticBaseModel):
                serialized[k] = v.model_dump()
            elif isinstance(v, list):
                serialized[k] = [
                    x.model_dump() if isinstance(x, AgenticBaseModel) else x 
                    for x in v
                ]
            else:
                serialized[k] = v # Primitives
        
        return copy.deepcopy(serialized)

    @property
    def phase(self) -> WorkflowPhase:
        return self._phase

    # -------------------------------------------------------------------------
    # MUTATORS (The Only Way to Write)
    # -------------------------------------------------------------------------

    def reset(self, initial_state: Dict[str, Any]) -> None:
        """
        Initialize the state, applying budget constraints immediately.
        """
        # Deep copy to avoid reference issues
        base = copy.deepcopy(initial_state)
        
        # Normalize core keys
        base.setdefault("messages", [])
        base.setdefault("rag_history", [])
        base.setdefault("summary", "")
        base.setdefault("metadata", {})
        
        # Apply Budgeting (Pillar 7)
        base["messages"] = ContextBudget.prune_messages(base["messages"])
        
        self._state = base
        self._phase = WorkflowPhase.INIT
        self._phase_history = [self._phase]

    def set_phase(self, phase: WorkflowPhase) -> None:
        """Transition workflow phase."""
        self._phase = phase
        self._phase_history.append(phase)
        
        # Update metadata tracking
        meta = self._state.setdefault("metadata", {})
        meta["phase"] = phase.value
        meta["phase_history"] = [p.value for p in self._phase_history]

    def apply_patch(self, patch: StatePatch) -> None:
        """
        Apply an atomic patch to the state.
        Handles merging dicts/lists and replacing values.
        """
        key = patch.key
        value = patch.value

        # 1. Merge Strategy for Dicts
        if isinstance(value, dict) and isinstance(self._state.get(key), dict):
            self._state[key].update(value)
        
        # 2. Append Strategy for Lists
        elif isinstance(value, list) and isinstance(self._state.get(key), list):
            self._state[key].extend(value)
            
            # Re-apply budgeting if we modified a budgeted list
            if key == "messages":
                self._state["messages"] = ContextBudget.prune_messages(self._state["messages"])
            elif key in ("rag_history", "rag_result"):
                 # Heuristic: if it looks like a list of items, prune it
                 self._state[key] = ContextBudget.prune_rag(self._state[key])

        # 3. Replace Strategy for everything else (Pydantic models, primitives)
        else:
            self._state[key] = value

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def add_message(self, role: str, content: str) -> None:
        """Helper to append chat history."""
        msgs = self._state.get("messages", [])
        msgs.append({"role": role, "content": content})
        self._state["messages"] = ContextBudget.prune_messages(msgs)
