"""Bulkhead Manager - Resource isolation for execution pools.

This module implements the bulkhead pattern to prevent resource starvation
between different engine types and priorities, ensuring that high-priority
tasks are not blocked by lower-priority ones.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Callable, Any, Optional, Dict, Set
from collections import deque

# Assuming CircuitBreaker and CircuitBreakerConfig are defined elsewhere
# from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker_registry

# Placeholder for CircuitBreaker if not available in the provided context
class CircuitBreaker:
    def __init__(self, config):
        pass
    def can_execute(self):
        return True
    def record_failure(self, exception, duration):
        pass
    @property
    def state(self):
        class State:
            value = "closed"
        return State()

class CircuitBreakerConfig:
    def __init__(self, failure_threshold, TIMEOUT, failure_rate_threshold):
        pass

async def get_circuit_breaker_registry():
    class Registry:
        async def get_circuit_breaker(self, name, config):
            return CircuitBreaker(config)
    return Registry()

# Placeholder for EngineType if not available in the provided context
class EngineType(str, Enum):
    RESUME = "RESUME"
    OUTREACH = "OUTREACH"

LOGGER = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class BulkheadConfig:
    """Configuration for a bulkhead."""
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
        self.REASON = reason

class Bulkhead:
    """A single bulkhead with isolated resources."""

    def __init__(self, name: str, config: BulkheadConfig, enable_circuit_breaker: bool = True):
        """Initialize bulkhead.

        Args:
            name: Bulkhead name
            config: Bulkhead configuration
            enable_circuit_breaker: Whether to enable circuit breaker
        """
        self.NAME = name
        self.CONFIG = config
        self.SEMAPHORE = asyncio.Semaphore(config.max_concurrency)
        self.QUEUE = asyncio.Queue(maxsize=config.queue_size)
        self.METRICS = BulkheadMetrics(
            name=name,
            max_concurrency=config.max_concurrency,
            queue_size=config.queue_size
        )

        # Task tracking
        self._active_tasks: Set[asyncio.Task] = set()
        self._wait_times: deque = deque(maxlen=1000)
        self._completed_count = 0
        self._rejected_count = 0

        # Circuit breaker
        self.circuit_breaker: Optional[CircuitBreaker] = None
        if enable_circuit_breaker:
            self._circuit_breaker_config = CircuitBreakerConfig(
                failure_threshold=max(3, config.max_concurrency // 2),
                TIMEOUT=60.0,
                failure_rate_threshold=0.5
            )

        LOGGER.info(f"Created bulkhead '{name}' with max_concurrency={config.max_concurrency}")

    async def _get_circuit_breaker(self) -> Optional[CircuitBreaker]:
        """Get or create circuit breaker.

        Returns:
            CircuitBreaker instance if enabled
        """
        if self.circuit_breaker is None and hasattr(self, '_circuit_breaker_config'):
            REGISTRY = await get_circuit_breaker_registry()
            self.circuit_breaker = await REGISTRY.get_circuit_breaker(
                f"bulkhead_{self.NAME.lower()}",  # Use lowercase name for consistency
                self._circuit_breaker_config
            )
        return self.circuit_breaker

    async def execute(
        self,
        coro: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
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
                self.NAME,
                f"Circuit breaker is {circuit_breaker.state.value}"
            )

        start_time = time.time()

        # Try to acquire semaphore with timeout
        effective_timeout = timeout or self.CONFIG.timeout_seconds

        try:
            # Check if we can queue the task
            if self.QUEUE.full():
                self._rejected_count += 1
                self.METRICS.rejected_tasks = self._rejected_count
                if circuit_breaker:
                    circuit_breaker.record_failure(
                        ResourceExhaustedError(self.NAME, "Queue full"),
                        0
                    )
                raise ResourceExhaustedError(
                    self.NAME,
                    f"Queue full ({self.QUEUE.qsize()}/{self.CONFIG.queue_size})"
                )

            # Add to queue
            await self.QUEUE.put(None)

            # Acquire semaphore
            try:
                await asyncio.wait_for(self.SEMAPHORE.acquire(), timeout=effective_timeout)
            except asyncio.TimeoutError:
                self.QUEUE.get_nowait()  # Remove from queue
                self._rejected_count += 1
                self.METRICS.rejected_tasks = self._rejected_count
                if circuit_breaker:
                    circuit_breaker.record_failure(
                        asyncio.TimeoutError(f"Timeout acquiring semaphore after {effective_timeout}s"),
                        effective_timeout * 1000
                    )
                raise ResourceExhaustedError(
                    self.NAME,
                    f"Timeout acquiring semaphore after {effective_timeout}s"
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
            if not self.QUEUE.empty():
                try:
                    self.QUEUE.get_nowait()
                except asyncio.QueueEmpty:
                    pass # Should not happen if logic is correct, but good practice
            self.SEMAPHORE.release()
            self._update_metrics()

    async def _execute_with_circuit_breaker(
        self,
        coro: Callable,
        *args,
        **kwargs
    ) -> Any:
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
            try:
                return await circuit_breaker.call(coro, *args, **kwargs)
            except Exception as e:
                # Circuit breaker's call method should handle recording failures
                raise
        else:
            # Execute normally
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                LOGGER.error(f"Task in bulkhead '{self.NAME}' failed: {e}")
                raise

    def _update_metrics(self) -> None:
        """Update bulkhead metrics."""
        self.METRICS.active_tasks = len(self._active_tasks)
        self.METRICS.queued_tasks = self.QUEUE.qsize()
        self.METRICS.completed_tasks = self._completed_count
        self.METRICS.rejected_tasks = self._rejected_count

        if self._wait_times:
            self.METRICS.avg_wait_time_ms = sum(self._wait_times) / len(self._wait_times)
            self.METRICS.max_wait_time_ms = max(self._wait_times)

        # Calculate utilization
        if self.CONFIG.max_concurrency > 0:
            self.METRICS.utilization_percent = (
                self.METRICS.active_tasks / self.CONFIG.max_concurrency
            ) * 100

        self.METRICS.last_updated = datetime.utcnow()

    def try_acquire(self) -> bool:
        """Try to acquire without blocking.

        Returns:
            True if acquired, False otherwise
        """
        return self.SEMAPHORE._value > 0 and not self.QUEUE.full()

    def get_metrics(self) -> BulkheadMetrics:
        """Get current metrics.

        Returns:
            Bulkhead metrics
        """
        self._update_metrics()
        return self.METRICS

    async def wait_for_available(self, timeout: float = 1.0) -> bool:
        """Wait for resources to become available.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if resources available, False if timeout
        """
        try:
            await asyncio.wait_for(
                self.QUEUE.join(),
                timeout=timeout
            )
            return self.try_acquire()
        except asyncio.TimeoutError:
            return False

class BulkheadManager:
    """Manages multiple bulkheads for resource isolation."""

    def __init__(self):
        """Initialize bulkhead manager."""
        self.bulkheads: Dict[str, Bulkhead] = {}
        self._global_metrics = {
            "total_active_tasks": 0,
            "total_queued_tasks": 0,
            "bulkhead_count": 0
        }

        # Default configurations
        self._default_configs = {
            "RESUME_GENERATION": BulkheadConfig(
                max_concurrency=5,
                priority=TaskPriority.HIGH,
                queue_size=50
            ),
            "OUTREACH_GENERATION": BulkheadConfig(
                max_concurrency=10,
                priority=TaskPriority.MEDIUM,
                queue_size=100
            ),
            "BACKGROUND_ANALYSIS": BulkheadConfig(
                max_concurrency=2,
                priority=TaskPriority.LOW,
                queue_size=20
            ),
            "CRITICAL_OPERATIONS": BulkheadConfig(
                max_concurrency=3,
                priority=TaskPriority.CRITICAL,
                queue_size=10,
                timeout_seconds=60.0
            )
        }

        # Initialize default bulkheads
        for name, config in self._default_configs.items():
            self.create_bulkhead(name, config)

        LOGGER.info(f"Initialized BulkheadManager with {len(self.bulkheads)} bulkheads")

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
        self.bulkheads[name.upper()] = bulkhead # Store with uppercase name
        self._global_metrics["bulkhead_count"] += 1

        LOGGER.info(f"Created bulkhead '{name}'")
        return bulkhead

    def get_bulkhead(self, name: str) -> Optional[Bulkhead]:
        """Get a bulkhead by name.

        Args:
            name: Bulkhead name

        Returns:
            Bulkhead if found
        """
        return self.bulkheads.get(name.upper()) # Use uppercase for lookup

    def remove_bulkhead(self, name: str) -> bool:
        """Remove a bulkhead.

        Args:
            name: Bulkhead name

        Returns:
            True if removed
        """
        if name.upper() in self.bulkheads:
            del self.bulkheads[name.upper()]
            self._global_metrics["bulkhead_count"] -= 1
            LOGGER.info(f"Removed bulkhead '{name}'")
            return True
        return False

    async def execute(
        self,
        bulkhead_name: str,
        coro: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs
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
            raise ResourceExhaustedError(
                bulkhead_name,
                "Bulkhead not found"
            )

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
        else: # Assuming OUTREACH is the only other type, or default
            return "OUTREACH_GENERATION"

    async def execute_for_engine(
        self,
        engine_type: EngineType,
        coro: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs
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

    def get_all_metrics(self) -> Dict[str, Any]:
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

        self._global_metrics.update({
            "total_active_tasks": total_active,
            "total_queued_tasks": total_queued
        })

        return {
            "global": self._global_metrics,
            "bulkheads": bulkhead_metrics
        }

    def log_utilization(self) -> None:
        """Log current utilization of all bulkheads."""
        metrics = self.get_all_metrics()

        LOGGER.info("=== Bulkhead Utilization ===")
        LOGGER.info(f"Total Active: {metrics['global']['total_active_tasks']}")
        LOGGER.info(f"Total Queued: {metrics['global']['total_queued_tasks']}")

        for name, bulkhead_metrics in metrics["bulkheads"].items():
            LOGGER.info(
                f"{name}: {bulkhead_metrics.active_tasks}/{bulkhead_metrics.max_concurrency} "
                f"({bulkhead_metrics.utilization_percent:.1f}%) "
                f"Queue: {bulkhead_metrics.queued_tasks}/{bulkhead_metrics.queue_size}"
            )

    async def health_check(self) -> Dict[str, Any]:
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
            if metrics.queued_tasks > metrics.queue_size * 0.8:
                issues.append(f"{name}: Queue buildup ({metrics.queued_tasks}/{metrics.queue_size})")

            # Check for high rejection rate
            if metrics.completed_tasks > 0:
                rejection_rate = metrics.rejected_tasks / (metrics.completed_tasks + metrics.rejected_tasks)
                if rejection_rate > 0.1:  # 10% rejection rate
                    issues.append(f"{name}: High rejection rate ({rejection_rate:.1%})")

        return {
            "status": "healthy" if not issues else "degraded",
            "bulkheads": len(self.bulkheads),
            "issues": issues,
            "metrics": self.get_all_metrics()
        }

# Global bulkhead manager
_bulkhead_manager: Optional[BulkheadManager] = None
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
def with_bulkhead(bulkhead_name: str, timeout: Optional[float] = None):
    """Decorator to execute function within a bulkhead.

    Args:
        bulkhead_name: Name of bulkhead
        timeout: Optional timeout

    Returns:
        Decorated function
    """
    def decorator(func):
        """TODO: Add docstring."""

        async def wrapper(*args, **kwargs):
            """Docstring."""
            manager = await get_bulkhead_manager()
            return await manager.execute(bulkhead_name, func, *args, timeout=timeout, **kwargs)
        return wrapper
    return decorator

# Engine-specific decorator
def with_engine_bulkhead(engine_type: EngineType, timeout: Optional[float] = None):
    """Decorator to execute function within engine-specific bulkhead.

    Args:
        engine_type: Type of engine
        timeout: Optional timeout

    Returns:
        Decorated function
    """
    bulkhead_name_map = {
        EngineType.RESUME: "RESUME_GENERATION",
        EngineType.OUTREACH: "OUTREACH_GENERATION"
    }
    if engine_type not in bulkhead_name_map:
        raise ValueError(f"Unknown engine type: {engine_type}")

    return with_bulkhead(bulkhead_name_map[engine_type], timeout)