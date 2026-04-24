"""Default in-process token-bucket rate limiter for E4 ingress gate.

Closes gap G-08: E4 was a silent no-op when ``rate_limiter`` was not injected.
This module ships a deterministic, dependency-free token-bucket limiter that is
safe to use in unit tests and as a baseline in production. Deployments with
multi-process or multi-host topologies SHOULD swap in a Redis-backed limiter
via the same :class:`RateLimiter` protocol.

Layer authority: L5 (policy plane) — in-process state only, bounded memory.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class RateLimiter(Protocol):
    """Protocol all rate-limiter implementations satisfy."""

    def is_allowed(self, caller_id: str) -> bool:
        """Return True if ``caller_id`` is within quota and consume one token."""

        ...


@dataclass(frozen=True)
class TokenBucketConfig:
    """Configuration for :class:`TokenBucketRateLimiter`.

    * ``capacity``: max burst size (tokens).
    * ``refill_per_second``: steady-state sustained rate (tokens / second).
    * ``max_tracked_callers``: LRU eviction threshold to bound memory.
    """

    capacity: float = 60.0
    refill_per_second: float = 10.0
    max_tracked_callers: int = 10_000


class TokenBucketRateLimiter:
    """Per-caller token-bucket limiter with LRU eviction.

    Thread-safe via a single internal lock. Complexity per call is O(1)
    amortised (LRU update is a move-to-end on the OrderedDict).
    """

    def __init__(
        self,
        config: TokenBucketConfig | None = None,
        *,
        time_source: object | None = None,
    ) -> None:
        self._cfg = config or TokenBucketConfig()
        self._time = getattr(time_source, "time", None) or time.time
        self._lock = threading.Lock()
        self._buckets: "OrderedDict[str, tuple[float, float]]" = OrderedDict()

    def is_allowed(self, caller_id: str) -> bool:
        if not caller_id:
            return False

        now = float(self._time())
        cap = self._cfg.capacity
        refill = self._cfg.refill_per_second

        with self._lock:
            if caller_id in self._buckets:
                tokens, last_refill = self._buckets[caller_id]
                elapsed = max(0.0, now - last_refill)
                tokens = min(cap, tokens + elapsed * refill)
            else:
                tokens = cap
                self._evict_if_needed()

            if tokens < 1.0:
                self._buckets[caller_id] = (tokens, now)
                self._buckets.move_to_end(caller_id)
                return False

            tokens -= 1.0
            self._buckets[caller_id] = (tokens, now)
            self._buckets.move_to_end(caller_id)
            return True

    def _evict_if_needed(self) -> None:
        while len(self._buckets) >= self._cfg.max_tracked_callers:
            self._buckets.popitem(last=False)

    def snapshot(self, caller_id: str) -> tuple[float, float] | None:
        """Inspect a caller's (tokens, last_refill) — for tests and diagnostics."""

        with self._lock:
            return self._buckets.get(caller_id)


class UnboundedRateLimiter:
    """Test-only limiter that always allows. Logs a WARNING on first use."""

    def __init__(self) -> None:
        self._warned = False

    def is_allowed(self, caller_id: str) -> bool:  # noqa: ARG002 - protocol contract
        if not self._warned:
            import logging

            logging.getLogger(__name__).warning(
                "[UnboundedRateLimiter] Always-allow limiter in use; do not ship this in prod."
            )
            self._warned = True
        return True


__all__ = [
    "RateLimiter",
    "TokenBucketConfig",
    "TokenBucketRateLimiter",
    "UnboundedRateLimiter",
]
