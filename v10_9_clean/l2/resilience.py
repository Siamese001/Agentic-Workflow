from __future__ import annotations

import asyncio
import random
import time
from typing import Callable, Awaitable, Optional, Tuple, TypeVar

from ..shared.exceptions import ToolExecutionError, ToolTimeoutError, ControlFlowHalt, ControlFlowAbort

T = TypeVar("T")


def _backoff(base: float, attempt: int, jitter: float) -> float:
    exp = base * (2 ** attempt)
    if jitter > 0:
        exp += random.uniform(0, jitter)
    return exp


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 0.1,
    jitter: float = 0.05,
    timeout: float = 30.0,
    retry_on: Tuple[type, ...] = (Exception,),  # noqa: BLE001
) -> T:
    last_exc: Optional[Exception] = None

    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(fn(), timeout=timeout)
        except retry_on as exc:
            last_exc = exc

            if isinstance(exc, (ControlFlowHalt, ControlFlowAbort)):
                raise

            if attempt < attempts - 1:
                await asyncio.sleep(_backoff(base_delay, attempt, jitter))
            else:
                raise

    raise last_exc or RuntimeError("retry_async failed unexpectedly")


class CircuitBreaker:
    def __init__(self, threshold: int = 3, cooldown: float = 5.0) -> None:
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = 0
        self.state = "CLOSED"
        self.opened_at: Optional[float] = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold and self.state == "CLOSED":
            self.state = "OPEN"
            self.opened_at = time.monotonic()

    def record_success(self) -> None:
        self.failures = 0
        self.state = "CLOSED"
        self.opened_at = None

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN" and self.opened_at is not None:
            if time.monotonic() - self.opened_at >= self.cooldown:
                self.state = "HALF"
                return True
        return self.state == "HALF"


async def safe_execute(
    fn: Callable[[], Awaitable[T]],
    *,
    circuit: Optional[CircuitBreaker] = None,
    attempts: int = 3,
    base_delay: float = 0.1,
    jitter: float = 0.05,
    timeout: float = 30.0,
) -> T:
    if circuit and not circuit.can_execute():
        raise ToolExecutionError("Circuit breaker OPEN — execution blocked.")

    try:
        result = await retry_async(
            fn,
            attempts=attempts,
            base_delay=base_delay,
            jitter=jitter,
            timeout=timeout,
        )
        if circuit:
            circuit.record_success()
        return result

    except asyncio.TimeoutError as exc:
        if circuit:
            circuit.record_failure()
        raise ToolTimeoutError(str(exc)) from exc

    except Exception as exc:  # noqa: BLE001
        if circuit:
            circuit.record_failure()
        raise ToolExecutionError(str(exc)) from exc
