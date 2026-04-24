"""LRU-bounded replay cache for E6 ingress deduplication.

Closes gap G-09: prior dedup used an unbounded in-memory ``set[str]``. This
module provides a thread-safe LRU cache with TTL eviction suitable for
single-process deployments; a Redis-backed implementation may be swapped in
via the same :class:`ReplayCache` protocol.

Layer authority: L5 (policy plane) — bounded memory, no durable writes.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Protocol, runtime_checkable


@runtime_checkable
class ReplayCache(Protocol):
    """Protocol for ingress replay-dedup caches."""

    def seen_and_mark(self, request_id: str) -> bool:
        """Return True if ``request_id`` was already seen; mark it otherwise."""

        ...


class LRUReplayCache:
    """Bounded LRU cache with optional TTL eviction.

    Used by :class:`IngressEnvelopeCheck` to detect duplicate ``request_id``
    within a configurable retention window. Both capacity- and time-based
    eviction are O(1) amortised per call.
    """

    def __init__(
        self,
        *,
        capacity: int = 100_000,
        ttl_seconds: float | None = 3600.0,
        time_source: object | None = None,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = int(capacity)
        self._ttl = float(ttl_seconds) if ttl_seconds is not None else None
        self._time = getattr(time_source, "time", None) or time.time
        self._lock = threading.Lock()
        self._items: "OrderedDict[str, float]" = OrderedDict()

    def seen_and_mark(self, request_id: str) -> bool:
        if not request_id:
            return False
        now = float(self._time())

        with self._lock:
            self._evict_expired(now)

            if request_id in self._items:
                stamp = self._items[request_id]
                if self._ttl is None or (now - stamp) <= self._ttl:
                    self._items.move_to_end(request_id)
                    return True
                # TTL expired — fall through to re-mark.
                del self._items[request_id]

            self._items[request_id] = now
            self._items.move_to_end(request_id)
            while len(self._items) > self._capacity:
                self._items.popitem(last=False)
            return False

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def _evict_expired(self, now: float) -> None:
        if self._ttl is None:
            return
        cutoff = now - self._ttl
        # OrderedDict iteration order == insertion order; expired items are at the head.
        while self._items:
            oldest_key = next(iter(self._items))
            if self._items[oldest_key] < cutoff:
                del self._items[oldest_key]
            else:
                break


class SetReplayCache:
    """Back-compat wrapper around an external ``set[str]`` for callers that
    passed a set into :class:`IngressEnvelopeCheck` directly.

    NOT recommended: unbounded; prefer :class:`LRUReplayCache`.
    """

    def __init__(self, seen: set[str]) -> None:
        self._seen = seen
        self._lock = threading.Lock()

    def seen_and_mark(self, request_id: str) -> bool:
        if not request_id:
            return False
        with self._lock:
            if request_id in self._seen:
                return True
            self._seen.add(request_id)
            return False


__all__ = ["LRUReplayCache", "ReplayCache", "SetReplayCache"]
