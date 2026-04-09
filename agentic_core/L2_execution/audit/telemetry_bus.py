"""C2 Telemetry Buses - Real-time control and async telemetry.

10C-REQ-133: Real-time control signals BUS D Deviation BUS E Anomaly
10C-REQ-134: Async telemetry data for learning BUS T
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable
import time
import queue


class BusType(Enum):
    """Telemetry bus types."""
    DEVIATION = auto()   # BUS D - Real-time control
    ANOMALY = auto()     # BUS E - Real-time control
    TELEMETRY = auto()   # BUS T - Async learning data


@dataclass
class BusMessage:
    """Message on telemetry bus."""
    bus_type: BusType
    signal_type: str
    payload: dict[str, Any]
    timestamp: float
    trace_id: str
    priority: int = 0


class TelemetryBus:
    """C2 Telemetry buses for real-time control and async learning.
    
    10C-REQ-133: BUS D Deviation and BUS E Anomaly - real-time control signals.
    10C-REQ-134: BUS T - async telemetry data for learning.
    """
    
    def __init__(self) -> None:
        self._queues: dict[BusType, queue.Queue[BusMessage]] = {
            bus: queue.Queue(maxsize=10000) for bus in BusType
        }
        self._handlers: dict[BusType, list[Callable[[BusMessage], None]]] = {
            bus: [] for bus in BusType
        }
        self._drop_counts: dict[BusType, int] = {bus: 0 for bus in BusType}
    
    def publish(
        self,
        bus_type: BusType,
        signal_type: str,
        payload: dict[str, Any],
        trace_id: str,
        priority: int = 0,
    ) -> bool:
        """Publish message to bus."""
        msg = BusMessage(
            bus_type=bus_type,
            signal_type=signal_type,
            payload=payload,
            timestamp=time.time(),
            trace_id=trace_id,
            priority=priority,
        )
        
        q = self._queues[bus_type]
        
        try:
            q.put_nowait(msg)
            
            if bus_type in (BusType.DEVIATION, BusType.ANOMALY):
                self._notify_handlers(bus_type, msg)
            
            return True
        except queue.Full:
            self._drop_counts[bus_type] += 1
            return False
    
    def _notify_handlers(self, bus_type: BusType, msg: BusMessage) -> None:
        """Notify handlers for real-time buses."""
        for handler in self._handlers[bus_type]:
            try:
                handler(msg)
            except (RuntimeError, ValueError, TypeError, KeyError):
                pass  # Continue notifying other handlers
    
    def subscribe(
        self,
        bus_type: BusType,
        handler: Callable[[BusMessage], None],
    ) -> None:
        """Subscribe to bus messages."""
        self._handlers[bus_type].append(handler)
    
    def drain(self, bus_type: BusType, max_messages: int = 100) -> list[BusMessage]:
        """Drain messages from async bus (T) for learning."""
        messages: list[BusMessage] = []
        q = self._queues[bus_type]
        
        for _ in range(max_messages):
            try:
                msg = q.get_nowait()
                messages.append(msg)
            except queue.Empty:
                break
        
        return messages
    
    def get_stats(self) -> dict[str, Any]:
        """Get bus statistics."""
        return {
            "queue_sizes": {
                bus.name: q.qsize() for bus, q in self._queues.items()
            },
            "drop_counts": {
                bus.name: count for bus, count in self._drop_counts.items()
            },
            "handler_counts": {
                bus.name: len(handlers) for bus, handlers in self._handlers.items()
            },
        }
