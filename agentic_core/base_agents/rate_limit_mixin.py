import asyncio
import hashlib
import json
import logging
import time
from functools import wraps


class RateLimitExceeded(Exception):
    """Raised when an operation exceeds its defined rate limit."""

    def __init__(self, key: str, wait_time: float):
        self.key = key
        self.wait_time = wait_time
        super().__init__(f"Rate limit exceeded for '{key}'. Retry in {wait_time:.2f}s")


class RateLimitMixin:
    """
    Phase 1 Critical Infrastructure: Universal Rate Limiting (Report 4.1).

    Implements a Token Bucket algorithm to control operation frequency.
    Features:
    - Per-operation limits (rate/per/burst)
    - Token bucket replenishment
    - Non-blocking checks
    - Integration with agent logging
    """

    def __init__(self, **kwargs):
        # Cooperatively call next parent in MRO
        super().__init__(**kwargs)

        # Internal state for token buckets
        # Structure: { "key": { "tokens": float, "last_updated": float } }
        self._bucket_state: dict[str, dict[str, float]] = {}

        # Default limits if not defined in child class
        if not hasattr(self, "_rate_limits"):
            self._rate_limits: dict[str, dict[str, float]] = {}

        self._violation_count: dict[str, int] = {}
        self._redis = None
        try:
            from agentic_core.L2_execution.mcp.caching_redis_mcp_client import get_redis_client

            self._redis = get_redis_client()
        except Exception:
            self._redis = None

        self._rl_logger = logging.getLogger(self.__class__.__name__)

    def _sanitize_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()[:32]

    def configure_rate_limit(self, key: str, rate: int, per: int = 60, burst: int | None = None):
        """
        Dynamically configure a rate limit for a specific operation key.

        Args:
            key: The operation identifier (e.g., 'mcp_call', 'heal')
            rate: Number of allowed operations per period
            per: Period in seconds (default 60s)
            burst: Max tokens allowed to accumulate (defaults to rate)
        """
        self._rate_limits[key] = {
            "rate": float(rate),
            "per": float(per),
            "burst": float(burst if burst is not None else rate),
        }
        self._rl_logger.debug(f"Rate limit configured for '{key}': {rate}/{per}s (burst={burst})")

    def _get_tokens(self, key: str) -> float:
        """Internal: Calculate current tokens for a key based on time elapsed."""
        config = self._rate_limits.get(key)
        if not config:
            return float("inf")  # Unlimited if not configured

        now = time.time()
        state = self._bucket_state.get(key, {"tokens": config["burst"], "last_updated": now})

        # Calculate refill
        elapsed = now - state["last_updated"]
        refill_rate = config["rate"] / config["per"]
        new_tokens = elapsed * refill_rate

        # Update state
        current_tokens = min(config["burst"], state["tokens"] + new_tokens)

        # Update internal state with new values
        self._bucket_state[key] = {"tokens": current_tokens, "last_updated": now}
        return current_tokens

    async def _load_state_from_redis(self, key: str) -> None:
        if not self._redis:
            return
        try:
            skey = self._sanitize_key(key)
            data = self._redis.get(f"rate_limit:{skey}")
            if asyncio.iscoroutine(data) or asyncio.isfuture(data):
                data = await data
            if data:
                state = json.loads(data)
                if isinstance(state, dict) and "tokens" in state and "last_updated" in state:
                    self._bucket_state[key] = state
        except Exception:
            return

    async def _save_state_to_redis(self, key: str) -> None:
        if not self._redis:
            return
        try:
            skey = self._sanitize_key(key)
            payload = json.dumps(self._bucket_state[key])
            result = self._redis.set(f"rate_limit:{skey}", payload, ex=3600)
            if asyncio.iscoroutine(result) or asyncio.isfuture(result):
                await result
        except Exception:
            return

    async def check_rate_limit(self, key: str, consume: int = 1, raise_exc: bool = True) -> bool:
        """
        Check if an operation is allowed. Consumes tokens if successful.

        Args:
            key: Operation identifier
            consume: Number of tokens to consume (default 1)
            raise_exc: If True, raises RateLimitExceeded on failure.

        Returns:
            bool: True if allowed, False if limit exceeded (and raise_exc=False)
        """
        if key not in self._rate_limits:
            return True

        if key not in self._bucket_state and self._redis:
            await self._load_state_from_redis(key)

        current_tokens = self._get_tokens(key)

        if current_tokens >= consume:
            # Consume tokens
            self._bucket_state[key]["tokens"] -= consume
            self._violation_count[key] = 0

            if self._redis:
                asyncio.create_task(self._save_state_to_redis(key))
            return True
        else:
            self._violation_count[key] = self._violation_count.get(key, 0) + 1
            # Calculate wait time
            config = self._rate_limits[key]
            refill_rate = config["rate"] / config["per"]
            needed = consume - current_tokens
            wait_time = needed / refill_rate

            if self._violation_count[key] >= 5:
                wait_time *= 1.5 ** (self._violation_count[key] - 4)
                self._rl_logger.warning(
                    f"Rate limit short-circuit: {key} - {self._violation_count[key]} violations",
                )

            msg = f"Rate limit hit for '{key}'. Allowed: {config['rate']}/{config['per']}s. Wait: {wait_time:.2f}s"

            if raise_exc:
                self._rl_logger.warning(msg)
                raise RateLimitExceeded(key, wait_time)
            else:
                self._rl_logger.debug(msg)
                return False

    @staticmethod
    def rate_limit(key: str, consume: int = 1):
        """Decorator to automatically enforce rate limits on agent methods."""

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                if isinstance(self, RateLimitMixin):
                    await self.check_rate_limit(key, consume=consume)
                return await func(self, *args, **kwargs)

            return wrapper

        return decorator
