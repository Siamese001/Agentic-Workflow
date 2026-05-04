"""Event Bus Core - Stub implementation for test compatibility."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable


class EventType(Enum):
    """Types of system events."""

    AGENT_THINKING = "agent_thinking"
    AGENT_COMPLETED = "agent_completed"
    ERROR_OCCURRED = "error_occurred"
    SYSTEM_HEALTH = "system_health"


@dataclass
class SystemEvent:
    """System event."""

    type: EventType
    source_component: str
    payload: dict[str, Any]
    trace_id: str | None = None
    timestamp: float = field(default_factory=time.time)

    @property
    def id(self) -> str:
        """Generate unique ID for event."""
        return f"{self.source_component}:{self.timestamp}"


class EventBus:
    """Stub event bus."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable[[SystemEvent], Awaitable[None]]]] = {}
        self._running = False

    async def initialize(self) -> None:
        """Initialize event bus."""
        self._running = True

    async def publish(self, channel: str, event: SystemEvent) -> bool:
        """Publish event to channel."""
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                await callback(event)
        return True

    async def subscribe(self, channel: str, callback: Callable[[SystemEvent], Awaitable[None]]) -> None:
        """Subscribe to channel."""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from channel."""
        if channel in self._subscribers:
            del self._subscribers[channel]

    async def close(self) -> None:
        """Close event bus."""
        self._running = False
        self._subscribers.clear()

    async def health_check(self) -> dict[str, Any]:
        """Check health status."""
        return {
            "status": "healthy" if self._running else "stopped",
            "channels": len(self._subscribers),
        }


_event_bus: EventBus | None = None


async def get_event_bus() -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
        await _event_bus.initialize()
    return _event_bus


__all__ = ["EventBus", "EventType", "SystemEvent", "get_event_bus"]
