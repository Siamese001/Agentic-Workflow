"""Async conductor coordinating bounded, reproducible execution."""
from __future__ import annotations

import asyncio
import hashlib
import random
from typing import Awaitable, Callable, List, Sequence, Tuple, TypeVar

T = TypeVar("T")


class Conductor:
    """Coordinate async tasks with deterministic ordering and IDs."""

    def __init__(self, concurrency: int = 3, seed: int = 7) -> None:
        if concurrency < 1:
            raise ValueError("concurrency must be >= 1")
        self._concurrency = concurrency
        self._seed = seed
        self._rng = random.Random(seed)
        self._id_counter = 0

    @property
    def concurrency(self) -> int:
        return self._concurrency

    def reset(self) -> None:
        """Reset deterministic state for repeatable replays."""

        self._rng.seed(self._seed)
        self._id_counter = 0

    def make_artifact_id(self, scope: str, company_id: str | None = None) -> str:
        """Return a deterministic artifact identifier."""

        self._id_counter += 1
        digest_input = f"{self._seed}|{scope}|{company_id or ''}|{self._id_counter}"
        digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
        return f"ev-{digest[:12]}"

    def _latency_delay(self, latency_ms: int) -> float:
        """Scale latency into a minimal async sleep for ordering."""

        jitter = self._rng.random() * 0.002
        return min(0.05, latency_ms / 1000.0 * 0.01) + jitter

    async def _execute_async(
        self, coroutine_factories: Sequence[Callable[[], Awaitable[Tuple[int, T]]]]
    ) -> List[T]:
        sem = asyncio.Semaphore(self._concurrency)
        results: List[Tuple[int, T]] = []

        async def _run(idx: int, factory: Callable[[], Awaitable[Tuple[int, T]]]) -> None:
            async with sem:
                value = await factory()
                results.append(value)

        tasks = [asyncio.create_task(_run(i, factory)) for i, factory in enumerate(coroutine_factories)]
        if tasks:
            await asyncio.wait(tasks)
        results.sort(key=lambda item: item[0])
        return results

    def run(self, coroutine_factories: Sequence[Callable[[], Awaitable[Tuple[int, T]]]]) -> List[Tuple[int, T]]:
        """Execute factories synchronously, returning results in input order."""

        if not coroutine_factories:
            return []
        return asyncio.run(self._execute_async(coroutine_factories))

    def wrap_tool_call(
        self,
        idx: int,
        call: Callable[[], Tuple[T, int]],
        after: Callable[[T], None] | None = None,
    ) -> Callable[[], Awaitable[Tuple[int, T]]]:
        """Return a coroutine factory executing ``call`` under the semaphore."""

        async def _invoke() -> Tuple[int, T]:
            result, latency_ms = call()
            await asyncio.sleep(self._latency_delay(latency_ms))
            if after:
                after(result)
            return idx, result

        return _invoke
