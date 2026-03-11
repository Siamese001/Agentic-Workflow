"""
Phase 5 — ViolationEventStore: L4 in-process persistence with prior-only fetch.

Guarantees:
- store_violation_event(event) -> event_hash  (idempotent by hash)
- fetch_latest_violation(before_tick) -> Optional[ViolationEvent]
  Returns only events with commit_tick < before_tick (prior-only).
- fetch_window(before_tick, window_ticks) -> list[ViolationEvent]
  Returns events with commit_tick in [before_tick - window_ticks, before_tick).
  Sorted ascending by (commit_tick, event_hash).

Same-cycle events (commit_tick == before_tick) are structurally invisible.
"""

from __future__ import annotations

from agentic_core.L4_state.types.violation_event_types import ViolationEvent


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class ViolationEventStore:
    """
    In-process L4 store for ViolationEvent records.

    Thread-safety: not guaranteed (single-threaded agent model assumed).
    Idempotent: storing the same event_hash twice is a no-op.
    """

    def __init__(self) -> None:
        self._events: dict[str, ViolationEvent] = {}

    def store_violation_event(self, event: ViolationEvent) -> str:
        """
        Persist a ViolationEvent. Returns event_hash.
        Idempotent: duplicate hashes are silently ignored.
        """
        if not isinstance(event, ViolationEvent):
            raise TypeError(
                f"ViolationEventStore.store_violation_event: "
                f"expected ViolationEvent, got {type(event).__name__}"
            )
        self._events[event.event_hash] = event
        return event.event_hash

    def fetch_latest_violation(self, before_tick: int) -> ViolationEvent | None:
        """
        Return the most recent ViolationEvent with commit_tick < before_tick.

        Same-cycle events (commit_tick == before_tick) are excluded.
        Returns None if no prior events exist.
        """
        prior = [e for e in self._events.values() if e.commit_tick < before_tick]
        if not prior:
            return None
        return max(prior, key=lambda e: (e.commit_tick, e.event_hash))

    def fetch_window(self, before_tick: int, window_ticks: int) -> list[ViolationEvent]:
        """
        Return all ViolationEvents with commit_tick in
        [before_tick - window_ticks, before_tick).

        Sorted ascending by (commit_tick, event_hash) for determinism.
        Same-cycle events (commit_tick == before_tick) are excluded.
        """
        if window_ticks < 0:
            raise ValueError(
                f"ViolationEventStore.fetch_window: window_ticks must be >= 0, got {window_ticks}"
            )
        low = before_tick - window_ticks
        window = [e for e in self._events.values() if low <= e.commit_tick < before_tick]
        return sorted(window, key=lambda e: (e.commit_tick, e.event_hash))

    def count(self) -> int:
        """Return total number of stored events."""
        return len(self._events)

    def clear(self) -> None:
        """Remove all stored events (test utility)."""
        self._events.clear()
