"""Event Bus Integration - Hardened event-driven communication.

This module provides integration between the Event Bus and the hardened
infrastructure, ensuring all event operations go through bulkheads,
circuit breakers, and retry policies.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from .bulkhead_manager import BulkheadManager, TaskPriority, get_bulkhead_manager
from .circuit_breaker import CircuitBreakerConfig, get_circuit_breaker_registry
from .core.event_bus import EventBus, EventType, SystemEvent, get_event_bus
from .dead_letter_queue import FailureReason, get_dead_letter_queue
from .retry_policy import RetryConfig, get_retry_executor

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class HardenedEventBus:
    """Event Bus wrapped with hardened infrastructure."""

    def __init__(
        self,
        event_bus: EventBus | None = None,
        bulkhead_manager: BulkheadManager | None = None,
    ):
        """Initialize hardened event bus.

        Args:
            event_bus: Event bus instance
            bulkhead_manager: Bulkhead manager instance
        """
        self.event_bus = event_bus
        self.bulkhead_manager = bulkhead_manager
        self._stats = {
            "events_published": 0,
            "events_failed": 0,
            "events_retried": 0,
            "bulkhead_rejections": 0,
        }

        logger.info("Initialized HardenedEventBus")

    async def initialize(self) -> None:
        """Initialize all components."""
        if not self.event_bus:
            self.event_bus = await get_event_bus()

        if not self.bulkhead_manager:
            self.bulkhead_manager = await get_bulkhead_manager()

        # Register bulkheads for event operations
        await self._register_bulkheads()

        # Register circuit breakers
        await self._register_circuit_breakers()

        # Register retry policies
        await self._register_retry_policies()

        logger.info("HardenedEventBus initialized")

    async def publish(
        self,
        channel: str,
        event: SystemEvent,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> bool:
        """Publish an event with hardened protection.

        Args:
            channel: Channel name
            event: Event to publish
            priority: Task priority for bulkhead

        Returns:
            True if published successfully
        """
        try:
            # Execute through bulkhead with circuit breaker and retry
            await self.bulkhead_manager.execute(
                self._publish_with_retry,
                channel,
                event,
                bulkhead_name="event_publish",
                priority=priority,
            )

            self._stats["events_published"] += 1
            return True

        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self._stats["events_failed"] += 1

            # Send to dead letter queue
            dlq = await get_dead_letter_queue()
            await dlq.add_failed_envelope(
                event,  # Using event as envelope-like object
                FailureReason.PROCESSING_ERROR,
                "HardenedEventBus.publish",
                str(e),
            )

            logger.error(f"Failed to publish event {event.id}: {e}")
            return False

    async def subscribe(
        self,
        channel: str,
        callback: Callable[[SystemEvent], Awaitable[None]],
    ) -> None:
        """Subscribe to events with hardened protection.

        Args:
            channel: Channel name
            callback: Event callback
        """
        # Wrap callback with hardened processing
        hardened_callback = self._wrap_callback(callback)

        # Subscribe through event bus
        await self.event_bus.subscribe(channel, hardened_callback)

        logger.info(f"Subscribed to channel {channel} with hardened processing")

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from events.

        Args:
            channel: Channel name
        """
        await self.event_bus.unsubscribe(channel)
        logger.info(f"Unsubscribed from channel {channel}")

    async def close(self) -> None:
        """Close the hardened event bus."""
        if self.event_bus:
            await self.event_bus.close()

        logger.info("HardenedEventBus closed")

    async def health_check(self) -> dict[str, Any]:
        """Check health of hardened event bus.

        Returns:
            Health status
        """
        # Get event bus health
        event_bus_health = await self.event_bus.health_check()

        # Get bulkhead stats
        bulkhead_stats = self.bulkhead_manager.get_all_metrics()

        # Combine results
        return {
            "event_bus": event_bus_health,
            "bulkheads": bulkhead_stats,
            "stats": self._stats.copy(),
        }

    async def _register_bulkheads(self) -> None:
        """Register bulkheads for event operations."""
        # Bulkhead for publishing events
        await self.bulkhead_manager.create_bulkhead(
            "event_publish",
            max_concurrency=10,
            queue_size=100,
            priority=TaskPriority.HIGH,
        )

        # Bulkhead for processing events
        await self.bulkhead_manager.create_bulkhead(
            "event_process",
            max_concurrency=20,
            queue_size=200,
            priority=TaskPriority.MEDIUM,
        )

        logger.debug("Registered event bus bulkheads")

    async def _register_circuit_breakers(self) -> None:
        """Register circuit breakers for event operations."""
        registry = await get_circuit_breaker_registry()

        # Circuit breaker for publishing
        await registry.get_circuit_breaker(
            "event_publish",
            CircuitBreakerConfig(failure_threshold=THRESHOLD, timeout=DEFAULT_TIMEOUT, failure_rate_threshold=THRESHOLD),
        )

        # Circuit breaker for processing
        await registry.get_circuit_breaker(
            "event_process",
            CircuitBreakerConfig(failure_threshold=THRESHOLD, timeout=DEFAULT_TIMEOUT, failure_rate_threshold=THRESHOLD),
        )

        logger.debug("Registered event bus circuit breakers")

    async def _register_retry_policies(self) -> None:
        """Register retry policies for event operations."""
        executor = await get_retry_executor()

        # Retry policy for publishing
        executor.register_policy(
            "event_publish",
            RetryConfig(max_attempts=3, base_delay=0.5, max_delay=5.0),
        )

        # Retry policy for processing
        executor.register_policy(
            "event_process",
            RetryConfig(max_attempts=5, base_delay=1.0, max_delay=10.0),
        )

        logger.debug("Registered event bus retry policies")

    async def _publish_with_retry(self, channel: str, event: SystemEvent) -> None:
        """Publish event with retry policy.

        Args:
            channel: Channel name
            event: Event to publish
        """
        executor = await get_retry_executor()
        await executor.execute(self.event_bus.publish, channel, event, policy="event_publish")

    def _wrap_callback(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
    ) -> Callable[[SystemEvent], Awaitable[None]]:
        """Wrap callback with hardened processing.

        Args:
            callback: Original callback

        Returns:
            Hardened callback
        """

        async def hardened_callback(event: SystemEvent) -> None:
            try:
                # Execute through bulkhead
                await self.bulkhead_manager.execute(
                    self._process_event,
                    callback,
                    event,
                    bulkhead_name="event_process",
                )

            except Exception as e:
                # Log error but don't crash
                logger.error(f"Failed to process event {event.id}: {e}")

                # Send to dead letter queue
                dlq = await get_dead_letter_queue()
                await dlq.add_failed_envelope(
                    event,
                    FailureReason.PROCESSING_ERROR,
                    "HardenedEventBus.process",
                    str(e),
                )

        return hardened_callback

    async def _process_event(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
        event: SystemEvent,
    ) -> None:
        """Process event with retry policy.

        Args:
            callback: Event callback
            event: Event to process
        """
        executor = await get_retry_executor()
        await executor.execute(callback, event, policy="event_process")


# Global hardened event bus
_hardened_bus: HardenedEventBus | None = None
_bus_lock = asyncio.Lock()


async def get_hardened_event_bus() -> HardenedEventBus:
    """Get global hardened event bus instance.

    Returns:
        HardenedEventBus instance
    """
    global _hardened_bus
    async with _bus_lock:
        if _hardened_bus is None:
            _hardened_bus = HardenedEventBus()
            await _hardened_bus.initialize()
    return _hardened_bus


# Event publishing helpers with hardening
async def publish_hardened_event(
    event_type: EventType,
    source_component: str,
    payload: dict[str, Any],
    trace_id: str | None = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> bool:
    """Publish a hardened system event.

    Args:
        event_type: Type of event
        source_component: Component publishing the event
        payload: Event payload
        trace_id: Trace ID for tracking
        priority: Task priority

    Returns:
        True if published successfully
    """
    from .core.event_bus import SystemEvent

    # Create event
    event = SystemEvent(
        type=event_type,
        source_component=source_component,
        payload=payload,
        trace_id=trace_id,
    )

    # Publish through hardened bus
    bus = await get_hardened_event_bus()
    channel = f"events.{event_type.value.lower()}"

    return await bus.publish(channel, event, priority)


# Event subscription helpers with hardening
async def subscribe_to_events(
    event_type: EventType,
    callback: Callable[[SystemEvent], Awaitable[None]],
) -> None:
    """Subscribe to events with hardened processing.

    Args:
        event_type: Type of event to subscribe to
        callback: Event callback
    """
    bus = await get_hardened_event_bus()
    channel = f"events.{event_type.value.lower()}"

    await bus.subscribe(channel, callback)


# Decorator for hardened event publishing
def hardened_event_publisher(event_type: EventType, priority: TaskPriority = TaskPriority.MEDIUM):
    """Decorator to automatically publish hardened events.

    Args:
        event_type: Type of event to publish
        priority: Task priority for publishing

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Extract trace_id from first argument if it's a SignalEnvelope
            trace_id = None
            if args and hasattr(args[0], "trace_id"):
                trace_id = args[0].trace_id

            # Publish start event
            await publish_hardened_event(
                EventType.AGENT_THINKING,
                func.__module__ + "." + func.__name__,
                {"status": "started", "args_count": len(args)},
                trace_id=trace_id,
                priority=priority,
            )

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Publish success event
                await publish_hardened_event(
                    EventType.AGENT_COMPLETED,
                    func.__module__ + "." + func.__name__,
                    {"status": "completed", "success": True},
                    trace_id=trace_id,
                    priority=priority,
                )

                return result

            except Exception as e:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                # Publish error event
                await publish_hardened_event(
                    EventType.ERROR_OCCURRED,
                    func.__module__ + "." + func.__name__,
                    {"status": "failed", "error": str(e)},
                    trace_id=trace_id,
                    priority=TaskPriority.HIGH,  # High priority for errors
                )
                raise

        return async_wrapper

    return decorator
