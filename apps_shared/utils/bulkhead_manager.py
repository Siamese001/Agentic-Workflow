"""Bulkhead Manager - Resource isolation for execution pools.

This module implements the bulkhead pattern to prevent resource starvation
between different engine types and priorities, ensuring that high-priority
tasks are not blocked by lower-priority ones.
"""

import asyncio
import logging
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker_registry
from .signal_infrastructure import EngineType

logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class BulkheadConfig:
    """configuration for a bulkhead."""

    max_concurrency: int
    priority: TaskPriority
    queue_size: int = 100
    timeout_seconds: float = 30.0
    metrics_enabled: bool = True


@dataclass
class BulkheadMetrics:
    """Metrics for a bulkhead."""

    name: str
    max_concurrency: int
    queue_size: int
    active_tasks: int = 0
    queued_tasks: int = 0
    completed_tasks: int = 0
    rejected_tasks: int = 0
    avg_wait_time_ms: float = 0.0
    max_wait_time_ms: float = 0.0
    utilization_percent: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ResourceExhaustedError(Exception):
    """Raised when bulkhead resources are exhausted."""

    def __init__(self, bulkhead_name: str, reason: str):
        """Initialize resource exhausted error.

        Args:
            bulkhead_name: Name of the bulkhead
            reason: Reason for exhaustion
        """
        super().__init__(f"Bulkhead '{bulkhead_name}' exhausted: {reason}")
        self.bulkhead_name = bulkhead_name
        self.reason = reason


class Bulkhead:
    """A single bulkhead with isolated resources."""

    def __init__(self, name: str, config: BulkheadConfig, enable_circuit_breaker: bool = True):
        """Initialize bulkhead.

        Args:
            name: Bulkhead name
            config: Bulkhead configuration
            enable_circuit_breaker: Whether to enable circuit breaker
        """
        self.name = name
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrency)
        self.queue = asyncio.Queue(maxsize=config.queue_size)
        self.metrics = BulkheadMetrics(
            name=name,
            max_concurrency=config.max_concurrency,
            queue_size=config.queue_size,
        )

        # Task tracking
        self._active_tasks: set[asyncio.Task] = set()
        self._wait_times: deque = deque(maxlen=1000)
        self._completed_count = 0
        self._rejected_count = 0

        # Circuit breaker
        self.circuit_breaker: CircuitBreaker | None = None
        if enable_circuit_breaker:
            self._circuit_breaker_config = CircuitBreakerConfig(
                failure_threshold=max(3, config.max_concurrency // 2),
                timeout=60.0,
                failure_rate_threshold=0.5,
            )

        logger.info(f"Created bulkhead '{name}' with max_concurrency={config.max_concurrency}")

    async def _get_circuit_breaker(self) -> CircuitBreaker | None:
        """Get or create circuit breaker.

        Returns:
            CircuitBreaker instance if enabled
        """
        if self.circuit_breaker is None and hasattr(self, "_circuit_breaker_config"):
            registry = await get_circuit_breaker_registry()
            self.circuit_breaker = await registry.get_circuit_breaker(
                f"bulkhead_{self.name}",
                self._circuit_breaker_config,
            )
        return self.circuit_breaker

    async def execute(self, coro: Callable, *args, timeout: float | None = None, **kwargs) -> Any:
        """Execute a coroutine within the bulkhead.

        Args:
            coro: Coroutine function to execute
            *args: Arguments to pass to coroutine
            timeout: Optional timeout override
            **kwargs: Keyword arguments to pass to coroutine

        Returns:
            Result of coroutine execution

        Raises:
            ResourceExhaustedError: If bulkhead is full
            asyncio.TimeoutError: If execution times out
        """
        # Check circuit breaker first
        circuit_breaker = await self._get_circuit_breaker()
        if circuit_breaker and not circuit_breaker.can_execute():
            raise ResourceExhaustedError(
                self.name,
                f"Circuit breaker is {circuit_breaker.state.value}",
            )

        start_time = time.time()

        # Try to acquire semaphore with timeout
        timeout = timeout or self.config.timeout_seconds

        try:
            # Check if we can queue the task
            if self.queue.full():
                self._rejected_count += 1
                self.metrics.rejected_tasks = self._rejected_count
                if circuit_breaker:
                    circuit_breaker.record_failure(
                        ResourceExhaustedError(self.name, "Queue full"),
                        0,
                    )
                raise ResourceExhaustedError(
                    self.name,
                    f"Queue full ({self.queue.qsize()}/{self.config.queue_size})",
                )

            # Add to queue
            await self.queue.put(None)

            # Acquire semaphore
            try:
                await asyncio.wait_for(self.semaphore.acquire(), timeout=timeout)
            except asyncio.TimeoutError:
                self.queue.get_nowait()  # Remove from queue
                self._rejected_count += 1
                self.metrics.rejected_tasks = self._rejected_count
                if circuit_breaker:
                    circuit_breaker.record_failure(
                        asyncio.TimeoutError(f"Timeout acquiring semaphore after {timeout}s"),
                        timeout * 1000,
                    )
                raise ResourceExhaustedError(
                    self.name,
                    f"Timeout acquiring semaphore after {timeout}s",
                )

            # Track wait time
            wait_time = (time.time() - start_time) * 1000
            self._wait_times.append(wait_time)

            # Create task
            task = asyncio.create_task(self._execute_with_circuit_breaker(coro, *args, **kwargs))
            self._active_tasks.add(task)
            task.add_done_callback(lambda t: self._active_tasks.discard(t))

            # Update metrics
            self._update_metrics()

            # Get result
            result = await task

            self._completed_count += 1
            return result

        finally:
            # Cleanup
            if not self.queue.empty():
                self.queue.get_nowait()
            self.semaphore.release()
            self._update_metrics()

    async def _execute_with_circuit_breaker(self, coro: Callable, *args, **kwargs) -> Any:
        """Execute coroutine with circuit breaker tracking.

        Args:
            coro: Coroutine function
            *args: Arguments
            **kwargs: Keyword arguments

        Returns:
            Result
        """
        circuit_breaker = await self._get_circuit_breaker()

        if circuit_breaker:
            # Execute through circuit breaker
            return await circuit_breaker.call(coro, *args, **kwargs)
        else:
            # Execute normally
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                logger.error(f"Task in bulkhead '{self.name}' failed: {e}")
                raise

    async def _execute_with_tracking(self, coro: Callable, *args, **kwargs) -> Any:
        """Execute coroutine with tracking.

        Args:
            coro: Coroutine function
            *args: Arguments
            **kwargs: Keyword arguments

        Returns:
            Result
        """
        try:
            return await coro(*args, **kwargs)
        except Exception as e:
            logger.error(f"Task in bulkhead '{self.name}' failed: {e}")
            raise

    def _update_metrics(self) -> None:
        """Update bulkhead metrics."""
        self.metrics.active_tasks = len(self._active_tasks)
        self.metrics.queued_tasks = self.queue.qsize()
        self.metrics.completed_tasks = self._completed_count
        self.metrics.rejected_tasks = self._rejected_count

        if self._wait_times:
            self.metrics.avg_wait_time_ms = sum(self._wait_times) / len(self._wait_times)
            self.metrics.max_wait_time_ms = max(self._wait_times)

        # Calculate utilization
        if self.config.max_concurrency > 0:
            self.metrics.utilization_percent = (self.metrics.active_tasks / self.config.max_concurrency) * 100

        self.metrics.last_updated = datetime.utcnow()

    def try_acquire(self) -> bool:
        """Try to acquire without blocking.

        Returns:
            True if acquired, False otherwise
        """
        return self.semaphore._value > 0 and not self.queue.full()

    def get_metrics(self) -> BulkheadMetrics:
        """Get current metrics.

        Returns:
            Bulkhead metrics
        """
        self._update_metrics()
        return self.metrics

    async def wait_for_available(self, timeout: float = 1.0) -> bool:
        """Wait for resources to become available.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if resources available, False if timeout
        """
        try:
            await asyncio.wait_for(self.queue.join(), timeout=timeout)
            return self.try_acquire()
        except asyncio.TimeoutError:
            return False


class BulkheadManager:
    """Manages multiple bulkheads for resource isolation."""

    def __init__(self):
        """Initialize bulkhead manager."""
        self.bulkheads: dict[str, Bulkhead] = {}
        self._global_metrics = {
            "total_active_tasks": 0,
            "total_queued_tasks": 0,
            "bulkhead_count": 0,
        }

        # Default configurations
        self._default_configs = {
            "RESUME_GENERATION": BulkheadConfig(
                max_concurrency=5,
                priority=TaskPriority.HIGH,
                queue_size=50,
            ),
            "OUTREACH_GENERATION": BulkheadConfig(
                max_concurrency=10,
                priority=TaskPriority.MEDIUM,
                queue_size=100,
            ),
            "BACKGROUND_ANALYSIS": BulkheadConfig(
                max_concurrency=2,
                priority=TaskPriority.LOW,
                queue_size=20,
            ),
            "CRITICAL_OPERATIONS": BulkheadConfig(
                max_concurrency=3,
                priority=TaskPriority.CRITICAL,
                queue_size=10,
                timeout_seconds=60.0,
            ),
        }

        # Initialize default bulkheads
        for name, config in self._default_configs.items():
            self.create_bulkhead(name, config)

        logger.info(f"Initialized BulkheadManager with {len(self.bulkheads)} bulkheads")

    def create_bulkhead(self, name: str, config: BulkheadConfig) -> Bulkhead:
        """Create a new bulkhead.

        Args:
            name: Bulkhead name
            config: Bulkhead configuration

        Returns:
            Created bulkhead
        """
        if name in self.bulkheads:
            raise ValueError(f"Bulkhead '{name}' already exists")

        bulkhead = Bulkhead(name, config)
        self.bulkheads[name] = bulkhead
        self._global_metrics["bulkhead_count"] += 1

        logger.info(f"Created bulkhead '{name}'")
        return bulkhead

    def get_bulkhead(self, name: str) -> Bulkhead | None:
        """Get a bulkhead by name.

        Args:
            name: Bulkhead name

        Returns:
            Bulkhead if found
        """
        return self.bulkheads.get(name)

    def remove_bulkhead(self, name: str) -> bool:
        """Remove a bulkhead.

        Args:
            name: Bulkhead name

        Returns:
            True if removed
        """
        if name in self.bulkheads:
            del self.bulkheads[name]
            self._global_metrics["bulkhead_count"] -= 1
            logger.info(f"Removed bulkhead '{name}'")
            return True
        return False

    async def execute(
        self,
        bulkhead_name: str,
        coro: Callable,
        *args,
        timeout: float | None = None,
        **kwargs,
    ) -> Any:
        """Execute a coroutine in a specific bulkhead.

        Args:
            bulkhead_name: Name of bulkhead
            coro: Coroutine to execute
            *args: Arguments
            timeout: Optional timeout
            **kwargs: Keyword arguments

        Returns:
            Result of execution

        Raises:
            ResourceExhaustedError: If bulkhead not found or exhausted
        """
        bulkhead = self.get_bulkhead(bulkhead_name)
        if not bulkhead:
            raise ResourceExhaustedError(bulkhead_name, "Bulkhead not found")

        return await bulkhead.execute(coro, *args, timeout=timeout, **kwargs)

    def get_engine_bulkhead(self, engine_type: EngineType) -> str:
        """Get bulkhead name for engine type.

        Args:
            engine_type: Type of engine

        Returns:
            Bulkhead name
        """
        if engine_type == EngineType.RESUME:
            return "RESUME_GENERATION"
        else:
            return "OUTREACH_GENERATION"

    async def execute_for_engine(
        self,
        engine_type: EngineType,
        coro: Callable,
        *args,
        timeout: float | None = None,
        **kwargs,
    ) -> Any:
        """Execute a coroutine for a specific engine.

        Args:
            engine_type: Type of engine
            coro: Coroutine to execute
            *args: Arguments
            timeout: Optional timeout
            **kwargs: Keyword arguments

        Returns:
            Result of execution
        """
        bulkhead_name = self.get_engine_bulkhead(engine_type)
        return await self.execute(bulkhead_name, coro, *args, timeout=timeout, **kwargs)

    def get_all_metrics(self) -> dict[str, Any]:
        """Get metrics for all bulkheads.

        Returns:
            Metrics dictionary
        """
        bulkhead_metrics = {}
        total_active = 0
        total_queued = 0

        for name, bulkhead in self.bulkheads.items():
            metrics = bulkhead.get_metrics()
            bulkhead_metrics[name] = metrics
            total_active += metrics.active_tasks
            total_queued += metrics.queued_tasks

        self._global_metrics.update(
            {"total_active_tasks": total_active, "total_queued_tasks": total_queued},
        )

        return {"global": self._global_metrics, "bulkheads": bulkhead_metrics}

    def log_utilization(self) -> None:
        """Log current utilization of all bulkheads."""
        metrics = self.get_all_metrics()

        logger.info("=== Bulkhead Utilization ===")
        logger.info(f"Total Active: {metrics['global']['total_active_tasks']}")
        logger.info(f"Total Queued: {metrics['global']['total_queued_tasks']}")

        for name, bulkhead_metrics in metrics["bulkheads"].items():
            logger.info(
                f"{name}: {bulkhead_metrics.active_tasks}/{bulkhead_metrics.config.max_concurrency} "
                f"({bulkhead_metrics.utilization_percent:.1f}%) "
                f"Queue: {bulkhead_metrics.queued_tasks}/{bulkhead_metrics.config.queue_size}",
            )

    async def health_check(self) -> dict[str, Any]:
        """Check health of all bulkheads.

        Returns:
            Health status
        """
        issues = []

        for name, bulkhead in self.bulkheads.items():
            metrics = bulkhead.get_metrics()

            # Check for high utilization
            if metrics.utilization_percent > 90:
                issues.append(f"{name}: High utilization ({metrics.utilization_percent:.1f}%)")

            # Check for queue buildup
            if metrics.queued_tasks > metrics.config.queue_size * 0.8:
                issues.append(
                    f"{name}: Queue buildup ({metrics.queued_tasks}/{metrics.config.queue_size})",
                )

            # Check for high rejection rate
            if metrics.completed_tasks > 0:
                rejection_rate = metrics.rejected_tasks / (metrics.completed_tasks + metrics.rejected_tasks)
                if rejection_rate > 0.1:  # 10% rejection rate
                    issues.append(f"{name}: High rejection rate ({rejection_rate:.1%})")

        return {
            "status": "healthy" if not issues else "degraded",
            "bulkheads": len(self.bulkheads),
            "issues": issues,
            "metrics": self.get_all_metrics(),
        }


# Global bulkhead manager
_bulkhead_manager: BulkheadManager | None = None
_manager_lock = asyncio.Lock()


async def get_bulkhead_manager() -> BulkheadManager:
    """Get global bulkhead manager instance.

    Returns:
        BulkheadManager instance
    """
    global _bulkhead_manager
    async with _manager_lock:
        if _bulkhead_manager is None:
            _bulkhead_manager = BulkheadManager()
    return _bulkhead_manager


# Decorator for automatic bulkhead execution
def with_bulkhead(bulkhead_name: str, timeout: float | None = None):
    """Decorator to execute function within a bulkhead.

    Args:
        bulkhead_name: Name of bulkhead
        timeout: Optional timeout

    Returns:
        Decorated function
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            manager = await get_bulkhead_manager()
            return await manager.execute(bulkhead_name, func, *args, timeout=timeout, **kwargs)

        return wrapper

    return decorator


# Engine-specific decorator
def with_engine_bulkhead(engine_type: EngineType, timeout: float | None = None):
    """Decorator to execute function within engine-specific bulkhead.

    Args:
        engine_type: Type of engine
        timeout: Optional timeout

    Returns:
        Decorated function
    """
    bulkhead_name = {
        EngineType.RESUME: "RESUME_GENERATION",
        EngineType.OUTREACH: "OUTREACH_GENERATION",
    }[engine_type]

    return with_bulkhead(bulkhead_name, timeout)
