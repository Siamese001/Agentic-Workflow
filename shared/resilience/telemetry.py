"""Centralized telemetry for resilience components.

Provides structured logging for monitoring system health, performance,
and error patterns. Compatible with Datadog, Splunk, and other observability platforms.

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class OperationStatus(Enum):
    """Status of an operation."""
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    CIRCUIT_OPEN = "circuit_open"
    TIMEOUT = "timeout"

@dataclass
class TelemetryEvent:
    """Structured telemetry event."""
    timestamp: float
    component: str
    operation: str
    status: OperationStatus
    latency_ms: float
    token_usage: Optional[int] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SystemTelemetry:
    """Centralized telemetry system for resilience components.

    Emits structured JSON logs for observability platforms.
    Tracks metrics like latency, error rates, token usage, and circuit breaker events.
    """

    def __init__(self, service_name: str = "agentic-workflow"):
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")

    def log_metric(
        """Docstring."""
        self,
        component: str,
        operation: str,
        status: OperationStatus,
        latency_ms: float,
        token_usage: Optional[int] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a telemetry event.

        Args:
            component: Component name (e.g., "openai_executor", "anthropic_executor")
            operation: Operation name (e.g., "chat_completion", "embeddings")
            status: Operation status (success, failure, retry, etc.)
            latency_ms: Latency in milliseconds
            token_usage: Number of tokens used (if applicable)
            error_type: Type of error (if any)
            error_message: Error message (if any)
            metadata: Additional metadata
        """
        event = TelemetryEvent(
            timestamp=time.time(),
            component=component,
            operation=operation,
            status=status,
            latency_ms=latency_ms,
            token_usage=token_usage,
            error_type=error_type,
            error_message=error_message,
            metadata=metadata or {},
        )

        # Convert to structured log format
        log_data = {
            "service": self.service_name,
            "timestamp": event.timestamp,
            "component": event.component,
            "operation": event.operation,
            "status": event.status.value,
            "latency_ms": event.latency_ms,
        }

        if event.token_usage is not None:
            log_data["token_usage"] = event.token_usage

        if event.error_type:
            log_data["error_type"] = event.error_type

        if event.error_message:
            log_data["error_message"] = event.error_message

        if event.metadata:
            log_data["metadata"] = event.metadata

        # Log with appropriate level
        if status in [OperationStatus.FAILURE, OperationStatus.CIRCUIT_OPEN]:
            self.logger.error(json.dumps(log_data))
        elif status == OperationStatus.RETRY:
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))

    def log_success(
        """Docstring."""
        self,
        component: str,
        operation: str,
        latency_ms: float,
        token_usage: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a successful operation."""
        self.log_metric(
            component=component,
            operation=operation,
            status=OperationStatus.SUCCESS,
            latency_ms=latency_ms,
            token_usage=token_usage,
            metadata=metadata,
        )

    def log_failure(
        """Docstring."""
        self,
        component: str,
        operation: str,
        latency_ms: float,
        error_type: str,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a failed operation."""
        self.log_metric(
            component=component,
            operation=operation,
            status=OperationStatus.FAILURE,
            latency_ms=latency_ms,
            error_type=error_type,
            error_message=error_message,
            metadata=metadata,
        )

    def log_retry(
        """Docstring."""
        self,
        component: str,
        operation: str,
        attempt: int,
        max_retries: int,
        backoff_ms: float,
        error_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a retry attempt."""
        retry_metadata = {
            "attempt": attempt,
            "max_retries": max_retries,
            "backoff_ms": backoff_ms,
        }
        if metadata:
            retry_metadata.update(metadata)

        self.log_metric(
            component=component,
            operation=operation,
            status=OperationStatus.RETRY,
            latency_ms=0.0,  # Retry events don't have operation latency
            error_type=error_type,
            metadata=retry_metadata,
        )

    def log_circuit_breaker(
        """Docstring."""
        self,
        component: str,
        breaker_name: str,
        state: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a circuit breaker event."""
        cb_metadata = {
            "breaker_name": breaker_name,
            "breaker_state": state,
        }
        if metadata:
            cb_metadata.update(metadata)

        self.log_metric(
            component=component,
            operation="circuit_breaker",
            status=OperationStatus.CIRCUIT_OPEN,
            latency_ms=0.0,
            metadata=cb_metadata,
        )

# Global telemetry instance
_default_telemetry: Optional[SystemTelemetry] = None

def get_telemetry() -> SystemTelemetry:
    """Get the default telemetry instance."""
    global _default_telemetry
    if _default_telemetry is None:
        _default_telemetry = SystemTelemetry()
    return _default_telemetry

def set_telemetry(telemetry: SystemTelemetry) -> None:
    """Set the default telemetry instance."""
    global _default_telemetry
    _default_telemetry = telemetry
