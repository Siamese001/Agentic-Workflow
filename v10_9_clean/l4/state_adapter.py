# state_adapter.py
"""
L4 — State Adapter (v10_9)

Centralized deterministic state manager.
Responsibilities:
    • Apply StatePatch objects
    • Enforce phase synchronization via StateMachine
    • Reconcile and prune memory via MemoryManager
    • Produce validated canonical state snapshots
"""

from __future__ import annotations

import copy
from typing import Any, Dict

from ..shared.models import StatePatch, WorkflowPhase
from .state_machine import StateMachine
from .memory_manager import MemoryManager
from .validation import validate_state


class StateAdapter:
    """High-level facade for deterministic orchestration state."""

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        state_machine: StateMachine | None = None,
    ) -> None:
        self.memory_manager = memory_manager or MemoryManager()
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

    # ------------------------------------------------------------------

    @property
    def state(self) -> Dict[str, Any]:
        """Return a deep copy for safety."""
        return copy.deepcopy(self._state)

    # ------------------------------------------------------------------

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
        """Apply one patch to state deterministically."""

        updated = copy.deepcopy(self._state)
        updated[patch.key] = patch.value

        # Reconcile memory
        updated = self.memory_manager.reconcile_state(updated)

        # Phase update
        phase_name = updated.get("phase")
        phase = WorkflowPhase(phase_name)
        if self.state_machine.phase != phase:
            self.state_machine.transition(phase)

        updated["phase"] = self.state_machine.phase.value
        updated["phase_metadata"] = {"phase": self.state_machine.phase.value}

        # Validation
        updated["metadata"]["validation"] = validate_state(updated)

        self._state = updated
        return self.state

    # ------------------------------------------------------------------

    def advance_phase(self, phase: WorkflowPhase) -> WorkflowPhase:
        """Explicit phase transition."""
        new_phase = self.state_machine.transition(phase)
        self._state["phase"] = new_phase.value
        return new_phase
