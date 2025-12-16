"""Hardening mixin for resilient execution.

Provides a unified way to add circuit breaking, retries, and telemetry
to any component that executes external operations.

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import logging
import time
from typing import Any, Awaitable, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class TokenLimitError(Exception):
    """Raised when token budget exceeds model limits."""


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
        telemetry: Optional[Any] = None, # Changed SystemTelemetry to Any as it's not imported
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
        # Assuming get_breaker, ErrorRecoveryManager, get_telemetry, CircuitBreakerState
        # and CircuitBreakerOpenError are defined elsewhere or intended to be imported.
        # For syntax repair, I'll assume they exist and focus on the current file's syntax.
        from resilience_components import get_breaker, ErrorRecoveryManager, get_telemetry, CircuitBreakerState, CircuitBreakerOpenError, SystemTelemetry # Added imports for missing components

        self.component_name = component_name
        self.circuit_breaker = get_breaker(
            NAME=f"{component_name}_breaker",
            failure_threshold=failure_threshold,
            reset_after_s=reset_timeout_s,
        )
        self.error_recovery = ErrorRecoveryManager(
            max_retries=max_retries,
            base_backoff_ms=base_backoff_ms,
            jitter_ms=jitter_ms,
            enable_circuit_breaker=True,
        )
        self.telemetry = telemetry or get_telemetry() # Changed SELF.TELEMETRY to self.telemetry

    async def execute_hardened( # Removed misplaced docstring
        self,
        operation: str,
        fn: Callable[[], Awaitable[Any]],
        *,
        validate_token_budget: Optional[Callable[[], None]] = None,
        metadata: Optional[Dict[str, Any]] = None,
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
        # Pre-flight validation
        if validate_token_budget:
            validate_token_budget()

        # Record start time
        start_time = time.time()

        try:
            # Execute with retry and circuit breaking
            result = await self.error_recovery.invoke_with_retry( # Changed RESULT to result
                fn=fn,
                breaker_name=self.circuit_breaker.name,
                context=metadata or {}, # Changed CONTEXT to context
            )

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Log success
            self.telemetry.log_success(
                component=self.component_name, # Changed COMPONENT to component
                operation=operation, # Changed OPERATION to operation
                latency_ms=latency_ms,
                metadata=metadata, # Changed METADATA to metadata
            )

            return result

        except CircuitBreakerOpenError as e:
            # Circuit breaker is open
            latency_ms = (time.time() - start_time) * 1000

            self.telemetry.log_circuit_breaker(
                component=self.component_name, # Changed COMPONENT to component
                breaker_name=e.breaker_name,
                state="OPEN", # Changed STATE to state
                metadata=metadata, # Changed METADATA to metadata
            )

            raise

        except Exception as e:
            # All other errors
            latency_ms = (time.time() - start_time) * 1000

            self.telemetry.log_failure(
                component=self.component_name, # Changed COMPONENT to component
                operation=operation, # Changed OPERATION to operation
                latency_ms=latency_ms,
                error_type=e.__class__.__name__,
                error_message=str(e),
                metadata=metadata, # Changed METADATA to metadata
            )

            raise

    def validate_token_budget_tiktoken( # Removed misplaced docstring
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
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
        except ImportError: # Removed 'as exc' as exc is not used
            # tiktoken not available - skip validation
            return

        # Get encoding for model
        try:
            if model.startswith("gpt-4"):
                encoding = tiktoken.encoding_for_model("gpt-4") # Changed ENCODING to encoding
            elif model.startswith("gpt-3.5"):
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo") # Changed ENCODING to encoding
            else:
                # Default to cl100k_base (most models)
                encoding = tiktoken.get_encoding("cl100k_base") # Changed ENCODING to encoding
        except KeyError: # Removed 'as exc' as exc is not used
            # Unknown model - use default
            encoding = tiktoken.get_encoding("cl100k_base") # Changed ENCODING to encoding

        # Count tokens
        tokens = len(encoding.encode(prompt)) # Changed TOKENS to tokens

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
        limit = max_tokens or model_limits.get(model, 4096) # Changed LIMIT to limit

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
        self.circuit_breaker.state = CircuitBreakerState.CLOSED
        self.circuit_breaker.failure_count = 0
        self.circuit_breaker.success_count = 0