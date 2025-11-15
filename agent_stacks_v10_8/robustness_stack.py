"""Layer-5 resilience stack that centralizes retry logic."""

from __future__ import annotations

import asyncio
import random
from typing import Any, Awaitable, Callable, Dict, Optional


class RobustnessStack:
    """Implements workflow-wide retry and backoff heuristics."""

    def __init__(
        self,
        context: Any,
        debug_mode: bool = False,
        *,
        max_retries: Optional[int] = None,
        base_backoff: Optional[float] = None,
        max_backoff: Optional[float] = None,
    ) -> None:
        self.context = context
        self.debug_mode = debug_mode
        config = getattr(context, "config", None)
        stack_config = getattr(config, "agent_stacks", None) if config else None
        perf_config = getattr(config, "performance_config", None) if config else None

        self.max_retries = (
            max_retries
            if max_retries is not None
            else getattr(stack_config, "max_local_retries", 1)
        )
        self.base_backoff = (
            base_backoff
            if base_backoff is not None
            else getattr(perf_config, "node_retry_backoff_seconds", 0.5)
        )
        self.max_backoff = (
            max_backoff
            if max_backoff is not None
            else getattr(perf_config, "node_retry_max_backoff_seconds", 4.0)
        )
        self._failure_counts: Dict[str, int] = {}

    async def run_with_resilience(
        self, stage: str, operation: Callable[[], Awaitable[Any]]
    ) -> Any:
        """Run an async operation with centralized retry controls."""

        while True:
            try:
                result = await operation()
            except Exception:
                if not self.should_retry(stage, "operation_failed"):
                    raise
                await asyncio.sleep(self._compute_backoff(stage))
                continue
            else:
                self.reset(stage)
                return result

    def should_retry(self, stage: str, error: Optional[str]) -> bool:
        """Decide whether a stage should retry after a failure."""

        failures = self._failure_counts.get(stage, 0)
        if failures >= self.max_retries:
            return False
        self._failure_counts[stage] = failures + 1
        return True

    def reset(self, stage: str) -> None:
        """Clear retry history for a stage after success."""

        self._failure_counts.pop(stage, None)

    def _compute_backoff(self, stage: str) -> float:
        attempt = self._failure_counts.get(stage, 1)
        delay = min(self.base_backoff * (2 ** max(attempt - 1, 0)), self.max_backoff)
        jitter = random.uniform(0, self.base_backoff / 2)
        return delay + jitter


__all__ = ["RobustnessStack"]

