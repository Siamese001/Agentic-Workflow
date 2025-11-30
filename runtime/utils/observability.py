"""
Runtime observability module.

Provides event recording, exception tracking, metrics collection,
and monitoring capabilities for the agentic system.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
import logging
import uuid
import traceback

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of observability events."""

    MODEL_INVOCATION = "model_invocation"
    TOOL_EXECUTION = "tool_execution"
    DAG_EXECUTION = "dag_execution"
    ERROR_OCCURRED = "error_occurred"
    SAFETY_VIOLATION = "safety_violation"
    PERFORMANCE_METRIC = "performance_metric"
    USER_INTERACTION = "user_interaction"
    SYSTEM_EVENT = "system_event"


class SeverityLevel(str, Enum):
    """Severity levels for events and errors."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ObservabilityEvent:
    """Structured observability event."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.SYSTEM_EVENT
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    severity: SeverityLevel = SeverityLevel.INFO
    source: str = "unknown"
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "source": self.source,
            "message": self.message,
            "data": self._sanitize_data(self.data),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "tags": self.tags
        }

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data to remove sensitive information."""
        sanitized = {}
        sensitive_keys = {"password", "token", "api_key", "secret", "key"}

        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value

        return sanitized


class ObservabilityManager:
    """Manages observability events and metrics."""

    def __init__(self, max_events: int = 10000):
        """Initialize observability manager."""
        self.events: List[ObservabilityEvent] = []
        self.max_events = max_events

    def record_event(
        self,
        event_type: EventType,
        message: str,
        source: str = "unknown",
        severity: SeverityLevel = SeverityLevel.INFO,
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Record an observability event."""
        event = ObservabilityEvent(
            event_type=event_type,
            message=message,
            source=source,
            severity=severity,
            data=data or {},
            user_id=user_id,
            session_id=session_id,
            task_id=task_id,
            tags=tags or []
        )

        self.events.append(event)

        # Maintain max size
        if len(self.events) > self.max_events:
            self.events = self.events[-int(self.max_events * 0.8):]

        logger.info(f"Recorded event: {event_type.value} - {message}")
        return event.event_id

    def record_exception(
        self,
        exception: Exception,
        source: str = "unknown",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record an exception event."""
        data = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc()
        }

        if additional_data:
            data.update(additional_data)

        return self.record_event(
            event_type=EventType.ERROR_OCCURRED,
            message=f"Exception in {source}: {str(exception)}",
            source=source,
            severity=SeverityLevel.ERROR,
            data=data,
            user_id=user_id,
            session_id=session_id,
            task_id=task_id,
            tags=["exception", "error"]
        )

    def get_events(
        self,
        event_type: Optional[EventType] = None,
        severity: Optional[SeverityLevel] = None,
        source: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ObservabilityEvent]:
        """Get filtered events."""
        filtered = self.events

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if severity:
            filtered = [e for e in filtered if e.severity == severity]

        if source:
            filtered = [e for e in filtered if e.source == source]

        # Sort by timestamp (newest first)
        filtered.sort(key=lambda e: e.timestamp, reverse=True)

        if limit:
            filtered = filtered[:limit]

        return filtered

    def get_statistics(self) -> Dict[str, Any]:
        """Get observability statistics."""
        total_events = len(self.events)

        # Event type distribution
        event_counts = {}
        for event in self.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Severity distribution
        severity_counts = {}
        for event in self.events:
            severity = event.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_events": total_events,
            "event_distribution": event_counts,
            "severity_distribution": severity_counts
        }


# Global observability manager instance
_observability_manager = ObservabilityManager()


def get_observability_manager() -> ObservabilityManager:
    """Get the global observability manager instance."""
    return _observability_manager


def record_event(
    event_type: EventType,
    message: str,
    source: str = "unknown",
    severity: SeverityLevel = SeverityLevel.INFO,
    data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    task_id: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """Record an observability event using the global manager."""
    return _observability_manager.record_event(
        event_type=event_type,
        message=message,
        source=source,
        severity=severity,
        data=data,
        user_id=user_id,
        session_id=session_id,
        task_id=task_id,
        tags=tags
    )


def record_exception(
    exception: Exception,
    source: str = "unknown",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    task_id: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> str:
    """Record an exception using the global manager."""
    return _observability_manager.record_exception(
        exception=exception,
        source=source,
        user_id=user_id,
        session_id=session_id,
        task_id=task_id,
        additional_data=additional_data
    )


__all__ = [
    "EventType",
    "SeverityLevel",
    "ObservabilityEvent",
    "ObservabilityManager",
    "get_observability_manager",
    "record_event",
    "record_exception"
]





