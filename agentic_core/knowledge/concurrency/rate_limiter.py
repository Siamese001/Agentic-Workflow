"""Rate Limiter.

Token bucket rate limiting for requests.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    requests_per_second: float = 10.0
    burst_size: int = 20
    cooldown_seconds: float = 1.0


class RateLimiter:
    """Token bucket rate limiter.

    The RateLimiter provides per-client rate limiting using
    token bucket algorithm.
    """

    def __init__(self, config: RateLimitConfig | None = None):
        """Initialize the rate limiter.

        Args:
            config: Optional configuration
        """
        self.config = config or RateLimitConfig()

        # Per-client token buckets
        self._buckets: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "tokens": self.config.burst_size,
                "last_update": time.time(),
            },
        )

        log.info(f"RateLimiter initialized (rps={self.config.requests_per_second})")

    def is_allowed(self, client_id: str, cost: int = 1) -> bool:
        """Check if request is allowed.

        Args:
            client_id: Client identifier
            cost: Token cost for this request

        Returns:
            True if request is allowed
        """
        trace_id = f"rate_{client_id}_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "RateLimiter.is_allowed",
        )

        bucket = self._buckets[client_id]
        now = time.time()

        # Refill tokens
        elapsed = now - bucket["last_update"]
        tokens_to_add = elapsed * self.config.requests_per_second

        bucket["tokens"] = min(
            bucket["tokens"] + tokens_to_add,
            self.config.burst_size,
        )
        bucket["last_update"] = now

        # Check if allowed
        if bucket["tokens"] >= cost:
            bucket["tokens"] -= cost
            return True

        _emit_records_telemetry_event(
            trace_id,
            "RateLimiter",
            f"blocked_{client_id}",
        )

        return False

    def get_wait_time(self, client_id: str, cost: int = 1) -> float:
        """Get time to wait for tokens.

        Args:
            client_id: Client identifier
            cost: Token cost

        Returns:
            Seconds to wait (0 if tokens available)
        """
        bucket = self._buckets[client_id]
        now = time.time()

        # Refill tokens
        elapsed = now - bucket["last_update"]
        tokens_to_add = elapsed * self.config.requests_per_second

        bucket["tokens"] = min(
            bucket["tokens"] + tokens_to_add,
            self.config.burst_size,
        )
        bucket["last_update"] = now

        # Calculate wait time
        if bucket["tokens"] >= cost:
            return 0.0

        needed = cost - bucket["tokens"]
        return needed / self.config.requests_per_second

    def get_stats(self, client_id: str | None = None) -> dict[str, Any]:
        """Get rate limiter statistics.

        Args:
            client_id: Optional client to get stats for

        Returns:
            Dictionary with stats
        """
        if client_id:
            bucket = self._buckets.get(client_id, {"tokens": 0, "last_update": time.time()})
            return {
                "client_id": client_id,
                "available_tokens": bucket["tokens"],
                "burst_size": self.config.burst_size,
                "requests_per_second": self.config.requests_per_second,
            }

        return {
            "total_clients": len(self._buckets),
            "config": {
                "requests_per_second": self.config.requests_per_second,
                "burst_size": self.config.burst_size,
            },
        }


# Global instance
_global_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter()
    return _global_limiter
