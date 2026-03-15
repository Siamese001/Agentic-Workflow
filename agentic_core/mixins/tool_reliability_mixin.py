"""
ToolReliabilityMixin - Phase 2 Critical Infrastructure: Tool Reliability

Provides retry logic and fallback mechanisms for external tool failures.

Features:
- Configurable retry policies with exponential backoff
- Circuit breaker pattern for failing tools
- Fallback chain execution
- Tool health monitoring
- Graceful degradation

SSOT PRINCIPLE:
    All agents requiring tool reliability should inherit from this mixin.
    This ensures consistent error handling across the agent ecosystem.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from agentic_core.L0_routing.enforcement.runtime_guard import (
    runtime_guard,
)
from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout_seconds: float = 60.0  # Time before trying half-open
    half_open_max_calls: int = 3  # Max calls in half-open state


@dataclass
class ToolHealth:
    """Health status for a tool."""

    tool_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_success_time: float | None = None
    last_failure_time: float | None = None
    last_error: str | None = None
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    consecutive_successes: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls

    @property
    def is_healthy(self) -> bool:
        """Check if tool is considered healthy."""
        return self.circuit_state == CircuitState.CLOSED and self.success_rate >= 0.5


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, tool_name: str, time_until_retry: float):
        self.tool_name = tool_name
        self.time_until_retry = time_until_retry
        super().__init__(f"Circuit breaker open for '{tool_name}'. Retry in {time_until_retry:.1f}s")


class RetryExhaustedError(Exception):
    """Raised when all retries are exhausted."""

    def __init__(self, tool_name: str, attempts: int, last_error: Exception):
        self.tool_name = tool_name
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"All {attempts} retries exhausted for '{tool_name}': {last_error}")


class ToolReliabilityMixin:
    """
    Mixin providing tool reliability features for agents.

    Phase 2 Critical Infrastructure:
    - Retry logic with exponential backoff
    - Circuit breaker pattern
    - Fallback chain execution
    - Tool health monitoring

    Usage:
        class MyAgent(ToolReliabilityMixin, SovereignBaseAgent):
            def __init__(self):
                super().__init__()
                self.configure_tool_retry("llm_call", max_retries=MAX_RETRIES)
                self.configure_circuit_breaker("external_api")

            async def call_external_api(self, data):
                return await self.with_retry(
                    "external_api",
                    lambda: self._do_api_call(data),
                    fallback=lambda: self._cached_response(data)
                )
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize tool reliability state."""
        super().__init__(**kwargs)

        # Retry policies per tool
        self._retry_policies: dict[str, RetryPolicy] = {}

        # Circuit breaker configs per tool
        self._circuit_configs: dict[str, CircuitBreakerConfig] = {}

        # Tool health tracking
        self._tool_health: dict[str, ToolHealth] = {}

        # Circuit breaker state
        self._circuit_opened_at: dict[str, float] = {}
        self._half_open_calls: dict[str, int] = {}

        # [HARDENING] Thread safety lock for tool health tracking
        self._reliability_lock = __import__("threading").RLock()

        # Initialization flag
        self._tool_reliability_initialized = True

        Logger.debug(f"[RELIABILITY] {self.__class__.__name__} tool reliability initialized")

    # guardian: allow-magic-config
    def configure_tool_retry(
        self,
        tool_name: str,
        max_retries: int = 3,
        base_delay_seconds: float = 1.0,
        max_delay_seconds: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,),
    ) -> None:
        """
        Configure retry policy for a tool.

        Args:
            tool_name: Name of the tool
            max_retries: Maximum retry attempts
            base_delay_seconds: Initial delay between retries
            max_delay_seconds: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            retryable_exceptions: Exception types that trigger retry

        Raises:
            ValueError: If any parameter is invalid
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"ToolReliabilityMixin.configure_tool_retry:{tool_name}")
        # [HARDENING] Validate inputs
        if not tool_name or not tool_name.strip():
            raise ValueError("tool_name cannot be empty")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must be non-negative")
        if max_delay_seconds < base_delay_seconds:
            raise ValueError("max_delay_seconds must be >= base_delay_seconds")
        if exponential_base < 1.0:
            raise ValueError("exponential_base must be >= 1.0")

        self._retry_policies[tool_name] = RetryPolicy(
            max_retries=max_retries,
            base_delay_seconds=base_delay_seconds,
            max_delay_seconds=max_delay_seconds,
            exponential_base=exponential_base,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions,
        )
        self._ensure_tool_health(tool_name)
        Logger.info(f"[RELIABILITY] Retry policy configured for '{tool_name}'")

    # guardian: allow-magic-config
    def configure_circuit_breaker(
        self,
        tool_name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 60.0,
        half_open_max_calls: int = 3,
    ) -> None:
        """
        Configure circuit breaker for a tool.

        Args:
            tool_name: Name of the tool
            failure_threshold: Failures before opening circuit
            success_threshold: Successes to close from half-open
            timeout_seconds: Time before trying half-open
            half_open_max_calls: Max calls allowed in half-open state

        Raises:
            ValueError: If any parameter is invalid
        """
        # [HARDENING] Validate inputs
        if not tool_name or not tool_name.strip():
            raise ValueError("tool_name cannot be empty")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if success_threshold <= 0:
            raise ValueError("success_threshold must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if half_open_max_calls <= 0:
            raise ValueError("half_open_max_calls must be positive")

        self._circuit_configs[tool_name] = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds,
            half_open_max_calls=half_open_max_calls,
        )
        self._ensure_tool_health(tool_name)
        Logger.info(f"[RELIABILITY] Circuit breaker configured for '{tool_name}'")

    def _ensure_tool_health(self, tool_name: str) -> ToolHealth:
        """Ensure tool health tracking exists."""
        if tool_name not in self._tool_health:
            self._tool_health[tool_name] = ToolHealth(tool_name=tool_name)
        return self._tool_health[tool_name]

    def _calculate_delay(self, tool_name: str, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        import random

        policy = self._retry_policies.get(tool_name, RetryPolicy())

        delay = policy.base_delay_seconds * (policy.exponential_base**attempt)
        delay = min(delay, policy.max_delay_seconds)

        if policy.jitter:
            delay = delay * (0.5 + random.random())

        return delay

    def _check_circuit_breaker(self, tool_name: str) -> None:
        """
        Check circuit breaker state and raise if open.

        Raises:
            CircuitBreakerError: If circuit is open
        """
        health = self._tool_health.get(tool_name)
        if not health:
            return

        config = self._circuit_configs.get(tool_name)
        if not config:
            return

        if health.circuit_state == CircuitState.OPEN:
            opened_at = self._circuit_opened_at.get(tool_name, 0)
            elapsed = time.time() - opened_at

            if elapsed >= config.timeout_seconds:
                # Transition to half-open
                health.circuit_state = CircuitState.HALF_OPEN
                self._half_open_calls[tool_name] = 0
                Logger.info(f"[RELIABILITY] Circuit for '{tool_name}' transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerError(tool_name, config.timeout_seconds - elapsed)

        elif health.circuit_state == CircuitState.HALF_OPEN:
            calls = self._half_open_calls.get(tool_name, 0)
            if calls >= config.half_open_max_calls:
                raise CircuitBreakerError(tool_name, config.timeout_seconds)
            self._half_open_calls[tool_name] = calls + 1

    def _record_success(self, tool_name: str) -> None:
        """Record successful tool call."""
        with self._reliability_lock:
            health = self._ensure_tool_health(tool_name)
            health.total_calls += 1
            health.successful_calls += 1
            health.last_success_time = time.time()
            health.consecutive_failures = 0
            health.consecutive_successes += 1

            config = self._circuit_configs.get(tool_name)
            if config and health.circuit_state == CircuitState.HALF_OPEN:
                if health.consecutive_successes >= config.success_threshold:
                    health.circuit_state = CircuitState.CLOSED
                    health.consecutive_successes = 0
                    Logger.info(f"[RELIABILITY] Circuit for '{tool_name}' CLOSED")

    def _record_failure(self, tool_name: str, error: Exception) -> None:
        """Record failed tool call."""
        with self._reliability_lock:
            health = self._ensure_tool_health(tool_name)
            health.total_calls += 1
            health.failed_calls += 1
            health.last_failure_time = time.time()
            health.last_error = str(error)
            health.consecutive_successes = 0
            health.consecutive_failures += 1

            config = self._circuit_configs.get(tool_name)
            if config:
                if health.circuit_state == CircuitState.HALF_OPEN:
                    # Failed in half-open, reopen circuit
                    health.circuit_state = CircuitState.OPEN
                    self._circuit_opened_at[tool_name] = time.time()
                    Logger.warning(
                        f"[RELIABILITY] Circuit for '{tool_name}' reopened after half-open failure",
                    )
                elif health.consecutive_failures >= config.failure_threshold:
                    health.circuit_state = CircuitState.OPEN
                    self._circuit_opened_at[tool_name] = time.time()
                    Logger.warning(
                        f"[RELIABILITY] Circuit for '{tool_name}' OPENED after "
                        f"{health.consecutive_failures} consecutive failures",
                    )

    def _v15_build_retry_manifest(self, tool_name: str):
        """§8.1d — Construct SurgicalManifest for retry boundary entry.

        Built ONCE before the retry loop so the same manifest instance
        survives all retry attempts. Returns None when V15 enforcement is off.
        """
        if not is_v15_enforced():
            return None

        import hashlib as _hl

        from agentic_core.L0_routing.enforcement.traceability_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.determinism_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = (
            _hl.sha256(
                f"ToolReliabilityMixin.retry.{tool_name}".encode(),
            )
            .hexdigest()[:8]
            .upper()
        )
        trace_id = generate_trace_id(_hex8)

        ast_snippet = f"ToolReliabilityMixin.with_retry({tool_name!r})"
        return SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id=self.__class__.__name__,
            target_layer="L2",
            ast_snippet=ast_snippet,
            serialization_canon="tool_reliability_mixin",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=_hl.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

    def _v15_retry_audit(self, manifest, trace_id: str) -> None:
        """§8.1d — Gateway audit at retry boundary (LOG_ONLY, no RESULT)."""
        if manifest is None:
            return
        try:
            import hashlib as _hl

            from agentic_core.L0_routing.enforcement.execution_gateway import (
                V15ExecutionGateway,
            )

            gw = V15ExecutionGateway()
            gw.execute(
                manifest,
                lambda m: {"status": "retry_audit", "errors": 0},
                lambda: (
                    _hl.sha256(b"fs_retry").hexdigest(),
                    _hl.sha256(b"git_retry").hexdigest(),
                    _hl.sha256(b"mem_retry").hexdigest(),
                ),
                trace_id=trace_id,
                agent_id="tool_reliability_mixin",
            )
        # guardian: allow-silent-swallow
        except Exception as exc:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.warning("[V15] Retry gateway audit failed (LOG_ONLY): %s", exc)

    @runtime_guard("D.with_retry.tool_reliability_mixin")
    async def with_retry(
        self,
        tool_name: str,
        operation: Callable[[], T],
        fallback: Callable[[], T] | None = None,
        on_retry: Callable[[int, Exception], None] | None = None,
    ) -> T:
        """
        Execute operation with retry logic and optional fallback.

        Args:
            tool_name: Name of the tool for tracking
            operation: Async or sync callable to execute
            fallback: Optional fallback callable if all retries fail
            on_retry: Optional callback on each retry (attempt, error)

        Returns:
            Result of operation or fallback

        Raises:
            RetryExhaustedError: If all retries fail and no fallback
            CircuitBreakerError: If circuit breaker is open
        """
        # §8.1d — V15 manifest at retry boundary (built ONCE, survives all attempts)
        _v15_manifest = self._v15_build_retry_manifest(tool_name)
        if _v15_manifest is not None:
            self._v15_retry_audit(_v15_manifest, trace_id=_v15_manifest.correlation_id)

        # Check circuit breaker first
        self._check_circuit_breaker(tool_name)

        policy = self._retry_policies.get(tool_name, RetryPolicy())
        last_error: Exception | None = None

        for attempt in range(policy.max_retries + 1):
            try:
                # Execute operation
                result = operation()
                if asyncio.iscoroutine(result):
                    result = await result

                self._record_success(tool_name)
                return result

            except policy.retryable_exceptions as e:
                last_error = e
                self._record_failure(tool_name, e)

                if attempt < policy.max_retries:
                    delay = self._calculate_delay(tool_name, attempt)
                    Logger.warning(
                        f"[RELIABILITY] '{tool_name}' attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s",
                    )

                    if on_retry:
                        on_retry(attempt + 1, e)

                    await asyncio.sleep(delay)

                    # Re-check circuit breaker before retry
                    try:
                        self._check_circuit_breaker(tool_name)
                    except CircuitBreakerError:
                        break

        # All retries exhausted
        if fallback:
            Logger.info(f"[RELIABILITY] '{tool_name}' retries exhausted, using fallback")
            result = fallback()
            if asyncio.iscoroutine(result):
                result = await result
            return result

        raise RetryExhaustedError(tool_name, policy.max_retries + 1, last_error or Exception("Unknown error"))

    @runtime_guard("D.with_retry_sync.tool_reliability_mixin")
    def with_retry_sync(
        self,
        tool_name: str,
        operation: Callable[[], T],
        fallback: Callable[[], T] | None = None,
    ) -> T:
        """
        Synchronous version of with_retry.

        Args:
            tool_name: Name of the tool for tracking
            operation: Sync callable to execute
            fallback: Optional fallback callable if all retries fail

        Returns:
            Result of operation or fallback
        """
        # §8.1d — V15 manifest at retry boundary (built ONCE, survives all attempts)
        _v15_manifest = self._v15_build_retry_manifest(tool_name)
        if _v15_manifest is not None:
            self._v15_retry_audit(_v15_manifest, trace_id=_v15_manifest.correlation_id)

        self._check_circuit_breaker(tool_name)

        policy = self._retry_policies.get(tool_name, RetryPolicy())
        last_error: Exception | None = None

        for attempt in range(policy.max_retries + 1):
            try:
                result = operation()
                self._record_success(tool_name)
                return result

            except policy.retryable_exceptions as e:
                last_error = e
                self._record_failure(tool_name, e)

                if attempt < policy.max_retries:
                    delay = self._calculate_delay(tool_name, attempt)
                    Logger.warning(
                        f"[RELIABILITY] '{tool_name}' attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s",
                    )
                    time.sleep(delay)

                    try:
                        self._check_circuit_breaker(tool_name)
                    except CircuitBreakerError:
                        break

        if fallback:
            Logger.info(f"[RELIABILITY] '{tool_name}' retries exhausted, using fallback")
            return fallback()

        raise RetryExhaustedError(tool_name, policy.max_retries + 1, last_error or Exception("Unknown error"))

    def get_tool_health(self, tool_name: str) -> dict[str, Any]:
        """
        Get health status for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with health metrics
        """
        with self._reliability_lock:
            health = self._tool_health.get(tool_name)
            if not health:
                return {"tool_name": tool_name, "status": "unknown"}

            return {
                "tool_name": health.tool_name,
                "total_calls": health.total_calls,
                "successful_calls": health.successful_calls,
                "failed_calls": health.failed_calls,
                "success_rate": health.success_rate,
                "is_healthy": health.is_healthy,
                "circuit_state": health.circuit_state.value,
                "consecutive_failures": health.consecutive_failures,
                "last_error": health.last_error,
            }

    def get_all_tool_health(self) -> dict[str, dict[str, Any]]:
        """
        Get health status for all tracked tools.

        Returns:
            Dictionary mapping tool names to health metrics
        """
        return {name: self.get_tool_health(name) for name in self._tool_health}

    def reset_circuit_breaker(self, tool_name: str) -> None:
        """
        Manually reset circuit breaker for a tool.

        Args:
            tool_name: Name of the tool
        """
        with self._reliability_lock:
            health = self._tool_health.get(tool_name)
            if health:
                health.circuit_state = CircuitState.CLOSED
                health.consecutive_failures = 0
                health.consecutive_successes = 0
                self._circuit_opened_at.pop(tool_name, None)
                self._half_open_calls.pop(tool_name, None)
                Logger.info(f"[RELIABILITY] Circuit breaker reset for '{tool_name}'")


__all__ = [
    "ToolReliabilityMixin",
    "RetryPolicy",
    "CircuitBreakerConfig",
    "ToolHealth",
    "CircuitState",
    "CircuitBreakerError",
    "RetryExhaustedError",
]
