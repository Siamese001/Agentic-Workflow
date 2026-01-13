import time
import logging
from typing import Dict, Optional, Any, Tuple
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
        self._bucket_state: Dict[str, Dict[str, float]] = {}
        
        # Default limits if not defined in child class
        if not hasattr(self, "_rate_limits"):
            self._rate_limits: Dict[str, Dict[str, float]] = {}
            
        self._rl_logger = logging.getLogger(self.__class__.__name__)

    def configure_rate_limit(self, key: str, rate: int, per: int = 60, burst: Optional[int] = None):
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
            "burst": float(burst if burst is not None else rate)
        }
        self._rl_logger.debug(f"Rate limit configured for '{key}': {rate}/{per}s (burst={burst})")

    def _get_tokens(self, key: str) -> float:
        """Internal: Calculate current tokens for a key based on time elapsed."""
        config = self._rate_limits.get(key)
        if not config:
            return float('inf')  # Unlimited if not configured

        now = time.time()
        state = self._bucket_state.get(key, {"tokens": config["burst"], "last_updated": now})
        
        # Calculate refill
        elapsed = now - state["last_updated"]
        refill_rate = config["rate"] / config["per"]
        new_tokens = elapsed * refill_rate
        
        # Update state
        current_tokens = min(config["burst"], state["tokens"] + new_tokens)
        
        # Update internal state with new values
        self._bucket_state[key] = {
            "tokens": current_tokens,
            "last_updated": now
        }
        return current_tokens

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

        current_tokens = self._get_tokens(key)
        
        if current_tokens >= consume:
            # Consume tokens
            self._bucket_state[key]["tokens"] -= consume
            return True
        else:
            # Calculate wait time
            config = self._rate_limits[key]
            refill_rate = config["rate"] / config["per"]
            needed = consume - current_tokens
            wait_time = needed / refill_rate
            
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
