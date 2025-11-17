# state_machine.py
"""
L4 — State Machine (v10_9)

Enforces legal workflow phase transitions:
    INIT → PLANNING → EXECUTING → REVIEWING → COMPLETE
"""

from __future__ import annotations

from typing import Dict, List

from ..shared.constants import WorkflowPhase
from ..shared.exceptions import IllegalTransitionError


class StateMachine:
    """Finite state machine for workflow phases."""

    _TRANSITIONS = {
        WorkflowPhase.INIT: {WorkflowPhase.PLANNING, WorkflowPhase.FAILED},
        WorkflowPhase.PLANNING: {WorkflowPhase.EXECUTING, WorkflowPhase.FAILED},
        WorkflowPhase.EXECUTING: {WorkflowPhase.REVIEWING, WorkflowPhase.FAILED},
        WorkflowPhase.REVIEWING: {WorkflowPhase.COMPLETE, WorkflowPhase.PLANNING, WorkflowPhase.FAILED},
        WorkflowPhase.COMPLETE: set(),
        WorkflowPhase.FAILED: set(),
    }

    def __init__(self, initial: WorkflowPhase = WorkflowPhase.INIT) -> None:
        self.phase = initial
        self._history: List[WorkflowPhase] = [initial]

    # ------------------------------------------------------------------

    def can_transition(self, target: WorkflowPhase) -> bool:
        return target in self._TRANSITIONS[self.phase]

    # ------------------------------------------------------------------

    def transition(self, target: WorkflowPhase) -> WorkflowPhase:
        if not self.can_transition(target):
            raise IllegalTransitionError(f"Illegal transition: {self.phase} → {target}")
        self.phase = target
        self._history.append(target)
        return self.phase

    # ------------------------------------------------------------------

    def serialize(self) -> Dict[str, str]:
        return {"phase": self.phase.value}

    def history(self) -> List[str]:
        return [p.value for p in self._history]
