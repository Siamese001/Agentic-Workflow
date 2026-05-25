"""Healing outcome sink protocol — injectable seam for L2.3 outcome emission.

The sink is injected into the L2.3 dispatch path. When absent, no emission
occurs and the default runtime behaviour is unchanged.

Invariants:
  - Protocol-only; no concrete implementation in this module
  - emit() is fire-and-forget; caller does not branch on its return
"""

from __future__ import annotations

from typing import Protocol

from agentic_core.L6_system_learning.types.healing_outcome_types import HealingOutcomeEvent


class HealingOutcomeSink(Protocol):
    """Protocol for receiving L2.3 healing outcome events.

    Implementations may buffer, aggregate, or forward events.
    The caller MUST NOT branch on any side-effect of emit().
    """

    def emit(self, event: HealingOutcomeEvent) -> None:
        """Emit a single healing outcome event.

        Parameters
        ----------
        event : HealingOutcomeEvent
            Immutable outcome event to record.
        """
        ...


__all__ = ["HealingOutcomeSink"]
