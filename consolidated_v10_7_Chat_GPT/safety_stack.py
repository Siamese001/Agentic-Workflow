# === CONSOLIDATED FILE ===
# TIMESTAMP: 2025-11-17T16:29:33.153692Z
# TARGET: safety_stack.py
# SOURCE FILES:
# - /workspace/Agentic-Workflow/_latest_extract/agent_stacks_v/robustness_stack.py | SHA256: fcbf641e01e132996d550bf98dbf65f8f24f0c169a05bd1dd17219cdd4051a14
# - /workspace/Agentic-Workflow/_latest_extract/core_v/resilience.py | SHA256: 5839710468ab00b68074b34b1a663da6fdf3bbba172e7eeeaff4376da9ac14d3
# MERGE RULE: 10_8 overrides 10_7; namespace collisions suffixed with __srcN


# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/agent_stacks_v/robustness_stack.py (sha256=fcbf641e01e132996d550bf98dbf65f8f24f0c169a05bd1dd17219cdd4051a14) ====
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

# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/agent_stacks_v/robustness_stack.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/core_v/resilience.py (sha256=5839710468ab00b68074b34b1a663da6fdf3bbba172e7eeeaff4376da9ac14d3) ====
"""Resilience utilities and MCP wrappers for v10.7."""
from __future__ import annotations

import asyncio
import logging
from functools import wraps
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional, Tuple

from mcp import sync_context

from .exceptions import (
    CircuitBreakerOpenError,
    JSONParsingError,
    ModelAPIError,
    PydanticSchemaError,
    WorkflowError,
    WorkflowTimeoutError,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .context import WorkflowContext

logger = logging.getLogger("core_v10_7")


class CircuitBreaker:
    """Circuit breaker utility used by batch workflows."""

    def __init____src2(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")

    def record_success(self):
        self.failure_count = 0
        self.is_open = False

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            self.logger.error("Circuit breaker OPEN after %s failures", self.failure_count)

    def check(self):
        if self.is_open:
            raise CircuitBreakerOpenError(
                f"Circuit breaker open after {self.failure_count} failures"
            )


def exponential_backoff_retry(max_retries: int = 3, initial_delay: float = 1.0):
    """Decorator factory that applies exponential backoff to async node functions."""

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            total_attempts = max(1, max_retries + 1)

            for attempt in range(total_attempts):
                try:
                    return await func(*args, **kwargs)
                except (
                    ModelAPIError,
                    JSONParsingError,
                    PydanticSchemaError,
                    asyncio.TimeoutError,
                ) as exc:
                    logger.warning(
                        "Node %s failed (Attempt %s/%s): %s",
                        func.__name__,
                        attempt + 1,
                        total_attempts,
                        exc,
                    )

                    if attempt + 1 == total_attempts:
                        logger.error(
                            "Node %s failed permanently after %s attempts.",
                            func.__name__,
                            total_attempts,
                        )
                        raise

                    sleep_time = delay * (2 ** attempt)
                    if sleep_time > 0:
                        logger.info(
                            "Retrying %s in %.2fs...",
                            func.__name__,
                            sleep_time,
                        )
                        await asyncio.sleep(sleep_time)

            raise WorkflowError(f"Node {func.__name__} failed after max retries")

        return wrapper

    return decorator


def async_timeout(seconds: int):
    """Decorator factory that enforces a timeout on async nodes."""

    def decorator__src2(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=float(seconds))
            except asyncio.TimeoutError as exc:
                raise WorkflowTimeoutError(
                    f"Node {func.__name__} timed out after {seconds}s"
                ) from exc

        return wrapper

    return decorator


def get_timeout_decorator(timeout_seconds: float) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Compatibility wrapper retained for orchestration helpers."""

    return async_timeout(int(timeout_seconds))


def _extract_workflow_context(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Optional["WorkflowContext"]:
    """Inspect call arguments to find a WorkflowContext instance."""

    from .context import WorkflowContext  # Local import avoids circular import issues.

    for arg in args:
        if isinstance(arg, WorkflowContext):
            return arg
    context = kwargs.get("workflow_context")
    if isinstance(context, WorkflowContext):
        return context
    return None


def update_context(context: Optional["WorkflowContext"]) -> None:
    """Synchronise the workflow context with the MCP runtime."""

    if context is None:
        return
    try:
        sync_context(context, scope="workflow")
    except Exception as exc:  # pragma: no cover - sync failures should not break flow
        logger.debug("Context sync skipped: %s", exc)


def wrap_mcp(func: Optional[Callable] = None, *, force: bool = False) -> Callable:
    """Decorator that ensures MCP clients are initialised for node handlers."""

    if func is None:
        return lambda inner: wrap_mcp(inner, force=force)

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = _extract_workflow_context(args, kwargs)
            if context and context.is_mcp_enabled() and (force or context.wrap_mcp_nodes):
                context.ensure_mcp_clients()
            result = await func(*args, **kwargs)
            update_context(context)
            return result

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        context = _extract_workflow_context(args, kwargs)
        if context and context.is_mcp_enabled() and (force or context.wrap_mcp_nodes):
            context.ensure_mcp_clients()
        result = func(*args, **kwargs)
        update_context(context)
        return result

    return sync_wrapper


__all__ = [
    "CircuitBreaker",
    "exponential_backoff_retry",
    "async_timeout",
    "get_timeout_decorator",
    "wrap_mcp",
    "update_context",
]
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/core_v/resilience.py ====
