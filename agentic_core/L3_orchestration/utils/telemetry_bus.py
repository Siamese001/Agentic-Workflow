from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any


class BusType(str, Enum):
    TELEMETRY = "telemetry"


@dataclass
class BusMessage:
    bus_type: BusType
    signal_type: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        self.bus_type = self.bus_type if isinstance(self.bus_type, BusType) else BusType.TELEMETRY
        self.signal_type = str(self.signal_type or "")
        self.payload = dict(self.payload or {})


class TelemetryBus:
    def __init__(self, max_messages: int = 10_000) -> None:
        self._messages: list[BusMessage] = []
        self._lock = Lock()
        self._max_messages = max(1, int(max_messages))

    def publish(self, message: BusMessage) -> None:
        normalized = message if isinstance(message, BusMessage) else BusMessage(**dict(message or {}))
        with self._lock:
            self._messages.append(normalized)
            overflow = len(self._messages) - self._max_messages
            if overflow > 0:
                del self._messages[:overflow]

    def qsize(self, bus_type: BusType | None = None) -> int:
        with self._lock:
            if bus_type is None:
                return len(self._messages)
            return sum(1 for message in self._messages if message.bus_type == bus_type)

    def snapshot(self, bus_type: BusType | None = None) -> list[BusMessage]:
        with self._lock:
            messages = list(self._messages)
        if bus_type is None:
            return messages
        return [message for message in messages if message.bus_type == bus_type]

    def clear(self, bus_type: BusType | None = None) -> None:
        with self._lock:
            if bus_type is None:
                self._messages.clear()
                return
            self._messages = [message for message in self._messages if message.bus_type != bus_type]

    def drain(self, bus_type: BusType, max_messages: int = 100) -> list[BusMessage]:
        max_messages = max(0, int(max_messages))
        with self._lock:
            drained: list[BusMessage] = []
            kept: list[BusMessage] = []
            for message in self._messages:
                if message.bus_type == bus_type and len(drained) < max_messages:
                    drained.append(message)
                else:
                    kept.append(message)
            self._messages = kept
            return drained


_TELEMETRY_BUS = TelemetryBus()


def get_telemetry_bus() -> TelemetryBus:
    return _TELEMETRY_BUS
