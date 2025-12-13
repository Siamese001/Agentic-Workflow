"""Rate Limiter - Prevents DoS attacks and controls request frequency.

This module provides rate limiting with multiple strategies (sliding window,
token bucket, fixed window) to protect against abuse and ensure fair usage.
"""

import asyncio
import logging
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
import threading
import hashlib
import json

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int
    window_seconds: int
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_size: Optional[int] = None  # For token bucket
    refill_rate: Optional[float] = None  # For token bucket

class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, identifier: str, config: RateLimitConfig, retry_after: float):
        """Initialize rate limit exceeded error.

        Args:
            identifier: Identifier that was rate limited
            config: Rate limit configuration
            retry_after: Seconds until next request allowed
        """
        self.identifier = identifier
        self.config = config
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {identifier}. Retry after {retry_after:.1f}s")

class SlidingWindowLimiter:
    """Sliding window rate limiter."""

    def __init__(self, config: RateLimitConfig):
        """Initialize the sliding window limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self._windows: Dict[str, deque] = defaultdict(lambda: deque())
        self._lock = threading.Lock()

    def is_allowed(self, identifier: str) -> Tuple[bool, float]:
        """Check if request is allowed.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)

        Returns:
            Tuple of (allowed, retry_after)
        """
        now = time.time()
        window_start = now - self.config.window_seconds

        with self._lock:
            window = self._windows[identifier]

            # Remove old entries
            while window and window[0] < window_start:
                window.popleft()

            # Check if under limit
            if len(window) < self.config.max_requests:
                window.append(now)
                return True, 0.0

            # Calculate retry after
            oldest_request = window[0]
            retry_after = oldest_request + self.config.window_seconds - now

            return False, max(0, retry_after)

class TokenBucketLimiter:
    """Token bucket rate limiter."""

    def __init__(self, config: RateLimitConfig):
        """Initialize the token bucket limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.burst_size = config.burst_size or config.max_requests
        self.refill_rate = config.refill_rate or (config.max_requests / config.window_seconds)

        self._buckets: Dict[str, Tuple[float, int]] = {}  # (last_refill, tokens)
        self._lock = threading.Lock()

    def is_allowed(self, identifier: str) -> Tuple[bool, float]:
        """Check if request is allowed.

        Args:
            identifier: Unique identifier

        Returns:
            Tuple of (allowed, retry_after)
        """
        now = time.time()

        with self._lock:
            last_refill, tokens = self._buckets.get(identifier, (now, self.burst_size))

            # Refill tokens
            time_passed = now - last_refill
            tokens = min(self.burst_size, tokens + int(time_passed * self.refill_rate))

            if tokens >= 1:
                # Consume token
                tokens -= 1
                self._buckets[identifier] = (now, tokens)
                return True, 0.0
            else:
                # Calculate retry after
                retry_after = (1 - tokens) / self.refill_rate
                self._buckets[identifier] = (now, tokens)
                return False, retry_after

class FixedWindowLimiter:
    """Fixed window rate limiter."""

    def __init__(self, config: RateLimitConfig):
        """Initialize the fixed window limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self._counters: Dict[str, Tuple[int, float]] = {}  # (count, window_start)
        self._lock = threading.Lock()

    def is_allowed(self, identifier: str) -> Tuple[bool, float]:
        """Check if request is allowed.

        Args:
            identifier: Unique identifier

        Returns:
            Tuple of (allowed, retry_after)
        """
        now = time.time()
        window_start = now - (now % self.config.window_seconds)

        with self._lock:
            count, current_window_start = self._counters.get(identifier, (0, window_start))

            # Reset if new window
            if current_window_start != window_start:
                count = 0
                current_window_start = window_start

            # Check limit
            if count < self.config.max_requests:
                count += 1
                self._counters[identifier] = (count, current_window_start)
                return True, 0.0
            else:
                # Calculate retry after (end of current window)
                retry_after = current_window_start + self.config.window_seconds - now
                return False, max(0, retry_after)

class RateLimiter:
    """Main rate limiter with multiple strategies."""

    def __init__(self, name: str = "default"):
        """Initialize the rate limiter.

        Args:
            name: Limiter name for logging
        """
        self.name = name
        self._limiters: Dict[str, Tuple[RateLimitConfig, Union[SlidingWindowLimiter, TokenBucketLimiter, FixedWindowLimiter]]] = {}
        self._lock = threading.Lock()

        logger.debug(f"Initialized RateLimiter: {name}")

    def add_limit(self, limit_name: str, config: RateLimitConfig) -> None:
        """Add a rate limit rule.

        Args:
            limit_name: Name for the limit rule
            config: Rate limit configuration
        """
        with self._lock:
            # Create appropriate limiter
            if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                limiter = SlidingWindowLimiter(config)
            elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                limiter = TokenBucketLimiter(config)
            elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
                limiter = FixedWindowLimiter(config)
            else:
                raise ValueError(f"Unknown strategy: {config.strategy}")

            self._limiters[limit_name] = (config, limiter)
            logger.debug(f"Added rate limit {limit_name}: {config.max_requests}/{config.window_seconds}s")

    def check_limit(self, identifier: str, limit_name: str) -> Tuple[bool, float]:
        """Check if identifier is under rate limit.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            limit_name: Name of limit rule to check

        Returns:
            Tuple of (allowed, retry_after)

        Raises:
            ValueError: If limit_name not found
        """
        with self._lock:
            if limit_name not in self._limiters:
                raise ValueError(f"Rate limit not found: {limit_name}")

            config, limiter = self._limiters[limit_name]
            return limiter.is_allowed(identifier)

    def check_limits(self, identifier: str, limit_names: List[str]) -> Tuple[bool, float, str]:
        """Check multiple rate limits.

        Args:
            identifier: Unique identifier
            limit_names: List of limit names to check

        Returns:
            Tuple of (all_allowed, retry_after, exceeded_limit)
        """
        retry_after = 0.0
        exceeded_limit = None

        for limit_name in limit_names:
            allowed, limit_retry = self.check_limit(identifier, limit_name)

            if not allowed:
                return False, max(retry_after, limit_retry), limit_name

        return True, 0.0, None

    def assert_limit(self, identifier: str, limit_name: str) -> None:
        """Assert that identifier is under rate limit.

        Args:
            identifier: Unique identifier
            limit_name: Name of limit rule

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        allowed, retry_after = self.check_limit(identifier, limit_name)

        if not allowed:
            raise RateLimitExceeded(identifier, self._limiters[limit_name][0], retry_after)

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = {
                "name": self.name,
                "limits": {}
            }

            for limit_name, (config, _) in self._limiters.items():
                stats["limits"][limit_name] = {
                    "max_requests": config.max_requests,
                    "window_seconds": config.window_seconds,
                    "strategy": config.strategy.value
                }

            return stats

    def clear(self, identifier: Optional[str] = None) -> None:
        """Clear rate limit data.

        Args:
            identifier: Specific identifier to clear, or None for all
        """
        # Note: This is a simplified implementation
        # In practice, each limiter would need its own clear method
        logger.debug(f"Cleared rate limit data for identifier: {identifier}")

# Global rate limiter registry
_limiters: Dict[str, RateLimiter] = {}
_limiter_lock = threading.Lock()

def get_rate_limiter(name: str = "default") -> RateLimiter:
    """Get or create a rate limiter.

    Args:
        name: Limiter name

    Returns:
        RateLimiter instance
    """
    with _limiter_lock:
        if name not in _limiters:
            _limiters[name] = RateLimiter(name)
        return _limiters[name]

# Decorator for rate limiting
def rate_limit(
    limit_name: str,
    identifier_func: Optional[Callable] = None,
    limiter_name: str = "default"
):
    """Decorator to rate limit a function.

    Args:
        limit_name: Name of rate limit rule
        identifier_func: Function to extract identifier from args
        limiter_name: Name of rate limiter to use

    Returns:
        Decorated function
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            limiter = get_rate_limiter(limiter_name)

            # Extract identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                # Default to first argument or IP from context
                identifier = str(args[0]) if args else "unknown"

            # Check rate limit
            limiter.assert_limit(identifier, limit_name)

            # Execute function
            return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            limiter = get_rate_limiter(limiter_name)

            # Extract identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = str(args[0]) if args else "unknown"

            # Check rate limit
            limiter.assert_limit(identifier, limit_name)

            # Execute function
            return func(*args, **kwargs)

        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# Predefined rate limit configurations
RATE_LIMITS = {
    "hop_execution": RateLimitConfig(
        max_requests=10,
        window_seconds=60,
        strategy=RateLimitStrategy.SLIDING_WINDOW
    ),
    "llm_calls": RateLimitConfig(
        max_requests=60,
        window_seconds=60,
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        burst_size=10,
        refill_rate=1.0
    ),
    "api_requests": RateLimitConfig(
        max_requests=100,
        window_seconds=60,
        strategy=RateLimitStrategy.SLIDING_WINDOW
    ),
    "file_operations": RateLimitConfig(
        max_requests=50,
        window_seconds=60,
        strategy=RateLimitStrategy.FIXED_WINDOW
    )
}

def setup_default_limits(limiter: RateLimiter) -> None:
    """Setup default rate limits.

    Args:
        limiter: Rate limiter to configure
    """
    for name, config in RATE_LIMITS.items():
        limiter.add_limit(name, config)

    logger.info("Setup default rate limits")
