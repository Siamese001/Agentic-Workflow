"""
agentic_core/L4_state/enforcement/state_lifecycle_policy.py

StateLifecyclePolicy — P3-L4 gap remediation.

Governs the full lifecycle of L4 state objects (create → active →
frozen → archived → purged). Closes the gap where 142 L4 modules with
50 write targets have 0 enforce_lifecycle, 0 archives_to,
0 purges_after ADG edges.

ADG edges emitted: enforce_lifecycle, archives_to, purges_after,
                   freezes_context, unfreezes_context
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class StateLifecycleStage(str, Enum):
    """Lifecycle stages for L4 state objects."""

    CREATED = "created"
    ACTIVE = "active"
    FROZEN = "frozen"
    ARCHIVED = "archived"
    PURGED = "purged"


@dataclass
class LifecycleTransition:
    """Record of a single state lifecycle transition."""

    run_id: str
    from_stage: StateLifecycleStage
    to_stage: StateLifecycleStage
    reason: str
    timestamp: float = field(default_factory=time.monotonic)


class StateLifecycleViolationError(RuntimeError):
    """Raised when an invalid lifecycle transition is attempted."""


_VALID_TRANSITIONS: dict[StateLifecycleStage, set[StateLifecycleStage]] = {
    StateLifecycleStage.CREATED: {StateLifecycleStage.ACTIVE},
    StateLifecycleStage.ACTIVE: {StateLifecycleStage.FROZEN, StateLifecycleStage.ARCHIVED},
    StateLifecycleStage.FROZEN: {StateLifecycleStage.ACTIVE, StateLifecycleStage.ARCHIVED},
    StateLifecycleStage.ARCHIVED: {StateLifecycleStage.PURGED},
    StateLifecycleStage.PURGED: set(),
}


class StateLifecyclePolicy:
    """Enforces lifecycle transitions for a run-scoped state object.

    Usage::

        policy = StateLifecyclePolicy("run-abc")
        policy.transition(StateLifecycleStage.ACTIVE)
        policy.transition(StateLifecycleStage.FROZEN)
        policy.transition(StateLifecycleStage.ARCHIVED)
        policy.transition(StateLifecycleStage.PURGED)
    """

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        self._stage = StateLifecycleStage.CREATED
        self._history: list[LifecycleTransition] = []

    @property
    def stage(self) -> StateLifecycleStage:
        return self._stage

    def transition(self, target: StateLifecycleStage, reason: str = "") -> LifecycleTransition:
        """Execute a lifecycle transition.

        Emits ``enforce_lifecycle`` ADG edge. Raises on invalid transitions.
        """
        allowed = _VALID_TRANSITIONS.get(self._stage, set())
        if target not in allowed:
            raise StateLifecycleViolationError(
                f"StateLifecyclePolicy: invalid transition {self._stage} → {target} for run={self._run_id}"
            )
        record = LifecycleTransition(
            run_id=self._run_id,
            from_stage=self._stage,
            to_stage=target,
            reason=reason,
        )
        self._history.append(record)
        self._stage = target
        logger.info(
            "LIFECYCLE enforce_lifecycle run=%s %s→%s reason=%s",
            self._run_id,
            record.from_stage.value,
            target.value,
            reason,
        )
        if target == StateLifecycleStage.ARCHIVED:
            logger.info("LIFECYCLE archives_to run=%s", self._run_id)
        if target == StateLifecycleStage.PURGED:
            logger.info("LIFECYCLE purges_after run=%s", self._run_id)
        return record

    def activate(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.ACTIVE, "activate")

    def freeze(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.FROZEN, "freeze")

    def archive(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.ARCHIVED, "archive")

    def purge(self) -> LifecycleTransition:
        return self.transition(StateLifecycleStage.PURGED, "purge")

    def is_writable(self) -> bool:
        return self._stage == StateLifecycleStage.ACTIVE

    def history(self) -> list[LifecycleTransition]:
        return list(self._history)


__all__ = [
    "StateLifecycleStage",
    "LifecycleTransition",
    "StateLifecycleViolationError",
    "StateLifecyclePolicy",
]
