"""Telemetry utilities.

Zero-Ambiguity Standard: Renamed from SystemTelemetry.py to system_telemetry_util.py.
Category: UTILITY (Telemetry collector).

Provides a lightweight in-process telemetry collector with bounded retention,
deterministic event identifiers, and thread-safe singleton access.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import Counter, deque
from dataclasses import dataclass
from typing import Any

get_clock: Any = None

try:
    from agentic_core.L2_execution.utils.providers import (
        get_clock,
    )  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
except ImportError:
    get_clock = None


@dataclass(frozen=True)
class TelemetryEvent:
    """Normalized telemetry event."""

    event_id: str
    status: str
    component: str
    operation: str
    latency_ms: float
    recorded_at: float
    metadata: dict[str, Any]
    error_type: str = ""
    error_message: str = ""
    breaker_name: str = ""
    breaker_state: str = ""


class OperationStatus:
    """Operation status enumeration."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CIRCUIT_BREAKER = "circuit_breaker"


class SystemTelemetry:
    """Thread-safe bounded telemetry collector.

    The collector retains only the most recent ``max_events`` records to avoid
    unbounded memory growth in long-lived processes.
    """

    def __init__(self, **kwargs: Any) -> None:
        max_events = kwargs.get("max_events", 1000)
        self._max_events = max(1, int(max_events))
        self._component_filter = set(kwargs.get("component_filter", []) or [])
        self._events: deque[TelemetryEvent] = deque(maxlen=self._max_events)
        self._lock = threading.RLock()
        self._counters: Counter[str] = Counter()
        self._component_counters: dict[str, Counter[str]] = {}

    def _now_epoch(self) -> float:
        if get_clock is not None:
            try:
                return float(get_clock().now_epoch())
            except (
                AttributeError,
                RuntimeError,
                TypeError,
                ValueError,
            ):  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow
                pass
        return time.time()

    @staticmethod
    def _normalize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
        if not metadata:
            return {}
        if isinstance(metadata, dict):
            return dict(metadata)
        return {"value": metadata}

    def _should_record(self, component: str) -> bool:
        return not self._component_filter or component in self._component_filter

    def _build_event_id(
        self,
        *,
        status: str,
        component: str,
        operation: str,
        latency_ms: float,
        metadata: dict[str, Any],
        error_type: str = "",
        error_message: str = "",
        breaker_name: str = "",
        breaker_state: str = "",
    ) -> str:
        payload = {
            "status": status,
            "component": component,
            "operation": operation,
            "latency_ms": round(float(latency_ms), 6),
            "metadata": metadata,
            "error_type": error_type,
            "error_message": error_message,
            "breaker_name": breaker_name,
            "breaker_state": breaker_state,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return f"tel-{digest[:16]}"

    def _record(
        self,
        *,
        status: str,
        component: str,
        operation: str,
        latency_ms: float,
        metadata: dict[str, Any] | None = None,
        error_type: str = "",
        error_message: str = "",
        breaker_name: str = "",
        breaker_state: str = "",
    ) -> TelemetryEvent | None:
        component = component or "unknown_component"
        operation = operation or "unknown_operation"
        if not self._should_record(component):
            return None

        normalized_metadata = self._normalize_metadata(metadata)
        event = TelemetryEvent(
            event_id=self._build_event_id(
                status=status,
                component=component,
                operation=operation,
                latency_ms=latency_ms,
                metadata=normalized_metadata,
                error_type=error_type,
                error_message=error_message,
                breaker_name=breaker_name,
                breaker_state=breaker_state,
            ),
            status=status,
            component=component,
            operation=operation,
            latency_ms=max(0.0, float(latency_ms)),
            recorded_at=self._now_epoch(),
            metadata=normalized_metadata,
            error_type=error_type,
            error_message=error_message,
            breaker_name=breaker_name,
            breaker_state=breaker_state,
        )
        with self._lock:
            self._events.append(event)
            self._counters[status] += 1
            component_counter = self._component_counters.setdefault(component, Counter())
            component_counter[status] += 1
        return event

    def log_success(
        self,
        component: str,
        operation: str,
        latency_ms: float,
        metadata: dict[str, Any] | None = None,
    ) -> TelemetryEvent | None:
        """Log a successful operation."""
        return self._record(
            status=OperationStatus.SUCCESS,
            component=component,
            operation=operation,
            latency_ms=latency_ms,
            metadata=metadata,
        )

    def log_failure(
        self,
        component: str,
        operation: str,
        latency_ms: float,
        error_type: str,
        error_message: str,
        metadata: dict[str, Any] | None = None,
    ) -> TelemetryEvent | None:
        """Log a failed operation."""
        return self._record(
            status=OperationStatus.FAILURE,
            component=component,
            operation=operation,
            latency_ms=latency_ms,
            metadata=metadata,
            error_type=error_type or "unknown_error",
            error_message=error_message or "",
        )

    def log_circuit_breaker(
        self,
        component: str,
        breaker_name: str,
        state: str,
        metadata: dict[str, Any] | None = None,
    ) -> TelemetryEvent | None:
        """Log circuit breaker state change."""
        return self._record(
            status=OperationStatus.CIRCUIT_BREAKER,
            component=component,
            operation="circuit_breaker",
            latency_ms=0.0,
            metadata=metadata,
            breaker_name=breaker_name or "default_breaker",
            breaker_state=state or "unknown",
        )

    def get_recent_events(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Return the most recent events as dictionaries."""
        with self._lock:
            events = list(self._events)
        if limit is not None and limit >= 0:
            events = events[-limit:]
        return [event.__dict__.copy() for event in events]

    def get_summary(self) -> dict[str, Any]:
        """Return an aggregate telemetry summary."""
        with self._lock:
            events = list(self._events)
            counters = dict(self._counters)
            component_breakdown = {
                component: dict(counter) for component, counter in self._component_counters.items()
            }
        average_latency_ms = sum(event.latency_ms for event in events) / len(events) if events else 0.0
        return {
            "max_events": self._max_events,
            "retained_events": len(events),
            "status_counts": counters,
            "component_breakdown": component_breakdown,
            "average_latency_ms": round(average_latency_ms, 3),
        }


_TELEMETRY_SINGLETON: SystemTelemetry | None = None
_TELEMETRY_LOCK = threading.Lock()


def get_telemetry(**kwargs: Any) -> SystemTelemetry:
    """Get the process-level telemetry instance.

    The first call wins for singleton configuration. Later calls reuse the
    existing collector to preserve in-process aggregation semantics.
    """
    global _TELEMETRY_SINGLETON
    if _TELEMETRY_SINGLETON is None:
        with _TELEMETRY_LOCK:
            if _TELEMETRY_SINGLETON is None:
                _TELEMETRY_SINGLETON = SystemTelemetry(**kwargs)
    return _TELEMETRY_SINGLETON
