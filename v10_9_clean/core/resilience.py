"""Resilience primitives for v10_7 runtime."""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


async def retry_async(fn: Callable[[], Awaitable[T]], attempts: int = 3, delay: float = 0.1) -> T:
    """Retry a coroutine with simple backoff."""

    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(fn(), timeout=30.0)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            await asyncio.sleep(delay * (attempt + 1))
    if last_exc:
        raise last_exc
    raise RuntimeError("retry_async failed without exception")


async def mcp_wrap(event_name: str, coro: Callable[[], Awaitable[T]]) -> T:
    """Wrap coroutine execution to ensure MCP visibility."""

    return await retry_async(coro)
