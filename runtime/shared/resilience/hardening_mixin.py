"""
HardeningMixin - Unified resilience infrastructure for all components.

Provides common hardening patterns (circuit breaking, retry logic, telemetry)
that can be inherited by any component requiring fault tolerance.
"""

import time
import logging
from typing import Any, Callable, Optional, Dict
from pydantic import BaseModel, Field

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

from .circuit_breaker import CircuitBreaker, CircuitBreakerError
from .telemetry import SystemTelemetry, get_telemetry

logger = logging.getLogger(__name__)

class HardeningConfig(BaseModel):
    """Unified configuration for the HardeningMixin."""
    component_name: str = Field(..., description="Name for telemetry tracking.")
    max_retries: int = Field(5, ge=1, description="Max retry attempts for transient errors.")
    wait_min_ms: int = Field(1000, ge=1, description="Minimum backoff wait time in milliseconds.")
    wait_max_ms: int = Field(60000, ge=1, description="Maximum backoff wait time in milliseconds.")
    circuit_breaker_threshold: int = Field(5, ge=1, description="Failure count to trip the circuit.")
    circuit_reset_timeout: int = Field(60, ge=1, description="Seconds before attempting circuit recovery.")
    safety_threshold_ratio: float = Field(0.8, ge=0.0, le=1.0, description="Pre-flight token safety ratio.")
    enable_telemetry: bool = Field(True, description="Enable telemetry logging.")

class HardeningMixin:
    """
    Provides common hardening patterns for all components.

    Features:
    - Circuit Breaking: Prevents cascading failures
    - Retry Logic: Handles transient errors with exponential backoff
    - Telemetry: Structured logging and metrics collection

    Usage:
        class MyExecutor(HardeningMixin):
            def __init__(self, config: HardeningConfig):
                super().__init__(config)

            async def my_operation(self, *args, **kwargs):
                return await self.execute_with_hardening(
                    self._raw_operation,
                    *args,
                    **kwargs
                )
    """

    def __init__(self, config: HardeningConfig):
        """Initialize hardening infrastructure.

        Args:
            config: Hardening configuration
        """
        self.config = config

        # 1. Circuit Breaker initialization
        self.circuit_breaker = CircuitBreaker(
            name=config.component_name,
            fail_max=config.circuit_breaker_threshold,
            reset_timeout=config.circuit_reset_timeout
        )

        # 2. Telemetry Logger initialization
        self.telemetry = get_telemetry() if config.enable_telemetry else None

        # 3. Retry configuration (using tenacity)
        self._retry_decorator = retry(
            retry=retry_if_exception_type((
                ConnectionError,
                TimeoutError,
                # Add provider-specific transient errors here
            )),
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                multiplier=self.config.wait_min_ms / 1000,
                min=self.config.wait_min_ms / 1000,
                max=self.config.wait_max_ms / 1000
            ),
            reraise=True
        )

        logger.info(
            f"HardeningMixin initialized for '{config.component_name}': "
            f"max_retries={config.max_retries}, "
            f"circuit_threshold={config.circuit_breaker_threshold}"
        )

    async def execute_with_hardening(
        self,
        operation_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with full hardening stack.

        Flow:
        1. Circuit Breaker Check -> Fail fast if circuit is open
        2. Retry Loop -> Handle transient errors with exponential backoff
        3. Telemetry Logging -> Record success/failure metrics

        Args:
            operation_func: The operation to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Operation result

        Raises:
            CircuitBreakerError: If circuit is open
            RetryError: If all retry attempts exhausted
            Exception: Any unhandled exception from operation
        """
        component_name = self.config.component_name
        operation_name = operation_func.__name__
        start_time = time.time()
        tokens_used = 0

        # --- 1. Circuit Breaker Check ---
        try:
            self.circuit_breaker.raise_if_open()
        except CircuitBreakerError as e:
            # Log circuit breaker trip
            if self.telemetry:
                self.telemetry.log_operation(
                    component=component_name,
                    operation=operation_name,
                    duration=time.time() - start_time,
                    error=f"Circuit breaker open: {str(e)}"
                )
            raise

        # --- 2. Retry Loop with Exponential Backoff ---
        @self._retry_decorator
        async def _execute_with_retry():
            nonlocal tokens_used

            try:
                # Execute the operation
                result = await operation_func(*args, **kwargs)

                # Extract tokens if available (for LLM operations)
                if isinstance(result, tuple) and len(result) == 2:
                    actual_result, tokens_used = result
                    result = actual_result
                elif isinstance(result, dict) and 'tokens_used' in result:
                    tokens_used = result.get('tokens_used', 0)

                # --- Record Success ---
                self.circuit_breaker.record_success()

                # --- Structured Telemetry Logging ---
                if self.telemetry:
                    duration = time.time() - start_time
                    self.telemetry.log_operation(
                        component=component_name,
                        operation=operation_name,
                        duration=duration,
                        tokens=tokens_used
                    )

                return result

            except Exception as e:
                # --- Record Failure ---
                self.circuit_breaker.record_failure()

                # --- Log Failure Telemetry ---
                if self.telemetry:
                    self.telemetry.log_operation(
                        component=component_name,
                        operation=operation_name,
                        duration=time.time() - start_time,
                        error=str(e)
                    )

                # Re-raise for retry logic to handle
                raise

        try:
            return await _execute_with_retry()
        except RetryError as e:
            # All retries exhausted
            logger.error(
                f"All retries exhausted for {component_name}.{operation_name}: "
                f"{str(e.last_attempt.exception())}"
            )
            raise

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the hardened component.

        Returns:
            Health status dictionary
        """
        circuit_status = self.circuit_breaker.get_status()

        health = {
            "component": self.config.component_name,
            "healthy": self.circuit_breaker.is_closed(),
            "circuit_breaker": circuit_status,
            "config": {
                "max_retries": self.config.max_retries,
                "wait_min_ms": self.config.wait_min_ms,
                "wait_max_ms": self.config.wait_max_ms
            }
        }

        # Add telemetry stats if available
        if self.telemetry:
            health["telemetry"] = self.telemetry.get_component_stats(
                self.config.component_name
            )

        return health

    def reset_circuit(self) -> None:
        """Manually reset the circuit breaker."""
        self.circuit_breaker.reset()
        logger.info(f"Circuit breaker manually reset for '{self.config.component_name}'")
