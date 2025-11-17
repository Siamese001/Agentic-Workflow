"""
L4 — State Adapter (v10_9_clean)

Unified, deterministic state management layer.
Preserves 10_7 semantics (messages / rag_history / summary / world),
implements 10_8 architecture boundaries, and integrates the unified
ContextBudget + MemoryManager from core/services.py.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List

from utils_patch_helpers import apply_patch
from utils_types import Phase, StatePatch, Message

from ..core.services import ContextBudget, ContextBudgetManager
from ..core.services import MemoryManager  # unified manager
from ..core.services import normalize_world_facts  # world fact coercion
from ..core.state_machine import StateMachine  # clean 10_9 FSM
from ..core.state_validation import validate   # clean 10_9 validator


# ---------------------------------------------------------------------
# SINGLE authoritative MemoryManager
# (delegates all pruning to ContextBudget)
# ---------------------------------------------------------------------

# NOTE: We import MemoryManager from services.py — do NOT redefine it here.


# ---------------------------------------------------------------------
# SINGLE authoritative StateAdapter
# ---------------------------------------------------------------------

class StateAdapter:
    """Facade for deterministic, architecture-correct state operations."""

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        state_machine: StateMachine | None = None,
        context_budget: ContextBudget | None = None,
    ) -> None:

        self.context_budget = context_budget or ContextBudget()
        self.memory_manager = memory_manager or MemoryManager(self.context_budget)
        self.state_machine = state_machine or StateMachine()

        self._state: Dict[str, Any] = {
            "messages": [],
            "rag_history": [],
            "summary": "",
            "world": [],
            "session": {},
            "metadata": {},
            "phase": self.state_machine.phase.value,
            "phase_metadata": {"phase": self.state_machine.phase.value},
        }

    # -------------------------------
    # Accessor
    # -------------------------------

    @property
    def state(self) -> Dict[str, Any]:
        """Return deep copy for immutability guarantees."""
        return copy.deepcopy(self._state)

    # -------------------------------
    # Patch application
    # -------------------------------

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
        """Apply patch, prune+canonicalize via MemoryManager, sync FSM, validate."""

        updated = apply_patch(self._state, patch)

        # Canonicalize + enforce budgets
        updated = self.memory_manager.reconcile_state(updated)

        # Phase sync
        phase_value = updated.get("phase")
        if phase_value is not None:
            target_phase = Phase(phase_value)
            if self.state_machine.phase != target_phase:
                self.state_machine.transition(target_phase)

        updated["phase"] = self.state_machine.phase.value
        updated["phase_metadata"] = self.state_machine.on_enter_phase(
            self.state_machine.phase
        )

        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validate(updated)

        self._state = updated
        return self.state

    # -------------------------------
    # Manual phase advancement
    # -------------------------------

    def advance_phase(self, target: Phase) -> Phase:
        """Manual FSM transition (rarely used)."""
        new_phase = self.state_machine.transition(target)
        self._state["phase"] = new_phase.value
        return new_phase


# ---------------------------------------------------------------------
# State Views (single source)
# ---------------------------------------------------------------------

def get_conversational_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages", []) or []),
        "summary": state.get("summary", "") or "",
    }


def get_retrieval_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history", []) or []),
        "world": copy.deepcopy(state.get("world", []) or []),
    }


def get_evidence_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history", []) or []),
        "world": copy.deepcopy(state.get("world", []) or []),
    }


def get_prompt_context_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages", []) or []),
        "summary": state.get("summary", "") or "",
        "rag_history": copy.deepcopy(state.get("rag_history", []) or []),
        "world": copy.deepcopy(state.get("world", []) or []),
    }


__all__ = [
    "StateAdapter",
    "get_conversational_view",
    "get_retrieval_view",
    "get_evidence_view",
    "get_prompt_context_view",
]
