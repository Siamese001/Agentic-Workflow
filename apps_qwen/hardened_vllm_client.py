"""Hardened vLLM Client with Resilience Patterns.

Adds production-grade reliability features:
- Exponential backoff retry with jitter
- Circuit breaker pattern for failure isolation
- Graceful degradation on GPU OOM
- Request timeout handling
- Health check probing
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

from apps_qwen.optimized_vllm_client import (
    OptimizedVLLMClient,
    VLLMRequest,
    VLLMResponse,
)

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = auto()      # Normal operation
    OPEN = auto()        # Failing, reject requests
    HALF_OPEN = auto()   # Testing if service recovered


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_retries: int = 3
    base_delay_sec: float = 1.0
    max_delay_sec: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout_sec: float = 30.0
    half_open_max_calls: int = 3
    success_threshold: int = 2


@dataclass
class HardeningMetrics:
    """Metrics for hardened client."""
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    requests_retried: int = 0
    requests_circuit_blocked: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    gpu_oom_events: int = 0
    latency_p50_ms: float = 0.0
    latency_p99_ms: float = 0.0
    _latencies: list[float] = field(default_factory=list)

    def record_latency(self, latency_ms: float) -> None:
        """Record latency for percentile calculation."""
        self._latencies.append(latency_ms)
        # Keep last 1000 samples
        if len(self._latencies) > 1000:
            self._latencies = self._latencies[-1000:]

        # Update percentiles
        if self._latencies:
            sorted_lat = sorted(self._latencies)
            p50_idx = int(len(sorted_lat) * 0.5)
            p99_idx = int(len(sorted_lat) * 0.99)
            self.latency_p50_ms = sorted_lat[p50_idx]
            self.latency_p99_ms = sorted_lat[p99_idx] if p99_idx < len(sorted_lat) else sorted_lat[-1]


class CircuitBreaker:
    """Circuit breaker for failure isolation."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()

    async def call(self, operation: Callable[[], Any]) -> Any:
        """Execute operation with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    self.success_count = 0
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpenError("Circuit breaker HALF_OPEN limit reached")
                self.half_open_calls += 1

        # Execute operation outside lock
        try:
            result = await operation()
            await self._record_success()
            return result
        except Exception as _:
            await self._record_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout_sec

    async def _record_success(self) -> None:
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.info("Half-open success: %d/%d", self.success_count, self.config.success_threshold)
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.half_open_calls = 0
                    logger.info("Circuit breaker CLOSED - service recovered")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)

    async def _record_failure(self) -> None:
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker OPEN - recovery failed")
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker OPEN - %d failures", self.failure_count)


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""


class HardenedVLLMClient:
    """Hardened vLLM client with retry, circuit breaker, and OOM handling."""

    def __init__(
        self,
        base_client: OptimizedVLLMClient,
        retry_config: RetryConfig | None = None,
        circuit_config: CircuitBreakerConfig | None = None,
    ):
        self.base_client = base_client
        self.retry_config = retry_config or RetryConfig()
        self.circuit = CircuitBreaker(circuit_config or CircuitBreakerConfig())
        self.metrics = HardeningMetrics()
        self._degraded_mode = False
        self._min_batch_size = 1

    async def infer(self, request: VLLMRequest) -> VLLMResponse:
        """Execute inference with full hardening."""
        self.metrics.requests_total += 1

        try:
            # Try with circuit breaker
            response = await self.circuit.call(
                lambda: self._infer_with_retry(request)
            )

            if response.success:
                self.metrics.requests_success += 1
                self.metrics.record_latency(response.latency_ms)
            else:
                self.metrics.requests_failed += 1
                # Check for OOM
                if self._is_oom_error(response.error_message):
                    await self._handle_oom()

            return response

        except CircuitBreakerOpenError:
            self.metrics.requests_circuit_blocked += 1
            return VLLMResponse(
                success=False,
                text="",
                model="",
                tokens_used=0,
                latency_ms=0.0,
                error_message="Circuit breaker open - service unavailable",
            )
        except (OSError, RuntimeError) as e:
            self.metrics.requests_failed += 1
            return VLLMResponse(
                success=False,
                text="",
                model="",
                tokens_used=0,
                latency_ms=0.0,
                error_message=f"Unexpected error: {e}",
            )

    async def _infer_with_retry(self, request: VLLMRequest) -> VLLMResponse:
        """Execute inference with retry logic."""
        last_error: Exception | None = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                response = await self.base_client.infer(request)

                # Don't retry on success or client errors (4xx)
                if response.success or self._is_client_error(response.error_message):
                    return response

                # Retryable error - treat as failure for circuit breaker
                last_error = Exception(response.error_message)
                await self.circuit._record_failure()

                if attempt < self.retry_config.max_retries:
                    delay = self._calculate_delay(attempt)
                    self.metrics.requests_retried += 1
                    logger.warning("Retry %d/%d after %.1fs: %s", attempt + 1, self.retry_config.max_retries, delay, response.error_message)
                    await asyncio.sleep(delay)

            except (OSError, RuntimeError) as e:
                last_error = e
                # Record failure for circuit breaker
                await self.circuit._record_failure()
                if attempt < self.retry_config.max_retries:
                    delay = self._calculate_delay(attempt)
                    self.metrics.requests_retried += 1
                    logger.warning("Retry %d/%d after %.1fs: %s", attempt + 1, self.retry_config.max_retries, delay, e)
                    await asyncio.sleep(delay)

        # All retries exhausted
        return VLLMResponse(
            success=False,
            text="",
            model="",
            tokens_used=0,
            latency_ms=0.0,
            error_message=f"Max retries exceeded: {last_error}",
        )

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        delay = self.retry_config.base_delay_sec * (
            self.retry_config.exponential_base ** attempt
        )
        delay = min(delay, self.retry_config.max_delay_sec)

        if self.retry_config.jitter:
            # Add ±25% jitter
            jitter = delay * 0.25 * (2 * random.random() - 1)
            delay += jitter

        return delay

    def _is_client_error(self, error_message: str | None) -> bool:
        """Check if error is a client error (don't retry)."""
        if not error_message:
            return False
        client_indicators = [
            "invalid request",
            "bad request",
            "validation error",
            "invalid prompt",
            "too large",
        ]
        error_lower = error_message.lower()
        return any(indicator in error_lower for indicator in client_indicators)

    def _is_oom_error(self, error_message: str | None) -> bool:
        """Check if error is GPU OOM."""
        if not error_message:
            return False
        oom_indicators = [
            "out of memory",
            "oom",
            "cuda out of memory",
            "gpu memory exceeded",
            "allocation failed",
        ]
        error_lower = error_message.lower()
        return any(indicator in error_lower for indicator in oom_indicators)

    async def _handle_oom(self) -> None:
        """Handle GPU OOM by reducing batch sizes."""
        self.metrics.gpu_oom_events += 1

        if not self._degraded_mode:
            self._degraded_mode = True
            logger.warning("Entering degraded mode due to GPU OOM")

        # Reduce batch size on the base client
        if hasattr(self.base_client, 'batch_size'):
            old_batch = self.base_client.batch_size
            new_batch = max(self._min_batch_size, old_batch // 2)
            self.base_client.batch_size = new_batch
            logger.warning("Reduced batch size: %d -> %d", old_batch, new_batch)

    def get_metrics(self) -> dict[str, Any]:
        """Get hardening metrics."""
        return {
            "requests_total": self.metrics.requests_total,
            "requests_success": self.metrics.requests_success,
            "requests_failed": self.metrics.requests_failed,
            "requests_retried": self.metrics.requests_retried,
            "requests_circuit_blocked": self.metrics.requests_circuit_blocked,
            "success_rate": self.metrics.requests_success / max(1, self.metrics.requests_total),
            "retry_rate": self.metrics.requests_retried / max(1, self.metrics.requests_total),
            "circuit_opens": self.circuit.failure_count,
            "circuit_state": self.circuit.state.name,
            "gpu_oom_events": self.metrics.gpu_oom_events,
            "degraded_mode": self._degraded_mode,
            "latency_p50_ms": self.metrics.latency_p50_ms,
            "latency_p99_ms": self.metrics.latency_p99_ms,
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check including hardening status."""
        base_health = await self.base_client.health_check()

        return {
            **base_health,
            "circuit_state": self.circuit.state.name,
            "degraded_mode": self._degraded_mode,
            "retry_config": {
                "max_retries": self.retry_config.max_retries,
                "base_delay_sec": self.retry_config.base_delay_sec,
            },
        }


__all__ = [
    "HardenedVLLMClient",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "RetryConfig",
    "HardeningMetrics",
    "CircuitState",
    "CircuitBreakerOpenError",
]
