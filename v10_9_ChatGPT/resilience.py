"""Resilience utilities such as circuit breakers and timeouts."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable


class CircuitBreaker:
    def __init__(self, threshold: int = 3) -> None:
        self.threshold = threshold
        self.failures = 0

    async def run(self, func: Callable[[], Awaitable[Any]]) -> Any:
        if self.failures >= self.threshold:
            raise RuntimeError("circuit open")
        try:
            result = await func()
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            raise


def timeout(seconds: float):
    def decorator(fn: Callable[..., Awaitable[Any]]):
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await asyncio.wait_for(fn(*args, **kwargs), timeout=seconds)

        return wrapper

    return decorator


@asynccontextmanager
async def mcp_lock():
    lock = asyncio.Lock()
    async with lock:
        yield


async def wrap_mcp(fn: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
    async with mcp_lock():
        return await fn(*args, **kwargs)


__all__ = ["CircuitBreaker", "timeout", "wrap_mcp", "mcp_lock"]
