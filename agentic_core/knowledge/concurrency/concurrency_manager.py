"""Concurrency Manager.

Token bucket and semaphore-based concurrency control.
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class ConcurrencyConfig:
    """Configuration for concurrency control."""
    max_concurrent: int = 10
    token_rate: float = 1.0  # tokens per second
    token_bucket_size: int = 10


class ConcurrencyManager:
    """Manages concurrency with token bucket and semaphore.

    The ConcurrencyManager provides both semaphore-based concurrency
    limiting and token bucket rate limiting.
    """

    def __init__(self, config: ConcurrencyConfig | None = None):
        """Initialize the concurrency manager.

        Args:
            config: Optional configuration
        """
        self.config = config or ConcurrencyConfig()

        # Semaphore for concurrent limiting
        self._semaphore = threading.Semaphore(self.config.max_concurrent)

        # Token bucket state
        self._tokens = self.config.token_bucket_size
        self._last_update = time.time()
        self._token_lock = threading.Lock()

        log.info(f"ConcurrencyManager initialized (max_concurrent={self.config.max_concurrent})")

    def acquire(self, timeout: float | None = None) -> bool:
        """Acquire a concurrency slot.

        Args:
            timeout: Maximum time to wait

        Returns:
            True if acquired
        """
        trace_id = f"concurrency_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "ConcurrencyManager.acquire"
        )

        return self._semaphore.acquire(timeout=timeout)

    def release(self) -> None:
        """Release a concurrency slot."""
        self._semaphore.release()

    def consume_token(self, count: int = 1, timeout: float = 1.0) -> bool:
        """Consume tokens from the bucket.

        Args:
            count: Number of tokens to consume
            timeout: Maximum time to wait for tokens

        Returns:
            True if tokens consumed
        """
        start = time.time()

        while time.time() - start < timeout:
            with self._token_lock:
                self._refill_tokens()

                if self._tokens >= count:
                    self._tokens -= count
                    return True

            time.sleep(0.01)  # Small sleep to avoid busy waiting

        return False

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_update

        # Calculate tokens to add
        tokens_to_add = elapsed * self.config.token_rate

        self._tokens = min(
            self._tokens + tokens_to_add,
            self.config.token_bucket_size
        )

        self._last_update = now

    def get_stats(self) -> dict[str, Any]:
        """Get concurrency statistics.

        Returns:
            Dictionary with stats
        """
        with self._token_lock:
            self._refill_tokens()

            return {
                "available_tokens": self._tokens,
                "max_concurrent": self.config.max_concurrent,
                "available_slots": self._semaphore._value,  # type: ignore
            }


# Global instance
_global_manager: ConcurrencyManager | None = None


def get_concurrency_manager() -> ConcurrencyManager:
    """Get or create the global concurrency manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = ConcurrencyManager()
    return _global_manager
