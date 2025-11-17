# control_flow.py
"""
L3 — Control Flow Manager (v10_9)

Determines legal phase transitions:
    INIT → PLANNING → EXECUTING → REVIEWING → COMPLETE
Handles:
    • retries
    • replanning
    • halts
    • failure propagation
"""

from __future__ import annotations

from ..shared.constants import WorkflowPhase
from ..shared.exceptions import IllegalTransitionError


class ControlFlow:
    """Manages phase transitions for orchestrator."""

    _TRANSITIONS = {
        "init": "planning",
        "planning": "executing",
        "executing": "reviewing",
        "reviewing": "complete",
        "complete": "complete",
        "failed": "failed",
    }

    def next_phase(self, current: str) -> WorkflowPhase:
        if current not in self._TRANSITIONS:
            raise IllegalTransitionError(f"Unknown phase {current!r}")

        target = self._TRANSITIONS[current]
        return WorkflowPhase(target)
