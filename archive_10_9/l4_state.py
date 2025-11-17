"""Layer 4 state management module consolidating state logic."""



from __future__ import annotations
import copy
from typing import Any, Dict

from l4_memory import MemoryManager
from utils_patch_helpers import apply_patch
from utils_types import Phase, StatePatch


class StateAdapter:
    """Facade for deterministic state operations."""

    def __init__(self, memory_manager: MemoryManager | None = None, state_machine: StateMachine | None = None) -> None:
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

    @property
    def state(self) -> Dict[str, Any]:
        """Return a deep copy of the current state."""

        return copy.deepcopy(self._state)

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
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
"""
L4 — State Machine

Provides deterministic transitions between orchestration phases.
"""

from typing import Dict, List

from utils_types import Phase


class StateMachine:
    """Finite state machine enforcing legal transitions."""

    _TRANSITIONS = {
        Phase.INIT: {Phase.PLANNING, Phase.FAILED},
        Phase.PLANNING: {Phase.EXECUTING, Phase.FAILED},
        Phase.EXECUTING: {Phase.REVIEWING, Phase.FAILED},
        Phase.REVIEWING: {Phase.COMPLETE, Phase.PLANNING, Phase.FAILED},
        Phase.COMPLETE: set(),
        Phase.FAILED: set(),
    }

    def __init__(self, initial: Phase = Phase.INIT) -> None:
        self.phase = initial
        self._history: List[Phase] = [initial]

    def can_transition(self, target: Phase) -> bool:
        """Return True if the transition is legal."""

        return target in self._TRANSITIONS[self.phase]

    def transition(self, target: Phase) -> Phase:
        """Move to the target phase if legal, otherwise raise."""

        if not self.can_transition(target):
            raise ValueError(f"Illegal transition from {self.phase} to {target}")
        self.phase = target
        self._history.append(target)
        return self.phase

    def serialize(self) -> Dict[str, str]:
        """Return a serializable representation of the current phase."""

        return {"phase": self.phase.value}

    def on_enter_phase(self, phase: Phase) -> Dict[str, str]:
        return {"phase": phase.value}

    def history(self) -> List[str]:
        return [p.value for p in self._history]
"""
State Validation Utilities

Provides lightweight validation of orchestration state with warnings for
cross-field inconsistencies.
"""

from typing import Any, Dict, List


_EXPECTED_TYPES = {
    "messages": list,
    "rag_history": list,
    "summary": str,
    "world": list,
    "session": dict,
    "metadata": dict,
    "phase": str,
    "phase_metadata": dict,
}


def validate(state: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate the orchestration state for required keys and consistency."""

    missing: List[str] = []
    type_mismatch: List[str] = []
    cross_field_warnings: List[str] = []

    for field, expected_type in _EXPECTED_TYPES.items():
        if field not in state:
            missing.append(field)
            continue
        if not isinstance(state[field], expected_type):
            type_mismatch.append(field)

    if state.get("draft") is not None and len(state.get("messages", [])) == 0:
        cross_field_warnings.append("draft present but messages are empty")

    if state.get("qa_report") is not None and "plan" not in state:
        cross_field_warnings.append("qa_report present without plan")

    return {
        "missing": missing,
        "type_mismatch": type_mismatch,
        "cross_field_warnings": cross_field_warnings,
    }
