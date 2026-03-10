"""Healing outcome sink protocol — injectable seam for L2.3 outcome emission.

The sink is injected into the L2.3 dispatch path. When absent, no emission
occurs and the default runtime behaviour is unchanged.

Invariants:
  - Protocol-only; no concrete implementation in this module
  - emit() is fire-and-forget; caller does not branch on its return
"""

from __future__ import annotations

from typing import Protocol

from system_learning.types.healing_outcome_types import HealingOutcomeEvent


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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


__all__ = [
    "HealingOutcomeSink",
]
