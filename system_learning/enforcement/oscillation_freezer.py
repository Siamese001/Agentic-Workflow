"""
OscillationDetector — Adaptive thrashing prevention for meta-learning.

If the same threshold parameter flips in opposite directions twice within
a cooldown window, the parameter is frozen for N cycles.  This prevents
oscillatory meta-learning from destabilising the routing configuration.

Phase 6.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class _ThresholdEvent:
    parameter: str
    value: Any
    cycle: int


class ParameterFrozenError(RuntimeError):
    """Raised when a frozen parameter is modified during its freeze window."""


class OscillationDetector:
    """Detects and freezes oscillating meta-learning threshold parameters.

    Usage::

        detector = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        detector.record_change("routing_threshold", 0.7, cycle=1)
        detector.record_change("routing_threshold", 0.5, cycle=2)
        # Second flip within cooldown_window triggers freeze:
        detector.record_change("routing_threshold", 0.7, cycle=3)  # -> ParameterFrozenError

    Args:
        cooldown_window: Number of most-recent events to inspect per parameter.
        freeze_cycles: How many cycles a frozen parameter remains locked.
    """

    def __init__(self, cooldown_window: int = 10, freeze_cycles: int = 5) -> None:
        if cooldown_window < 2:
            raise ValueError("cooldown_window must be >= 2")
        if freeze_cycles < 1:
            raise ValueError("freeze_cycles must be >= 1")
        self._cooldown_window = cooldown_window
        self._freeze_cycles = freeze_cycles
        self._lock = threading.Lock()
        self._history: dict[str, deque[_ThresholdEvent]] = {}
        self._frozen_until: dict[str, int] = {}

    def record_change(self, parameter: str, new_value: Any, cycle: int) -> None:
        """Record a parameter change and enforce freeze if oscillation detected.

        Args:
            parameter: Name of the threshold parameter being changed.
            new_value: The proposed new value.
            cycle: Current meta-learning cycle counter (monotonically increasing).

        Raises:
            ParameterFrozenError: if *parameter* is within its freeze window.
        """
        with self._lock:
            self._assert_not_frozen(parameter, cycle)
            self._append_event(parameter, new_value, cycle)
            if self._oscillation_detected(parameter):
                freeze_until = cycle + self._freeze_cycles
                self._frozen_until[parameter] = freeze_until
                raise ParameterFrozenError(
                    f"OscillationDetector: parameter {parameter!r} oscillated twice within cooldown_window={self._cooldown_window}; frozen until cycle {freeze_until}"
                )

    def is_frozen(self, parameter: str, cycle: int) -> bool:
        """Return True if *parameter* is currently frozen at *cycle*."""
        with self._lock:
            return cycle <= self._frozen_until.get(parameter, -1)

    def frozen_count(self) -> int:
        """Return number of currently-tracked frozen parameters."""
        with self._lock:
            return len(self._frozen_until)

    def reset_for_testing(self) -> None:
        """Clear all history and frozen state (test isolation only)."""
        with self._lock:
            self._history.clear()
            self._frozen_until.clear()

    def _assert_not_frozen(self, parameter: str, cycle: int) -> None:
        freeze_until = self._frozen_until.get(parameter, -1)
        if cycle <= freeze_until:
            raise ParameterFrozenError(
                f"OscillationDetector: parameter {parameter!r} is frozen until cycle {freeze_until} (current cycle={cycle})"
            )

    def _append_event(self, parameter: str, value: Any, cycle: int) -> None:
        if parameter not in self._history:
            self._history[parameter] = deque(maxlen=self._cooldown_window)
        self._history[parameter].append(_ThresholdEvent(parameter, value, cycle))

    def _oscillation_detected(self, parameter: str) -> bool:
        """Return True if *parameter* has flipped direction at least twice."""
        events = list(self._history.get(parameter, []))
        if len(events) < 3:
            return False
        flip_count = 0
        for i in range(1, len(events)):
            if events[i].value != events[i - 1].value:
                flip_count += 1
                if flip_count >= 2:
                    return True
        return False


__all__ = ["OscillationDetector", "ParameterFrozenError"]
