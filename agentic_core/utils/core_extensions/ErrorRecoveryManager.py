from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from .backoff import calculate_backoff_ms
from .circuit_breaker import CircuitBreakerOpenError, get_breaker

Logger = logging.getLogger(__name__)


class ErrorRecoveryManager:
    def __init__(
        self,
        *,
        max_retries: int = 3,
        base_backoff_ms: int = 200,
        jitter_ms: int = 100,
        enable_circuit_breaker: bool = True,
        backoff_strategy: str = "exponential",
    ):
        self.max_retries = max_retries
        self.base_backoff_ms = base_backoff_ms
        self.jitter_ms = jitter_ms
        self.enable_circuit_breaker = enable_circuit_breaker
        self.backoff_strategy = backoff_strategy

    async def invoke_with_retry(
        self,
        *,
        fn: Callable[[], Awaitable[Any]],
        breaker_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> Any:
        context = context or {}
        breaker = (
            get_breaker(breaker_name) if (breaker_name and self.enable_circuit_breaker) else None
        )

        last_exc: BaseException | None = None
        for attempt in range(1, self.max_retries + 1):
            if breaker and not breaker.can_execute():
                raise CircuitBreakerOpenError("Circuit breaker open", breaker.name)

            try:
                result = await fn()
                if breaker:
                    breaker.record_success()
                return result
            except Exception as e:
                last_exc = e
                if breaker:
                    breaker.record_failure()

                if attempt >= self.max_retries:
                    break

                delay_ms = calculate_backoff_ms(
                    base_backoff_ms=self.base_backoff_ms,
                    attempt=attempt,
                    jitter_ms=self.jitter_ms,
                    strategy=self.backoff_strategy,
                )
                Logger.debug(
                    f"[RECOVERY] attempt {attempt}/{self.max_retries} failed: {e} | backoff={delay_ms}ms"
                )
                await asyncio.sleep(delay_ms / 1000.0)

        if last_exc:
            raise last_exc
        raise RuntimeError("invoke_with_retry failed without exception")
