"""Event Bus - Event-driven backbone for reactive architecture.

This module implements a hybrid event bus supporting Redis Streams for production
and in-memory asyncio.Queue for development, enabling decoupled agent communication
with fault tolerance through existing infrastructure.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """System event types."""
    # Lifecycle Events
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    WORKFLOW_PAUSED = "WORKFLOW_PAUSED"
    WORKFLOW_RESUMED = "WORKFLOW_RESUMED"

    # Agent Events
    AGENT_THINKING = "AGENT_THINKING"
    AGENT_ACTING = "AGENT_ACTING"
    AGENT_CRITIQUING = "AGENT_CRITIQUING"
    AGENT_FAILED = "AGENT_FAILED"
    AGENT_COMPLETED = "AGENT_COMPLETED"

    # Data Events
    INSIGHT_DISCOVERED = "INSIGHT_DISCOVERED"
    ARTIFACT_GENERATED = "ARTIFACT_GENERATED"
    DATA_PROCESSED = "DATA_PROCESSED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"

    # System Events
    ERROR_OCCURRED = "ERROR_OCCURRED"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    CIRCUIT_BREAKER_OPENED = "CIRCUIT_BREAKER_OPENED"
    CIRCUIT_BREAKER_CLOSED = "CIRCUIT_BREAKER_CLOSED"

    # Business Events
    JOB_POSTING_RECEIVED = "JOB_POSTING_RECEIVED"
    RESUME_TAILORING_STARTED = "RESUME_TAILORING_STARTED"
    OUTREACH_MESSAGE_GENERATED = "OUTREACH_MESSAGE_GENERATED"
    INTERVIEW_PREP_COMPLETED = "INTERVIEW_PREP_COMPLETED"


class SystemEvent(BaseModel):
    """Immutable system event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    type: EventType
    source_component: str
    payload: dict[str, Any]
    timestamp: float = Field(default_factory=time.time)
    correlation_id: str | None = None  # Links related events
    causation_id: str | None = None   # The event that caused this one

    class Config:
        frozen = True  # Events are immutable

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "type": self.type.value,
            "source_component": self.source_component,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemEvent":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            SystemEvent instance
        """
        return cls(
            id=data["id"],
            trace_id=data["trace_id"],
            type=EventType(data["type"]),
            source_component=data["source_component"],
            payload=data["payload"],
            timestamp=data["timestamp"],
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id")
        )


class EventBus(ABC):
    """Abstract base class for event bus implementations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the event bus backend."""
        pass

    @abstractmethod
    async def publish(self, channel: str, event: SystemEvent) -> None:
        """Publish an event to a channel.

        Args:
            channel: Channel name
            event: Event to publish
        """
        pass

    @abstractmethod
    async def subscribe(
        self,
        channel: str,
        callback: Callable[[SystemEvent], Awaitable[None]]
    ) -> None:
        """Subscribe to events on a channel.

        Args:
            channel: Channel name
            callback: Async callback for events
        """
        pass

    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel.

        Args:
            channel: Channel name
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the event bus connection."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check health of event bus.

        Returns:
            Health status
        """
        pass


class MemoryEventBus(EventBus):
    """In-memory event bus using asyncio.Queue."""

    def __init__(self):
        """Initialize memory event bus."""
        self._queues: dict[str, asyncio.Queue] = {}
        self._subscribers: dict[str, list[Callable]] = {}
        self._workers: dict[str, asyncio.Task] = {}
        self._running = False
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "subscriber_errors": 0,
            "channels": 0
        }

        logger.info("Initialized MemoryEventBus")

    async def connect(self) -> None:
        """Connect to the event bus."""
        self._running = True
        logger.info("MemoryEventBus connected")

    async def publish(self, channel: str, event: SystemEvent) -> None:
        """Publish an event to a channel.

        Args:
            channel: Channel name
            event: Event to publish
        """
        if not self._running:
            raise RuntimeError("Event bus not connected")

        # Validate payload is JSON serializable
        try:
            json.dumps(event.payload)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Event payload is not JSON serializable: {e}")

        # Get or create queue for channel
        if channel not in self._queues:
            self._queues[channel] = asyncio.Queue()
            self._stats["channels"] += 1

        # Add event to queue
        await self._queues[channel].put(event)
        self._stats["events_published"] += 1

        # Start worker if needed
        if channel not in self._workers:
            self._workers[channel] = asyncio.create_task(
                self._worker_loop(channel)
            )

        logger.debug(f"Published event {event.id} to channel {channel}")

    async def subscribe(
        self,
        channel: str,
        callback: Callable[[SystemEvent], Awaitable[None]]
    ) -> None:
        """Subscribe to events on a channel.

        Args:
            channel: Channel name
            callback: Async callback for events
        """
        if channel not in self._subscribers:
            self._subscribers[channel] = []

        self._subscribers[channel].append(callback)
        logger.debug(f"Subscribed to channel {channel}")

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel.

        Args:
            channel: Channel name
        """
        if channel in self._subscribers:
            del self._subscribers[channel]
            logger.debug(f"Unsubscribed from channel {channel}")

    async def close(self) -> None:
        """Close the event bus."""
        self._running = False

        # Cancel all workers
        for task in self._workers.values():
            task.cancel()

        # Wait for workers to finish
        if self._workers:
            await asyncio.gather(*self._workers.values(), return_exceptions=True)

        self._workers.clear()
        self._queues.clear()
        self._subscribers.clear()

        logger.info("MemoryEventBus closed")

    async def health_check(self) -> dict[str, Any]:
        """Check health of event bus.

        Returns:
            Health status
        """
        return {
            "status": "healthy" if self._running else "stopped",
            "type": "memory",
            "channels": len(self._queues),
            "subscribers": sum(len(subs) for subs in self._subscribers.values()),
            "queue_sizes": {ch: q.qsize() for ch, q in self._queues.items()},
            "stats": self._stats.copy()
        }

    async def _worker_loop(self, channel: str) -> None:
        """Worker loop for processing events.

        Args:
            channel: Channel to process
        """
        queue = self._queues[channel]
        subscribers = self._subscribers.get(channel, [])

        while self._running:
            try:
                # Wait for event
                event = await queue.get()

                # Notify all subscribers
                if subscribers:
                    await self._notify_subscribers(event, subscribers)

                self._stats["events_processed"] += 1
                queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error for channel {channel}: {e}")

    async def _notify_subscribers(
        self,
        event: SystemEvent,
        subscribers: list[Callable]
    ) -> None:
        """Notify all subscribers of an event.

        Args:
            event: Event to publish
            subscribers: List of subscriber callbacks
        """
        tasks = []

        for callback in subscribers:
            task = asyncio.create_task(self._safe_notify(callback, event))
            tasks.append(task)

        # Wait for all notifications (with error isolation)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_notify(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
        event: SystemEvent
    ) -> None:
        """Safely notify a subscriber.

        Args:
            callback: Subscriber callback
            event: Event to publish
        """
        try:
            await callback(event)
        except Exception as e:
            self._stats["subscriber_errors"] += 1
            logger.error(f"Subscriber callback error: {e}", exc_info=True)


class RedisEventBus(EventBus):
    """Redis-based event bus using Redis Streams."""

    def __init__(
        self,
        connection_string: str,
        consumer_group: str = "agentic_workflow",
        consumer_name: str | None = None
    ):
        """Initialize Redis event bus.

        Args:
            connection_string: Redis connection string
            consumer_group: Consumer group name
            consumer_name: Unique consumer name
        """
        self.connection_string = connection_string
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name or f"consumer_{uuid.uuid4().hex[:8]}"

        self.redis: Any | None = None
        self._running = False
        self._subscribers: dict[str, list[Callable]] = {}
        self._readers: dict[str, asyncio.Task] = {}
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "subscriber_errors": 0,
            "reconnections": 0,
            "channels": 0
        }

        logger.info(f"Initialized RedisEventBus for {connection_string}")

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as redis

            # Create Redis client with connection pooling
            self.redis = redis.from_url(
                self.connection_string,
                decode_responses=True,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )

            # Test connection
            await self.redis.ping()

            self._running = True
            logger.info("RedisEventBus connected")

        except ImportError:
            raise ImportError("redis package required for RedisEventBus")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def publish(self, channel: str, event: SystemEvent) -> None:
        """Publish an event to a Redis stream.

        Args:
            channel: Channel name (stream key)
            event: Event to publish
        """
        if not self._running or not self.redis:
            raise RuntimeError("Event bus not connected")

        # Validate payload is JSON serializable
        try:
            json.dumps(event.payload)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Event payload is not JSON serializable: {e}")

        try:
            # Add to stream
            await self.redis.xadd(
                channel,
                event.to_dict(),
                maxlen=10000  # Trim stream to 10k entries
            )

            self._stats["events_published"] += 1
            logger.debug(f"Published event {event.id} to Redis stream {channel}")

        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")
            await self._handle_connection_error(e)
            raise

    async def subscribe(
        self,
        channel: str,
        callback: Callable[[SystemEvent], Awaitable[None]]
    ) -> None:
        """Subscribe to a Redis stream.

        Args:
            channel: Channel name (stream key)
            callback: Async callback for events
        """
        if not self._running:
            raise RuntimeError("Event bus not connected")

        # Create consumer group if it doesn't exist
        try:
            await self.redis.xgroup_create(
                channel,
                self.consumer_group,
                id="0",
                mkstream=True
            )
        except Exception as e:
            # Group might already exist
            if "BUSYGROUP" not in str(e):
                logger.warning(f"Failed to create consumer group: {e}")

        # Register subscriber
        if channel not in self._subscribers:
            self._subscribers[channel] = []
            self._stats["channels"] += 1

            # Start reader task
            self._readers[channel] = asyncio.create_task(
                self._reader_loop(channel)
            )

        self._subscribers[channel].append(callback)
        logger.debug(f"Subscribed to Redis stream {channel}")

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a Redis stream.

        Args:
            channel: Channel name
        """
        if channel in self._subscribers:
            del self._subscribers[channel]

            # Cancel reader task
            if channel in self._readers:
                self._readers[channel].cancel()
                del self._readers[channel]

            logger.debug(f"Unsubscribed from Redis stream {channel}")

    async def close(self) -> None:
        """Close Redis connection."""
        self._running = False

        # Cancel all readers
        for task in self._readers.values():
            task.cancel()

        if self._readers:
            await asyncio.gather(*self._readers.values(), return_exceptions=True)

        # Close Redis connection
        if self.redis:
            await self.redis.close()

        logger.info("RedisEventBus closed")

    async def health_check(self) -> dict[str, Any]:
        """Check health of Redis event bus.

        Returns:
            Health status
        """
        if not self._running or not self.redis:
            return {"status": "disconnected", "type": "redis"}

        try:
            # Test Redis connection
            await self.redis.ping()

            return {
                "status": "healthy",
                "type": "redis",
                "connection": self.connection_string,
                "consumer_group": self.consumer_group,
                "channels": len(self._subscribers),
                "stats": self._stats.copy()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "type": "redis",
                "error": str(e),
                "stats": self._stats.copy()
            }

    async def _reader_loop(self, channel: str) -> None:
        """Reader loop for processing Redis stream events.

        Args:
            channel: Stream to read from
        """
        subscribers = self._subscribers.get(channel, [])

        while self._running:
            try:
                # Read from stream
                messages = await self.redis.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    {channel: ">"},
                    count=10,
                    block=1000  # 1 second timeout
                )

                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        try:
                            # Parse event
                            event = SystemEvent.from_dict(fields)

                            # Notify subscribers
                            if subscribers:
                                await self._notify_subscribers(event, subscribers)

                            # Acknowledge message
                            await self.redis.xack(channel, self.consumer_group, msg_id)

                            self._stats["events_processed"] += 1

                        except Exception as e:
                            logger.error(f"Failed to process message {msg_id}: {e}")
                            # Still acknowledge to avoid reprocessing
                            await self.redis.xack(channel, self.consumer_group, msg_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Reader error for stream {channel}: {e}")
                await asyncio.sleep(1)  # Brief pause before retry

    async def _notify_subscribers(
        self,
        event: SystemEvent,
        subscribers: list[Callable]
    ) -> None:
        """Notify all subscribers of an event.

        Args:
            event: Event to publish
            subscribers: List of subscriber callbacks
        """
        tasks = []

        for callback in subscribers:
            task = asyncio.create_task(self._safe_notify(callback, event))
            tasks.append(task)

        # Wait for all notifications (with error isolation)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_notify(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
        event: SystemEvent
    ) -> None:
        """Safely notify a subscriber.

        Args:
            callback: Subscriber callback
            event: Event to publish
        """
        try:
            await callback(event)
        except Exception as e:
            self._stats["subscriber_errors"] += 1
            logger.error(f"Subscriber callback error: {e}", exc_info=True)

    async def _handle_connection_error(self, error: Exception) -> None:
        """Handle Redis connection errors.

        Args:
            error: Connection error
        """
        logger.warning(f"Redis connection error: {error}")

        # Try to reconnect
        for attempt in range(3):
            try:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                await self.connect()
                self._stats["reconnections"] += 1
                logger.info("Redis reconnected successfully")
                break
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")


def create_event_bus(connection_string: str | None = None) -> EventBus:
    """Create an event bus instance.

    Args:
        connection_string: Redis connection string or None for memory bus

    Returns:
        EventBus instance
    """
    if connection_string and connection_string.startswith("redis://"):
        return RedisEventBus(connection_string)
    else:
        return MemoryEventBus()


# Global event bus
_event_bus: EventBus | None = None
_bus_lock = asyncio.Lock()


async def get_event_bus() -> EventBus:
    """Get global event bus instance.

    Returns:
        EventBus instance
    """
    global _event_bus
    async with _bus_lock:
        if _event_bus is None:
            _event_bus = create_event_bus()
            await _event_bus.connect()
    return _event_bus


# Event publishing helpers
async def publish_event(
    event_type: EventType,
    source_component: str,
    payload: dict[str, Any],
    trace_id: str | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None
) -> None:
    """Publish a system event.

    Args:
        event_type: Type of event
        source_component: Component publishing the event
        payload: Event payload
        trace_id: Trace ID for tracking
        correlation_id: Correlation ID for related events
        causation_id: ID of event that caused this one
    """
    event = SystemEvent(
        type=event_type,
        source_component=source_component,
        payload=payload,
        trace_id=trace_id or str(uuid.uuid4()),
        correlation_id=correlation_id,
        causation_id=causation_id
    )

    bus = await get_event_bus()
    channel = f"events.{event_type.value.lower()}"
    await bus.publish(channel, event)


# Decorator for event publishing
def event_publisher(
    event_type: EventType,
    channel: str | None = None
):
    """Decorator to automatically publish events.

    Args:
        event_type: Type of event to publish
        channel: Optional channel override

    Returns:
        Decorated function
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Extract trace_id from first argument if it's a SignalEnvelope
            trace_id = None
            if args and hasattr(args[0], 'trace_id'):
                trace_id = args[0].trace_id

            # Publish start event
            await publish_event(
                event_type,
                func.__module__ + "." + func.__name__,
                {"status": "started", "args_count": len(args)},
                trace_id=trace_id
            )

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Publish success event
                await publish_event(
                    event_type,
                    func.__module__ + "." + func.__name__,
                    {"status": "completed", "success": True},
                    trace_id=trace_id,
                    causation_id=trace_id
                )

                return result

            except Exception as e:
                # Publish error event
                await publish_event(
                    EventType.ERROR_OCCURRED,
                    func.__module__ + "." + func.__name__,
                    {"status": "failed", "error": str(e)},
                    trace_id=trace_id,
                    causation_id=trace_id
                )
                raise

        return async_wrapper
    return decorator
