from __future__ import annotations

"""Rate limiting implementations for API throttling.

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import time
from dataclasses import dataclass, field


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after_s: float = 0.0):
        super().__init__(message)
        self.retry_after_s = retry_after_s


@dataclass
class TokenBucket:
    """Token bucket rate limiter.

    Allows bursts up to capacity, refilling at a constant rate.

    Attributes:
        capacity: Maximum number of tokens
        refill_rate: Tokens added per second
        tokens: Current token count
        last_refill: Timestamp of last refill
    """

    capacity: float
    refill_rate: float
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self) -> None:
        self.tokens = self.capacity
        self.last_refill = time.time()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def acquire(self, tokens: float = 1.0) -> bool:
        """Attempt to acquire tokens.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens acquired, False otherwise
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def wait_time(self, tokens: float = 1.0) -> float:
        """Calculate wait time until tokens available.

        Args:
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


@dataclass
class FixedWindow:
    """Fixed window rate limiter.

    Allows a fixed number of requests per time window.

    Attributes:
        max_requests: Maximum requests per window
        window_s: Window duration in seconds
        request_count: Current request count
        window_start: Start of current window
    """

    max_requests: int
    window_s: float
    request_count: int = 0
    window_start: float = field(default_factory=time.time)

    def _reset_if_needed(self) -> None:
        """Reset window if expired."""
        now = time.time()

        if now - self.window_start >= self.window_s:
            self.request_count = 0
            self.window_start = now

    def acquire(self) -> bool:
        """Attempt to acquire a request slot.

        Returns:
            True if request allowed, False otherwise
        """
        self._reset_if_needed()

        if self.request_count < self.max_requests:
            self.request_count += 1
            return True

        return False

    def wait_time(self) -> float:
        """Calculate wait time until next window.

        Returns:
            Wait time in seconds
        """
        self._reset_if_needed()

        if self.request_count < self.max_requests:
            return 0.0

        now = time.time()
        return self.window_s - (now - self.window_start)


class RateLimiter:
    """Unified rate limiter with multiple strategies.

    Manages rate limits for different services/endpoints.
    """

    def __init__(self):
        self._limiters: dict[str, TokenBucket | FixedWindow] = {}

    def add_token_bucket(
        self,
        name: str,
        capacity: float,
        refill_rate: float,
    ) -> None:
        """Add a token bucket limiter.

        Args:
            name: Unique identifier
            capacity: Maximum tokens
            refill_rate: Tokens per second
        """
        self._limiters[name] = TokenBucket(
            capacity=capacity,
            refill_rate=refill_rate,
        )

    def add_fixed_window(
        self,
        name: str,
        max_requests: int,
        window_s: float,
    ) -> None:
        """Add a fixed window limiter.

        Args:
            name: Unique identifier
            max_requests: Max requests per window
            window_s: Window duration in seconds
        """
        self._limiters[name] = FixedWindow(
            max_requests=max_requests,
            window_s=window_s,
        )

    def acquire(self, name: str, tokens: float = 1.0) -> None:
        """Acquire from a rate limiter, blocking if needed.

        Args:
            name: Limiter identifier
            tokens: Tokens to acquire (for token bucket)

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        limiter = self._limiters.get(name)

        if not limiter:
            return

        if isinstance(limiter, TokenBucket):
            if not limiter.acquire(tokens):
                wait_time = limiter.wait_time(tokens)
                raise RateLimitExceeded(
                    f"Rate limit exceeded for '{name}'",
                    retry_after_s=wait_time,
                )

        elif isinstance(limiter, FixedWindow):
            if not limiter.acquire():
                wait_time = limiter.wait_time()
                raise RateLimitExceeded(
                    f"Rate limit exceeded for '{name}'",
                    retry_after_s=wait_time,
                )

    def check(self, name: str, tokens: float = 1.0) -> bool:
        """Check if request would be allowed without acquiring.

        Args:
            name: Limiter identifier
            tokens: Tokens to check (for token bucket)

        Returns:
            True if request would be allowed
        """
        limiter = self._limiters.get(name)

        if not limiter:
            return True

        if isinstance(limiter, TokenBucket):
            limiter._refill()
            return limiter.tokens >= tokens

        elif isinstance(limiter, FixedWindow):
            limiter._reset_if_needed()
            return limiter.request_count < limiter.max_requests

        return True
