"""G8 Thundering-herd mitigation: single-flight lock + TTL jitter helpers."""

from __future__ import annotations

import contextlib
import logging
import random
import time
from typing import Any, Iterator

_LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def acquire_single_flight(
    redis_client: Any,
    key: str,
    *,
    ttl_seconds: int = 10,
    wait_seconds: float = 0.0,
    retry_interval_seconds: float = 0.1,
) -> Iterator[bool]:
    """Yield True iff this caller acquired the single-flight lock.

    Redis errors yield False so the caller proceeds without the lock
    (prefer a double-compute over a hang).
    """
    if redis_client is None or not key:
        yield False
        return

    lock_key = f"sc:lock:{key}"
    acquired = False
    deadline = time.monotonic() + max(0.0, wait_seconds)
    try:
        while True:
            try:
                ok = bool(
                    redis_client.set(
                        lock_key, "1", nx=True, ex=max(1, int(ttl_seconds))
                    )
                )
            except (AttributeError, ConnectionError, TimeoutError, RuntimeError) as exc:
                _LOGGER.debug("single-flight redis error: %s", exc)
                ok = False
            if ok:
                acquired = True
                break
            if time.monotonic() >= deadline:
                break
            time.sleep(retry_interval_seconds)
        yield acquired
    finally:
        if acquired:
            try:
                redis_client.delete(lock_key)
            except (AttributeError, ConnectionError, TimeoutError, RuntimeError) as exc:  # guardian: allow-log-and-swallow -- single-flight redis release is best-effort; lock will expire via TTL if release fails
                _LOGGER.debug("single-flight redis release error: %s", exc)


def jittered_ttl(base_ttl: int, pct: float = 0.1) -> int:
    """Return *base_ttl* with uniform jitter in ``[-pct, +pct]``.

    Minimum returned value is 1 second.
    """
    if base_ttl <= 0:
        return 1
    pct = max(0.0, min(1.0, pct))
    if pct == 0.0:
        return int(base_ttl)
    delta = base_ttl * random.uniform(-pct, pct)
    result = int(round(base_ttl + delta))
    return max(1, result)


__all__ = ["acquire_single_flight", "jittered_ttl"]
