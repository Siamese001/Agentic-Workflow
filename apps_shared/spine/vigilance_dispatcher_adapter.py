"""
Vigilance Dispatcher Adapter — bridges VigilanceDispatcher to spine adapters.

VigilanceDispatcher.dispatch() requires a VigilanceEventArtifact and an
enqueue_fn callable. The spine adapters call dispatch(*args, **kwargs).

This adapter:
1. Constructs a VigilanceEventArtifact from the execution context
2. Routes events to a module-level in-memory queue (non-blocking)
3. Falls back to no-op if VigilanceDispatcher cannot be imported

Dispatching is fire-and-forget: any failure is logged and swallowed.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)
_EVENT_QUEUE: deque = deque(maxlen=256)


def _drain_event_queue() -> list:
    """Return and clear the current event queue (for testing)."""
    events = list(_EVENT_QUEUE)
    _EVENT_QUEUE.clear()
    return events


def _build_real_dispatcher():
    from agentic_core.L6_observability.engines.vigilance_dispatcher import (
        VigilanceDispatcher,
        VigilanceEventArtifact,
    )

    return (VigilanceDispatcher, VigilanceEventArtifact)


class VigilanceDispatcherAdapter:
    """
    Adapter wrapping VigilanceDispatcher for use in spine adapters.

    dispatch() is fire-and-forget: failures are logged but never re-raised
    so vigilance events never block execution.
    """

    def __init__(self) -> None:
        try:
            VigilanceDispatcher, self._ArtifactCls = _build_real_dispatcher()
            self._dispatcher = VigilanceDispatcher()
            self._real = True
        except ImportError:
            logger.warning("VigilanceDispatcher unavailable; using null fallback")
            self._dispatcher = None
            self._ArtifactCls = None
            self._real = False

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        """
        Dispatch a vigilance event extracted from execution context kwargs.

        Accepts the same variadic signature as the null stubs so spine code
        needs no changes.  When invoked with named keys:
          trace_id (str) — from CID or cycle
          signals  (tuple[str, ...] | list[str]) — execution signals
          summary  (str) — human-readable summary

        Falls back to no-op if any step fails.
        """
        if not self._real:
            return
        try:
            trace_id: str = str(kwargs.get("trace_id", "unknown"))
            raw_signals = kwargs.get("signals", ())
            if isinstance(raw_signals, str):
                raw_signals = (raw_signals,)
            signals: tuple[str, ...] = tuple(raw_signals)
            summary: str = str(kwargs.get("summary", "spine-execution"))
            event = self._ArtifactCls.create(trace_id=trace_id, signals=signals, summary=summary)
            self._dispatcher.dispatch(event=event, enqueue_fn=_EVENT_QUEUE.append)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("VigilanceDispatcherAdapter.dispatch swallowed: %s", exc)

    @property
    def is_real(self) -> bool:
        """True if backed by the real VigilanceDispatcher, False for null fallback."""
        return self._real
