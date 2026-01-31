"""Hardening mixin for resilient execution.

Provides a unified way to add circuit breaking, retries, and telemetry
to any component that executes external operations.

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any

from agentic_core.L4_state.ledger.CircuitBreaker import CircuitBreakerOpenError, get_breaker

from .ErrorRecoveryManager import ErrorRecoveryManager
from .SystemTelemetry import SystemTelemetry, get_telemetry


class TokenLimitError(Exception):
    """Raised when token budget exceeds model limits."""

    pass


class HardeningMixin:
    """Mixin that adds military-grade resilience to any executor.

    Integrates circuit breaking, retry logic, and structured telemetry.
    Classes should inherit from this mixin and call execute_hardened()
    for external operations.
    """

    def __init__(
        self,
        component_name: str,
        *,
        failure_threshold: int = 5,
        reset_timeout_s: int = 30,
        max_retries: int = 3,
        base_backoff_ms: int = 200,
        jitter_ms: int = 100,
        telemetry: SystemTelemetry | None = None,
    ):
        """Initialize hardening components.

        Args:
            component_name: Name for telemetry and circuit breaker
            failure_threshold: Failures before opening circuit
            reset_timeout_s: Seconds before attempting recovery
            max_retries: Maximum retry attempts
            base_backoff_ms: Base delay for exponential backoff
            jitter_ms: Random jitter range
            telemetry: Custom telemetry instance (uses default if None)
        """
        self.component_name = component_name
        self.circuit_breaker = get_breaker(
            name=f"{component_name}_breaker",
            failure_threshold=failure_threshold,
            reset_after_s=reset_timeout_s,
        )
        self.error_recovery = ErrorRecoveryManager(
            max_retries=max_retries,
            base_backoff_ms=base_backoff_ms,
            jitter_ms=jitter_ms,
            enable_circuit_breaker=True,
        )
        self.telemetry = telemetry or get_telemetry()

    async def execute_hardened(
        self,
        operation: str,
        fn: Callable[[], Awaitable[Any]],
        *,
        validate_token_budget: Callable[[], None] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Execute an async function with full hardening applied.

        Args:
            operation: Operation name for telemetry
            fn: Async function to execute
            validate_token_budget: Optional pre-flight validation
            metadata: Additional telemetry metadata

        Returns:
            Result from successful execution

        Raises:
            TokenLimitError: If token budget validation fails
            CircuitBreakerOpenError: If circuit breaker is open
            Exception: If all retries exhausted
        """
        # Record start time
        start_time = time.time()

        try:
            # Pre-flight validation
            if validate_token_budget:
                await asyncio.wait_for(
                    asyncio.to_thread(validate_token_budget),
                    timeout=2.5,
                )
            # Execute with retry and circuit breaking
            result = await self.error_recovery.invoke_with_retry(
                fn=fn,
                breaker_name=self.circuit_breaker.name,
                context=metadata or {},
            )

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Log success
            self.telemetry.log_success(
                component=self.component_name,
                operation=operation,
                latency_ms=latency_ms,
                metadata=metadata,
            )

            return result

        except asyncio.TimeoutError as e:
            latency_ms = (time.time() - start_time) * 1000

            self.telemetry.log_failure(
                component=self.component_name,
                operation=operation,
                latency_ms=latency_ms,
                error_type="ValidationTimeout",
                error_message="Token budget validation timed out",
                metadata=metadata,
            )

            raise TokenLimitError("Token budget validation timed out") from e

        except CircuitBreakerOpenError as e:
            # Circuit breaker is open
            latency_ms = (time.time() - start_time) * 1000

            self.telemetry.log_circuit_breaker(
                component=self.component_name,
                breaker_name=e.breaker_name,
                state="OPEN",
                metadata=metadata,
            )

            raise

        except Exception as e:
            # All other errors
            latency_ms = (time.time() - start_time) * 1000

            self.telemetry.log_failure(
                component=self.component_name,
                operation=operation,
                latency_ms=latency_ms,
                error_type=e.__class__.__name__,
                error_message=str(e),
                metadata=metadata,
            )

            raise

    def validate_token_budget_tiktoken(
        self,
        prompt: str,
        model: str,
        max_tokens: int | None = None,
    ) -> None:
        """Validate token budget using tiktoken.

        Args:
            prompt: Input prompt text
            model: OpenAI model name
            max_tokens: Maximum tokens allowed (model-specific if None)

        Raises:
            TokenLimitError: If prompt exceeds token budget
        """
        try:
            import tiktoken
        except ImportError:
            # tiktoken not available - skip validation
            return

        # Get encoding for model
        try:
            if model.startswith("gpt-4"):
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif model.startswith("gpt-3.5"):
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                # Default to cl100k_base (most models)
                encoding = tiktoken.get_encoding("cl100k_base")
        except KeyError:
            # Unknown model - use default
            encoding = tiktoken.get_encoding("cl100k_base")

        # Count tokens
        tokens = len(encoding.encode(prompt))

        # Model-specific limits
        model_limits = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-0613": 8192,
            "gpt-4-32k-0613": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-0613": 4096,
            "gpt-3.5-turbo-16k-0613": 16384,
            "gpt-4o": 128000,
            "gpt-4o-2024-08-06": 128000,
            "gpt-4o-mini": 128000,
        }

        # Find model limit
        limit = max_tokens or model_limits.get(model, 4096)

        # Check if over limit
        if tokens > limit:
            raise TokenLimitError(
                f"Prompt exceeds token budget: {tokens} > {limit} for model {model}"
            )

    def get_circuit_breaker_state(self) -> str:
        """Get current circuit breaker state."""
        return self.circuit_breaker.state.value

    def reset_circuit_breaker(self) -> None:
        """Reset circuit breaker to CLOSED state (for testing)."""
        from .circuit_breaker import CircuitBreakerState

        self.circuit_breaker.state = CircuitBreakerState.CLOSED
        self.circuit_breaker.failure_count = 0
        self.circuit_breaker.success_count = 0
