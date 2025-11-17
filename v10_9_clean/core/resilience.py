"""
Resilience primitives for v10_9 runtime.

Provides:
  • async retry with exponential backoff + jitter
  • timeout protection
  • circuit-breaker pattern
  • safe execution wrappers for L2/L3
  • MCP / observability hooks (no-op by default)

This module has NO external side effects and performs NO logging. All behavior
is encapsulated and controlled through return values and raised exceptions.
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Awaitable, Callable, Optional, TypeVar, Tuple

from .exceptions import (
    ToolExecutionError,
    ToolTimeoutError,
    ControlFlowHalt,
    ControlFlowAbort,
)

T = TypeVar("T")


# ======================================================================
# INTERNAL HELPERS
# ======================================================================

def _compute_backoff(base: float, attempt: int, jitter: float) -> float:
    """
    Compute exponential backoff with jitter.
    """
    exp = base * (2 ** attempt)
    if jitter > 0:
        exp += random.uniform(0, jitter)
    return exp


# ======================================================================
# RETRY ENGINE
# ======================================================================

async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 0.1,
    jitter: float = 0.05,
    timeout: float = 30.0,
    retry_on: Tuple[type, ...] = (Exception,),  # noqa: BLE001
) -> T:
    """
    Execute a coroutine with retries, exponential backoff, jitter, and timeout.

    Raises the final exception if all attempts fail.
    """

    last_exc: Optional[Exception] = None

    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(fn(), timeout=timeout)

        except retry_on as exc:  # noqa: BLE001
            last_exc = exc

            # Do not retry control-flow exceptions
            if isinstance(exc, (ControlFlowHalt, ControlFlowAbort)):
                raise

            if attempt < attempts - 1:
                delay = _compute_backoff(base_delay, attempt, jitter)
                await asyncio.sleep(delay)
            else:
                # Exhausted
                raise

    # Should not reach here
    raise last_exc or RuntimeError("retry_async failed unexpectedly")


# ======================================================================
# CIRCUIT BREAKER
# ======================================================================

class CircuitBreaker:
    """
    Simple circuit-breaker for L2 tools or L3 orchestration segments.

    States:
      • CLOSED  → normal operation
      • OPEN    → calls immediately fail
      • HALF    → testing state after cooldown
    """

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
                # Move to HALF-OPEN for a test call
                self.state = "HALF"
                return True
        return self.state == "HALF"


# ======================================================================
# SAFE CALL WRAPPER (L2/L3)
# ======================================================================

async def safe_execute(
    fn: Callable[[], Awaitable[T]],
    *,
    circuit: Optional[CircuitBreaker] = None,
    attempts: int = 3,
    base_delay: float = 0.1,
    jitter: float = 0.05,
    timeout: float = 30.0,
) -> T:
    """
    Execute a coroutine with retries + circuit breaker.
    Converts generic exceptions into ToolExecutionError.
    """

    if circuit and not circuit.can_execute():
        raise ToolExecutionError("Circuit breaker OPEN – execution blocked.")

    try:
        result = await retry_async(
            fn,
            attempts=attempts,
            base_delay=base_delay,
            jitter=jitter,
            timeout=timeout,
            retry_on=(Exception,),  # exclude ControlFlow*
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


# ======================================================================
# MCP WRAPPER (NO-OP FOR NOW)
# ======================================================================

async def mcp_wrap(event_name: str, coro: Callable[[], Awaitable[T]]) -> T:
    """
    Placeholder for MCP / observability wrapping.
    Currently behaves as a pass-through using safe_execute.
    """

    return await safe_execute(coro)

