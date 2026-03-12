"""
SSOT Rate Limit Mixin — Policy-Hash-Scoped Rate Limiting.

Provides rate limiting that:
  - Keys include active_policy_hash for isolation
  - Replay mode disables rate limiting entirely
  - Must not alter sovereignty token logic

Layer: L2 Execution Aid
Authority: Throttle only. No L4 mutation. No routing influence.
"""
from __future__ import annotations
import logging
import time
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger('SSOTRateLimit')

class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(self, bucket: str, limit: int, window: float):
        self.bucket = bucket
        self.limit = limit
        self.window = window
        super().__init__(f'Rate limit exceeded for {bucket}: {limit} calls per {window}s')

class SSOTRateLimitMixin:
    """Policy-hash-scoped rate limiter with replay bypass.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Rate limit keys are prefixed with policy hash.
    Under replay mode, rate limiting is completely disabled.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_rate_buckets: dict[str, list[float]] = {}

    # guardian: allow-magic-config
    def rate_check(self, bucket: str, limit: int=100, window: float=60.0) -> bool:
        """Check and record a rate-limited call.

        Parameters
        ----------
        bucket : str
            Rate limit bucket name (will be policy-hash-scoped).
        limit : int
            Maximum calls allowed within the window.
        window : float
            Time window in seconds.

        Returns
        -------
        bool
            True if the call is allowed.

        Raises
        ------
        RateLimitExceeded
            If the rate limit is exceeded (non-replay mode only).
        """
        if getattr(self, 'is_replay_mode', False):
            return True
        scoped_key = self._scoped_rate_key(bucket)
        now = time.time()
        if scoped_key not in self._ssot_rate_buckets:
            self._ssot_rate_buckets[scoped_key] = []
        cutoff = now - window
        self._ssot_rate_buckets[scoped_key] = [t for t in self._ssot_rate_buckets[scoped_key] if t > cutoff]
        if len(self._ssot_rate_buckets[scoped_key]) >= limit:
            raise RateLimitExceeded(scoped_key, limit, window)
        self._ssot_rate_buckets[scoped_key].append(now)
        return True

    # guardian: allow-magic-config
    def rate_remaining(self, bucket: str, limit: int=100, window: float=60.0) -> int:
        """Return remaining calls allowed in the current window."""
        if getattr(self, 'is_replay_mode', False):
            return limit
        scoped_key = self._scoped_rate_key(bucket)
        now = time.time()
        cutoff = now - window
        entries = self._ssot_rate_buckets.get(scoped_key, [])
        active = [t for t in entries if t > cutoff]
        return max(0, limit - len(active))

    def rate_reset(self, bucket: str) -> None:
        """Reset a rate limit bucket."""
        scoped_key = self._scoped_rate_key(bucket)
        self._ssot_rate_buckets.pop(scoped_key, None)

    def _scoped_rate_key(self, bucket: str) -> str:
        """Prefix bucket with active_policy_hash."""
        policy_hash = getattr(self, 'active_policy_hash', 'unknown')
        return f'{policy_hash}:{bucket}'
