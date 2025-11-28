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

    def __init__(self, failure_threshold: int = 3):
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

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
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
