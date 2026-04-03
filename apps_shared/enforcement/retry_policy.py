"""Retry Policy - Stub implementation for test compatibility."""
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0


class RetryExecutor:
    """Stub retry executor."""

    def __init__(self):
        self._policies: dict[str, RetryConfig] = {}

    def register_policy(self, name: str, config: RetryConfig) -> None:
        """Register a retry policy."""
        self._policies[name] = config

    async def execute(self, func: Callable, *args, policy: str = "default", **kwargs) -> Any:
        """Execute function with retry policy."""
        config = self._policies.get(policy, RetryConfig())
        last_error = None

        for attempt in range(config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < config.max_attempts - 1:
                    import asyncio
                    await asyncio.sleep(config.base_delay)

        if last_error:
            raise last_error


_executor: RetryExecutor | None = None


async def get_retry_executor() -> RetryExecutor:
    """Get global retry executor."""
    global _executor
    if _executor is None:
        _executor = RetryExecutor()
    return _executor


__all__ = ["RetryConfig", "RetryExecutor", "get_retry_executor"]
