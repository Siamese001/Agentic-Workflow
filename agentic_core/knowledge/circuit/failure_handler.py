"""Failure Handler.

Retry strategies, exponential backoff, and failure logging.
"""

import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategies."""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class RetryConfig:
    """Configuration for retries."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retryable_exceptions: list[type[Exception]] = field(default_factory=lambda: [Exception])
    on_retry: Callable[[int, Exception], None] | None = None


class FailureHandler:
    """Handles failures with retry logic.

    The FailureHandler provides retry strategies with exponential
    backoff and failure logging for resilient operations.
    """

    def __init__(self, config: RetryConfig | None = None):
        """Initialize the failure handler.

        Args:
            config: Optional retry configuration
        """
        self.config = config or RetryConfig()
        self._failure_log: list[dict[str, Any]] = []

        log.info(f"FailureHandler initialized (max_retries={self.config.max_retries})")

    def execute_with_retry(
        self,
        fn: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with retry logic.

        Args:
            fn: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries exhausted
        """
        trace_id = f"retry_{hash(str(fn)) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "FailureHandler.execute_with_retry"
        )

        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = fn(*args, **kwargs)

                if attempt > 0:
                    log.info(f"Function succeeded on attempt {attempt + 1}")

                return result

            except Exception as e:
                last_exception = e

                # Check if exception is retryable
                if not self._is_retryable(e):
                    log.warning(f"Non-retryable exception: {e}")
                    raise

                # Log failure
                self._log_failure(attempt, e)

                # Don't retry on last attempt
                if attempt >= self.config.max_retries:
                    break

                # Calculate delay
                delay = self._calculate_delay(attempt)

                # Call retry callback if provided
                if self.config.on_retry:
                    self.config.on_retry(attempt + 1, e)

                log.debug(f"Retry attempt {attempt + 1} after {delay:.2f}s delay")
                time.sleep(delay)

        # All retries exhausted
        _emit_records_telemetry_event(
            "retry_exhausted",
            f"max_retries_{self.config.max_retries}"
        )

        raise last_exception

    def _is_retryable(self, exception: Exception) -> bool:
        """Check if exception type is retryable."""
        return any(isinstance(exception, exc_type) for exc_type in self.config.retryable_exceptions)

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay."""
        if self.config.strategy == RetryStrategy.FIXED:
            return self.config.base_delay

        elif self.config.strategy == RetryStrategy.LINEAR:
            return self.config.base_delay * (attempt + 1)

        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (2 ** attempt)
            # Add jitter
            jitter = random.uniform(0, delay * 0.1)
            return min(delay + jitter, self.config.max_delay)

        return self.config.base_delay

    def _log_failure(self, attempt: int, exception: Exception) -> None:
        """Log a failure."""
        failure_entry = {
            "timestamp": time.time(),
            "attempt": attempt,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        }
        self._failure_log.append(failure_entry)

    def get_failure_log(self) -> list[dict[str, Any]]:
        """Get the failure log.

        Returns:
            List of failure entries
        """
        return self._failure_log.copy()

    def clear_failure_log(self) -> int:
        """Clear the failure log.

        Returns:
            Number of entries cleared
        """
        count = len(self._failure_log)
        self._failure_log.clear()
        return count


# Global instance
_global_handler: FailureHandler | None = None


def get_failure_handler() -> FailureHandler:
    """Get or create the global failure handler."""
    global _global_handler
    if _global_handler is None:
        _global_handler = FailureHandler()
    return _global_handler
