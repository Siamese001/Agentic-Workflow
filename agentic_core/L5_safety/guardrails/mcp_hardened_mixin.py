"""
MCPHardenedMixin - Eternal Hardening for All MCP Integrations

Provides:
- Exponential backoff retry (configurable, default 3 attempts)
- SovereignEvent emission on connect/fail/success
- Timeout enforcement
- CRITIQUE emission on exhausted retries

Usage:
    class MyMCPClient(MCPHardenedMixin):
        async def call_something(self):
            return await self._hardened_call(
                "operation_name",
                self._actual_call_func,
                *args,
                **kwargs
            )
"""
import asyncio
import logging
from typing import Any, Callable, Dict, Optional

logger: Any = logging.getLogger(__name__)


class MCPHardenedMixin:
    """
    Mixin providing hardened MCP operations:
    - Exponential backoff retry (3 attempts by default)
    - SovereignEvent emission on connect/fail
    - Timeout enforcement
    - CRITIQUE emission on exhausted retries
    """

    MAX_RETRIES: int = 3
    BASE_DELAY: float = 1.0
    MAX_DELAY: float = 30.0
    DEFAULT_TIMEOUT: float = 30.0

    async def _hardened_call(
        self,
        operation: str,
        call_func: Callable,
        *args: Any,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute MCP call with retry, timeout, and observability.

        Args:
            operation: Name of the operation (for logging/events)
            call_func: Async function to call
            *args: Positional arguments for call_func
            timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)
            **kwargs: Keyword arguments for call_func

        Returns:
            Result from call_func

        Raises:
            RuntimeError: If all retries are exhausted
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        last_error: Optional[str] = None

        for attempt in range(self.MAX_RETRIES):
            try:
                self._emit_sovereign_event(
                    "MCP_CALL_START",
                    {"operation": operation, "attempt": attempt + 1},
                )

                result: Any = await asyncio.wait_for(
                    call_func(*args, **kwargs),
                    timeout=timeout,
                )

                self._emit_sovereign_event(
                    "MCP_CALL_SUCCESS",
                    {"operation": operation, "attempt": attempt + 1},
                )

                return result

            except asyncio.TimeoutError:
                last_error = f"Timeout after {timeout}s"
                self._emit_sovereign_event(
                    "MCP_CALL_TIMEOUT",
                    {
                        "operation": operation,
                        "attempt": attempt + 1,
                        "timeout": timeout,
                    },
                )
            except Exception as e:
                last_error = str(e)
                self._emit_sovereign_event(
                    "MCP_CALL_FAIL",
                    {
                        "operation": operation,
                        "attempt": attempt + 1,
                        "error": str(e),
                    },
                )

            if attempt < self.MAX_RETRIES - 1:
                delay: float = min(
                    self.BASE_DELAY * (2**attempt), self.MAX_DELAY
                )
                logger.warning(
                    f"[MCP] {operation} attempt {attempt + 1} failed, "
                    f"retrying in {delay:.1f}s: {last_error}"
                )
                await asyncio.sleep(delay)

        self._emit_critique(operation, last_error or "Unknown error")
        raise RuntimeError(
            f"MCP {operation} failed after {self.MAX_RETRIES} attempts: {last_error}"
        )

    def _emit_sovereign_event(
        self, event_type: str, data: Dict[str, Any]
    ) -> None:
        """
        Emit telemetry event for observability.

        Args:
            event_type: Type of event (MCP_CALL_START, MCP_CALL_SUCCESS, etc.)
            data: Event data dictionary
        """
        try:
            from agentic_core.observability.telemetry.sovereign_events import (
                emit_event,
            )

            emit_event(event_type, data)
        except ImportError:
            logger.debug(f"[MCP] {event_type}: {data}")

    def _emit_critique(self, operation: str, error: str) -> None:
        """
        Emit CRITIQUE for subatomic retry consideration.

        Args:
            operation: Name of the failed operation
            error: Error message
        """
        logger.critical(f"[CRITIQUE] MCP {operation} exhausted: {error}")
        try:
            from agentic_core.observability.telemetry.sovereign_events import (
                emit_event,
            )

            emit_event(
                "MCP_CRITIQUE",
                {
                    "operation": operation,
                    "error": error,
                    "retries_exhausted": True,
                },
            )
        except ImportError:
            pass
