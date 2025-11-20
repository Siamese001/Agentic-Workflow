# FILE: l4.py
"""
Unified L4 State Layer (v10_10) — STATE & MEMORY MANAGEMENT

This module implements Pillar 4 (Workflow State) and Pillar 7 (Context Budgeting).
It acts as the "Hippocampus" of the agent, managing short-term memory and
ensuring state transitions are atomic and safe.

Responsibilities:
    1. Atomic Mutation: Apply `StatePatch` updates (merge/replace/append).
    2. Context Budgeting: Enforce token/message limits on history.
    3. State Serialization: Prepare state for Pydantic validation.

Refactor Highlights (v10_10):
    • Implements Dot-Notation Patching (surgical updates).
    • Removes manual type validation (relying on `models.py`).
    • Adds explicit `record_correction` logging.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Union
from pydantic import BaseModel

from models import (
    StatePatch,
    WorkflowPhase,
    CorrectionSignal,
    AgenticBaseModel
)

# =============================================================================
# CONTEXT BUDGET ENGINE (Pillar 7)
# =============================================================================

class ContextBudget:
    """
    Enforces limits on memory to prevent token overflow.
    """
    MAX_MESSAGES = 20
    MAX_RAG_DOCS = 10
    
    @staticmethod
    def prune_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Maintains a sliding window of conversation history.
        Always preserves the System Prompt (index 0) if present.
        """
        if len(messages) <= ContextBudget.MAX_MESSAGES:
            return messages
            
        # Assumption: Msg 0 is System/Context. Keep it.
        # Keep last (N-1) messages.
        return [messages[0]] + messages[-(ContextBudget.MAX_MESSAGES - 1):]

    @staticmethod
    def prune_rag_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keeps only top-k most relevant documents.
        """
        # In v10_10, docs are already sorted by score in L2.
        return docs[:ContextBudget.MAX_RAG_DOCS]


# =============================================================================
# STATE ADAPTER
# =============================================================================

class StateAdapter:
    """
    Mutable wrapper around the Workflow State.
    All writes MUST go through `apply_patch` or specialized methods.
    """

    def __init__(self, initial_state: Dict[str, Any] = None):
        # We hold state as a Dict to allow flexibility before final Pydantic export
        self._state: Dict[str, Any] = {
            "workflow_id": "unknown",
            "phase": WorkflowPhase.INIT.value,
            "objective": "",
            "messages": [],
            "rag_docs": [],
            "correction_log": [],
            "meta_profile": {}
        }
        if initial_state:
            self.reset(initial_state)

    @property
    def state(self) -> Dict[str, Any]:
        """Read-only view of current state."""
        return copy.deepcopy(self._state)

    def reset(self, initial_state: Dict[str, Any]) -> None:
        """
        Hard reset of the state memory.
        """
        # Merge default structure with input
        self._state.update(copy.deepcopy(initial_state))
        # Apply immediate budgeting
        self._state["messages"] = ContextBudget.prune_messages(self._state.get("messages", []))
        self.set_phase(WorkflowPhase.INIT)

    def set_phase(self, phase: WorkflowPhase) -> None:
        """Update the workflow phase."""
        self._state["phase"] = phase.value

    def record_correction(self, signal: CorrectionSignal) -> None:
        """Log a self-correction signal (Pillar 5)."""
        log = self._state.get("correction_log", [])
        log.append(signal.model_dump())
        self._state["correction_log"] = log

    # -------------------------------------------------------------------------
    # ATOMIC PATCHING (Pillar 4)
    # -------------------------------------------------------------------------

    def apply_patch(self, patch: StatePatch) -> None:
        """
        Applies a mutation to the state based on the operation type.
        """
        # If value is a Pydantic model, dump it to dict for storage
        value = patch.value
        if isinstance(value, BaseModel):
            value = value.model_dump()

        # Handle Root-Level Keys directly (Fast Path)
        if "." not in patch.path:
            self._apply_root_op(patch.path, patch.op, value)
            return

        # Handle Nested Keys (Slow Path - e.g. "meta_profile.bias_routing_fast")
        # Only supports 'replace' for nested keys in this implementation
        self._apply_nested_replace(patch.path, value)

    def _apply_root_op(self, key: str, op: str, value: Any) -> None:
        if op == "replace":
            self._state[key] = value
        
        elif op == "merge":
            target = self._state.get(key, {})
            if isinstance(target, dict) and isinstance(value, dict):
                target.update(value)
                self._state[key] = target
        
        elif op == "append":
            target = self._state.get(key, [])
            if isinstance(target, list):
                if isinstance(value, list):
                    target.extend(value)
                else:
                    target.append(value)
                self._state[key] = target
        
        # Post-Mutation Budgeting
        if key == "messages":
            self._state["messages"] = ContextBudget.prune_messages(self._state["messages"])
        elif key == "rag_docs":
            self._state["rag_docs"] = ContextBudget.prune_rag_docs(self._state["rag_docs"])

    def _apply_nested_replace(self, path: str, value: Any) -> None:
        keys = path.split(".")
        target = self._state
        
        # Traverse to parent
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        
        # Set value
        target[keys[-1]] = value
