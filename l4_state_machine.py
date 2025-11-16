"""
L4 — State Machine

Provides deterministic transitions between orchestration phases.
"""
from __future__ import annotations

from typing import Dict

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

    def can_transition(self, target: Phase) -> bool:
        """Return True if the transition is legal."""

        return target in self._TRANSITIONS[self.phase]

    def transition(self, target: Phase) -> Phase:
        """Move to the target phase if legal, otherwise raise."""

        if not self.can_transition(target):
            raise ValueError(f"Illegal transition from {self.phase} to {target}")
        self.phase = target
        return self.phase

    def serialize(self) -> Dict[str, str]:
        """Return a serializable representation of the current phase."""

        return {"phase": self.phase.value}
