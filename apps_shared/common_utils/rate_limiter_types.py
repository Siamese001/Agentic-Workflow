"""Rate Limiter - Protection against API abuse and flooding.

This module implements rate limiting with multiple strategies including
token bucket, sliding window, and fixed window to protect the system
from abuse while ensuring fair usage.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, identifier: str, limit: int, window: int, retry_after: float):
        """Initialize rate limit exceeded error.

        Args:
            identifier: Client identifier
            limit: Request limit
            window: Time window in seconds
            retry_after: Seconds until next request allowed
        """
        super().__init__(
            f"Rate limit exceeded for {identifier}: {limit} requests per {window}s. "
            f"Retry after {retry_after:.1f}s",
        )
        self.identifier = identifier
        self.limit = limit
        self.window = window
        self.retry_after = retry_after


@dataclass
class RateLimitConfig:
    """configuration for rate limiting."""

    limit: int  # Number of requests
    window: int  # Time window in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    burst_size: int | None = None  # For token bucket
    cleanup_interval: int = 3600  # Cleanup old entries every hour

    def __post_init__(self):
        """Post-initialization validation."""
        if self.burst_size is None:
            self.burst_size = self.limit * 2  # Default burst to 2x limit


@dataclass
class ClientState:
    """State for a rate-limited client."""

    identifier: str
    request_count: int = 0
    window_start: float = field(default_factory=time.time)
    last_request: float = field(default_factory=time.time)
    tokens: float = 0.0  # For token bucket
    last_refill: float = field(default_factory=time.time)

    def reset_window(self) -> None:
        """Reset the time window."""
        self.window_start = time.time()
        self.request_count = 0


class RateLimiter(ABC):
    """Abstract base for rate limiters."""

    @abstractmethod
    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            identifier: Client identifier (IP, API key, etc.)

        Returns:
            True if request is allowed
        """
        pass

    @abstractmethod
    async def check_limit(self, identifier: str) -> tuple[bool, float]:
        """Check rate limit and get retry after.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        pass


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter."""

    def __init__(self, config: RateLimitConfig):
        """Initialize token bucket rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.clients: dict[str, ClientState] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None

        # Statistics
        self._stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "active_clients": 0,
        }

        # Start cleanup task
        self._start_cleanup()

        logger.debug(f"Initialized TokenBucketRateLimiter: {config.limit}/{config.window}s")

    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            identifier: Client identifier

        Returns:
            True if request is allowed
        """
        allowed, _ = await self.check_limit(identifier)
        return allowed

    async def check_limit(self, identifier: str) -> tuple[bool, float]:
        """Check rate limit and get retry after.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        async with self._lock:
            now = time.time()

            # Get or create client state
            if identifier not in self.clients:
                self.clients[identifier] = ClientState(
                    identifier=identifier,
                    tokens=float(self.config.burst_size),
                )

            client = self.clients[identifier]

            # Refill tokens based on time elapsed
            time_elapsed = now - client.last_refill
            tokens_to_add = time_elapsed * (self.config.limit / self.config.window)
            client.tokens = min(client.tokens + tokens_to_add, self.config.burst_size)
            client.last_refill = now

            # Check if request is allowed
            self._stats["total_requests"] += 1

            if client.tokens >= 1:
                # Allow request
                client.tokens -= 1
                client.last_request = now
                self._stats["allowed_requests"] += 1
                return True, 0.0
            else:
                # Block request
                self._stats["blocked_requests"] += 1

                # Calculate retry after
                retry_after = (1 - client.tokens) * (self.config.window / self.config.limit)

                return False, retry_after

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats["active_clients"] = len(self.clients)

        if stats["total_requests"] > 0:
            stats["allow_rate"] = stats["allowed_requests"] / stats["total_requests"]
            stats["block_rate"] = stats["blocked_requests"] / stats["total_requests"]
        else:
            stats["allow_rate"] = 0.0
            stats["block_rate"] = 0.0

        return stats

    async def cleanup(self) -> int:
        """Clean up inactive clients.

        Returns:
            Number of clients cleaned up
        """
        async with self._lock:
            now = time.time()
            cutoff = now - self.config.cleanup_interval

            inactive_clients = [
                identifier for identifier, client in self.clients.items() if client.last_request < cutoff
            ]

            for identifier in inactive_clients:
                del self.clients[identifier]

            if inactive_clients:
                logger.debug(f"Cleaned up {len(inactive_clients)} inactive rate limit clients")

            return len(inactive_clients)

    def _start_cleanup(self) -> None:
        """Start the cleanup task."""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.cleanup_interval)
                    await self.cleanup()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Rate limiter cleanup error: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def stop(self) -> None:
        """Stop the rate limiter."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window rate limiter."""

    def __init__(self, config: RateLimitConfig):
        """Initialize sliding window rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.clients: dict[str, list[float]] = {}  # identifier -> list of request timestamps
        self._lock = asyncio.Lock()

        # Statistics
        self._stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "active_clients": 0,
        }

        logger.debug(f"Initialized SlidingWindowRateLimiter: {config.limit}/{config.window}s")

    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            identifier: Client identifier

        Returns:
            True if request is allowed
        """
        allowed, _ = await self.check_limit(identifier)
        return allowed

    async def check_limit(self, identifier: str) -> tuple[bool, float]:
        """Check rate limit and get retry after.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        async with self._lock:
            now = time.time()
            window_start = now - self.config.window

            # Get or create client request list
            if identifier not in self.clients:
                self.clients[identifier] = []

            requests = self.clients[identifier]

            # Remove old requests outside window
            requests[:] = [req_time for req_time in requests if req_time > window_start]

            # Check if under limit
            self._stats["total_requests"] += 1

            if len(requests) < self.config.limit:
                # Allow request
                requests.append(now)
                self._stats["allowed_requests"] += 1
                return True, 0.0
            else:
                # Block request
                self._stats["blocked_requests"] += 1

                # Calculate retry after (oldest request + window - now)
                oldest_request = min(requests)
                retry_after = (oldest_request + self.config.window) - now

                return False, max(0, retry_after)

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats["active_clients"] = len(self.clients)

        if stats["total_requests"] > 0:
            stats["allow_rate"] = stats["allowed_requests"] / stats["total_requests"]
            stats["block_rate"] = stats["blocked_requests"] / stats["total_requests"]
        else:
            stats["allow_rate"] = 0.0
            stats["block_rate"] = 0.0

        return stats


class RateLimitManager:
    """Manages multiple rate limiters."""

    def __init__(self):
        """Initialize rate limit manager."""
        self.limiters: dict[str, RateLimiter] = {}
        self._lock = asyncio.Lock()

        logger.info("Initialized RateLimitManager")

    async def add_limiter(self, name: str, config: RateLimitConfig) -> RateLimiter:
        """Add a rate limiter.

        Args:
            name: Limiter name
            config: Rate limit configuration

        Returns:
            Created rate limiter
        """
        async with self._lock:
            if name in self.limiters:
                raise ValueError(f"Rate limiter '{name}' already exists")

            # Create appropriate limiter based on strategy
            if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                limiter = TokenBucketRateLimiter(config)
            elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                limiter = SlidingWindowRateLimiter(config)
            else:
                raise ValueError(f"Unsupported rate limit strategy: {config.strategy}")

            self.limiters[name] = limiter
            logger.info(f"Added rate limiter '{name}' with {config.limit}/{config.window}s")

            return limiter

    async def check_limit(self, limiter_name: str, identifier: str) -> tuple[bool, float]:
        """Check rate limit.

        Args:
            limiter_name: Name of rate limiter
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        limiter = self.limiters.get(limiter_name)
        if not limiter:
            raise ValueError(f"Rate limiter '{limiter_name}' not found")

        return await limiter.check_limit(identifier)

    async def is_allowed(self, limiter_name: str, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            limiter_name: Name of rate limiter
            identifier: Client identifier

        Returns:
            True if allowed
        """
        limiter = self.limiters.get(limiter_name)
        if not limiter:
            raise ValueError(f"Rate limiter '{limiter_name}' not found")

        return await limiter.is_allowed(identifier)

    def get_limiter(self, name: str) -> RateLimiter | None:
        """Get rate limiter by name.

        Args:
            name: Limiter name

        Returns:
            Rate limiter if found
        """
        return self.limiters.get(name)

    def list_limiters(self) -> list[str]:
        """List all rate limiter names.

        Returns:
            List of names
        """
        return list(self.limiters.keys())

    async def remove_limiter(self, name: str) -> bool:
        """Remove a rate limiter.

        Args:
            name: Limiter name

        Returns:
            True if removed
        """
        async with self._lock:
            if name in self.limiters:
                limiter = self.limiters[name]

                # Stop cleanup tasks if applicable
                if hasattr(limiter, "stop"):
                    await limiter.stop()

                del self.limiters[name]
                logger.info(f"Removed rate limiter '{name}'")
                return True

            return False

    async def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all limiters.

        Returns:
            Statistics dictionary
        """
        return {name: limiter.get_stats() for name, limiter in self.limiters.items()}


# Global rate limit manager
_rate_manager: RateLimitManager | None = None
_manager_lock = asyncio.Lock()


async def get_rate_limit_manager() -> RateLimitManager:
    """Get global rate limit manager.

    Returns:
        RateLimitManager instance
    """
    global _rate_manager
    async with _manager_lock:
        if _rate_manager is None:
            _rate_manager = RateLimitManager()
    return _rate_manager


# Decorators for rate limiting
def rate_limit(limiter_name: str, identifier_extractor: Callable | None = None):
    """Decorator to add rate limiting to functions.

    Args:
        limiter_name: Name of rate limiter
        identifier_extractor: Function to extract identifier from args

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            manager = await get_rate_limit_manager()

            # Extract identifier
            if identifier_extractor:
                identifier = identifier_extractor(*args, **kwargs)
            else:
                # Default: use first argument or 'default'
                identifier = str(args[0]) if args else "default"

            # Check rate limit
            allowed, retry_after = await manager.check_limit(limiter_name, identifier)

            if not allowed:
                raise RateLimitExceeded(
                    identifier,
                    manager.get_limiter(limiter_name).config.limit,
                    manager.get_limiter(limiter_name).config.window,
                    retry_after,
                )

            # Execute function
            return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in thread pool
            async def async_func():
                return func(*args, **kwargs)

            return asyncio.run(async_func())

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Predefined configurations
RATE_LIMIT_CONFIGS = {
    "api_default": RateLimitConfig(limit=100, window=60, strategy=RateLimitStrategy.TOKEN_BUCKET),
    "api_heavy": RateLimitConfig(
        limit=1000,
        window=60,
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        burst_size=2000,
    ),
    "api_strict": RateLimitConfig(limit=10, window=60, strategy=RateLimitStrategy.SLIDING_WINDOW),
    "upload": RateLimitConfig(limit=5, window=60, strategy=RateLimitStrategy.TOKEN_BUCKET),
}


# Initialize default limiters
async def init_default_rate_limits() -> None:
    """Initialize default rate limiters."""
    manager = await get_rate_limit_manager()

    for name, config in RATE_LIMIT_CONFIGS.items():
        await manager.add_limiter(name, config)

    logger.info("Initialized default rate limiters")
