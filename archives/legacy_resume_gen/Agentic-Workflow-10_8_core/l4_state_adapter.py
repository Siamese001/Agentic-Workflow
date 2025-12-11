"""
L4 — State Adapter

Bridges orchestration code with deterministic state management. It applies
state patches, coordinates memory handling, and surfaces the current phase via
an embedded finite state machine.
"""
from __future__ import annotations

import copy
from typing import Any, Dict

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l4_memory import MemoryManager  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l4_state import StateMachine  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l4_state import validate  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.utils_patch_helpers import apply_patch  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.utils_types import Phase, StatePatch  # INVALID: Cannot import from path with hyphens


class StateAdapter:
    """Facade for deterministic state operations."""

    def __init__(self, memory_manager: MemoryManager | None = None, state_machine: StateMachine | None = None) -> None:
        self.memory_manager = memory_manager or MemoryManager()
        self.state_machine = state_machine or StateMachine()
        self._state: Dict[str, object] = {
            "messages": [],
            "rag_history": [],
            "summary": "",
            "world": [],
            "session": {},
            "metadata": {},
            "phase": self.state_machine.phase.value,
            "phase_metadata": {"phase": self.state_machine.phase.value},
        }

    @property
    def state(self) -> Dict[str, object]:
        """Return a deep copy of the current state."""

        return copy.deepcopy(self._state)

    def apply_patch(self, patch: StatePatch) -> Dict[str, object]:
        """Apply a patch, reconcile memory budgets, and update cached state."""

        updated = apply_patch(self._state, patch)
        updated = self.memory_manager.reconcile_state(updated)
        # Sync FSM if the patch contains a phase directive
        phase_value = updated.get("phase")
        if phase_value is not None:
            phase = Phase(phase_value)
            if self.state_machine.phase != phase:
                self.state_machine.transition(phase)
        updated["phase"] = self.state_machine.phase.value
        metadata = self.state_machine.on_enter_phase(self.state_machine.phase)
        updated["phase_metadata"] = metadata
        updated.setdefault("metadata", {})
        updated["metadata"]["validation"] = validate(updated)
        self._state = updated
        return self.state

    def advance_phase(self, target: Phase) -> Phase:
        """Transition the FSM and mirror the phase into state."""

        new_phase = self.state_machine.transition(target)
        self._state["phase"] = new_phase.value
        return new_phase
