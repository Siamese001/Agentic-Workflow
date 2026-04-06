"""System Learning Telemetry Integration

Integrates system learning components with agentic_core lifecycle trace contract
for comprehensive observability and enterprise-grade telemetry.

Provides unified telemetry emission across all system learning operations
with structured event types, metrics capture, and monitoring integration.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    # P1 Execution
    _emit_captures_evaluation_metric,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    # P4 Observability
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

# Module-level telemetry initialization
_emit_applies_guardrail("p0", "system_learning_telemetry", "p0_governance")
_emit_reads_policy_state("p0", "system_learning_telemetry", "policy_binding")
_emit_snapshots_state("p0", "system_learning_telemetry", "state_snapshot")

_emit_emits_metric_event("system_learning_telemetry", "p4obs", "metric_1")
_emit_emits_metric_event("system_learning_telemetry", "p4obs", "metric_2")
_emit_emits_metric_event("system_learning_telemetry", "p4obs", "metric_3")
_emit_emits_metric_event("system_learning_telemetry", "p4obs", "metric_4")
_emit_emits_metric_event("system_learning_telemetry", "p4obs", "metric_5")
_emit_emits_metric_event("system_learning_telemetry", "p4obs", "metric_6")
_emit_records_incident_event("system_learning_telemetry", "p4obs", "incident")
_emit_captures_runtime_anomaly("system_learning_telemetry", "p4obs", "anomaly")
_emit_writes_observability_log("system_learning_telemetry", "p4obs", "obs_log")
_emit_records_telemetry_event("system_learning_telemetry", "p4obs", "mon_state")
_emit_triggers_alert("system_learning_telemetry", "p4obs", "alert")
_emit_links_incident_trace("system_learning_telemetry", "p4obs", "trace_link")
_emit_captures_pattern("system_learning_telemetry", "p3lm", "pattern")
_emit_records_learning_event("system_learning_telemetry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("system_learning_telemetry", "p3lm", "snapshot")
_emit_feeds_meta_learning("system_learning_telemetry", "p3lm", "meta_feed")
_emit_feeds_meta_learning("system_learning_telemetry", "p3lm", "routing")
_emit_improves_agent_policy("system_learning_telemetry", "p3lm", "policy")
_emit_stores_learning_state("system_learning_telemetry", "p3lm", "state")

logger = logging.getLogger(__name__)


class SystemLearningEventType(Enum):
    """System learning specific event types for structured telemetry."""

    # Core Operations
    CACHE_OPERATION = "cache_operation"
    EMBEDDING_OPERATION = "embedding_operation"
    RETRIEVAL_OPERATION = "retrieval_operation"
    DRIFT_DETECTION = "drift_detection"
    POLICY_VALIDATION = "policy_validation"

    # Learning Events
    LEARNING_SESSION_START = "learning_session_start"
    LEARNING_SESSION_END = "learning_session_end"
    MODEL_UPDATE = "model_update"
    PATTERN_DETECTED = "pattern_detected"

    # State Management
    STATE_SNAPSHOT = "state_snapshot"
    CONFIG_CHANGE = "config_change"
    VERSION_ACTIVATION = "version_activation"

    # Performance
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_OCCURRED = "error_occurred"
    RESOURCE_UTILIZATION = "resource_utilization"


class SystemLearningOperationType(Enum):
    """System learning operation types for execution tracing."""

    # Cache Operations
    CACHE_GET = "cache_get"
    CACHE_SET = "cache_set"
    CACHE_DELETE = "cache_delete"
    CACHE_INVALIDATE = "cache_invalidate"

    # Embedding Operations
    EMBEDDING_GENERATE = "embedding_generate"
    EMBEDDING_BATCH = "embedding_batch"
    EMBEDDING_CACHE = "embedding_cache"

    # Retrieval Operations
    RETRIEVAL_QUERY = "retrieval_query"
    RETRIEVAL_INDEX = "retrieval_index"
    RETRIEVAL_RANK = "retrieval_rank"

    # Learning Operations
    LEARNING_TRAIN = "learning_train"
    LEARNING_INFERENCE = "learning_inference"
    LEARNING_EVALUATE = "learning_evaluate"


@dataclass
class SystemLearningTelemetryContext:
    """Telemetry context for system learning operations."""

    # Basic context
    component_name: str
    operation_type: SystemLearningOperationType
    session_id: str | None = None
    trace_id: str | None = None

    # Performance context
    start_time: float | None = field(default_factory=time.time)
    end_time: float | None = None
    duration_ms: float | None = None

    # Resource context
    memory_usage_mb: float | None = None
    cpu_utilization: float | None = None
    cache_size: int | None = None

    # Learning context
    learning_rate: float | None = None
    model_version: str | None = None
    data_version: str | None = None

    # Error context
    error_type: str | None = None
    error_message: str | None = None
    error_stack: str | None = None


@dataclass
class SystemLearningMetric:
    """Structured metric for system learning telemetry."""

    name: str
    value: int | float | str
    unit: str | None = None
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: float | None = field(default_factory=time.time)

    # Metric classification
    is_counter: bool = False
    is_gauge: bool = False
    is_histogram: bool = False


class SystemLearningTelemetryEmitter:
    """Unified telemetry emitter for system learning components.

    Provides structured telemetry emission with:
    - Lifecycle trace contract integration
    - Performance metrics capture
    - Error and anomaly reporting
    - Learning event tracking
    - Resource utilization monitoring
    """

    def __init__(self, component_name: str) -> None:
        """Initialize telemetry emitter for a component."""
        self.component_name = component_name
        self.session_id = str(uuid.uuid4())

        # Metrics tracking
        self._metrics: dict[str, SystemLearningMetric] = {}
        self._operation_counts: dict[str, int] = {}
        self._error_counts: dict[str, int] = {}

        logger.info(f"SystemLearningTelemetryEmitter initialized for {component_name}")

    def start_operation(
        self,
        operation_type: SystemLearningOperationType,
        **context_kwargs: Any,
    ) -> SystemLearningTelemetryContext:
        """Start telemetry tracking for an operation."""
        trace_id = str(uuid.uuid4())

        context = SystemLearningTelemetryContext(
            component_name=self.component_name,
            operation_type=operation_type,
            session_id=self.session_id,
            trace_id=trace_id,
            **context_kwargs,
        )

        # Emit execution trace start
        _emit_records_execution_trace(
            trace_id, LayerSegment.L3_ORCHESTRATION, f"{self.component_name}.{operation_type.value}"
        )

        # Emit telemetry event for operation start
        self._emit_telemetry_event(
            SystemLearningEventType.CACHE_OPERATION,
            {
                "operation": operation_type.value,
                "action": "start",
                "trace_id": trace_id,
                "session_id": self.session_id,
                "component": self.component_name,
            },
        )

        # Update operation counts
        op_key = operation_type.value
        self._operation_counts[op_key] = self._operation_counts.get(op_key, 0) + 1

        return context

    def end_operation(
        self,
        context: SystemLearningTelemetryContext,
        success: bool = True,
        result: Any | None = None,
        error: Exception | None = None,
        **additional_metrics: Any,
    ) -> None:
        """End telemetry tracking for an operation."""
        context.end_time = time.time()
        context.duration_ms = (context.end_time - context.start_time) * 1000

        # Add additional metrics
        for key, value in additional_metrics.items():
            setattr(context, key, value)

        # Emit execution trace end
        if context.trace_id:
            _emit_records_execution_trace(
                context.trace_id,
                LayerSegment.L3_ORCHESTRATION,
                f"{self.component_name}.{context.operation_type.value}.end",
            )

        # Emit completion telemetry
        event_type = (
            SystemLearningEventType.ERROR_OCCURRED
            if not success or error
            else SystemLearningEventType.PERFORMANCE_METRIC
        )

        telemetry_data = {
            "operation": context.operation_type.value,
            "action": "end",
            "success": success,
            "duration_ms": context.duration_ms,
            "trace_id": context.trace_id,
            "session_id": self.session_id,
            "component": self.component_name,
        }

        # Add performance metrics
        if context.duration_ms:
            telemetry_data["duration_ms"] = context.duration_ms
        if context.memory_usage_mb:
            telemetry_data["memory_usage_mb"] = context.memory_usage_mb
        if context.cache_size is not None:
            telemetry_data["cache_size"] = context.cache_size

        # Add error information
        if error:
            context.error_type = type(error).__name__
            context.error_message = str(error)
            telemetry_data.update(
                {
                    "error_type": context.error_type,
                    "error_message": context.error_message,
                }
            )

            # Update error counts
            error_key = context.error_type
            self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1

            # Emit error-specific telemetry
            _emit_captures_runtime_anomaly(
                "p4obs", self.component_name, f"operation_error:{context.operation_type.value}"
            )
            _emit_records_incident_event("p4obs", self.component_name, f"error:{context.error_type}")

        # Add result information
        if result is not None:
            if isinstance(result, (list, dict)):
                telemetry_data["result_size"] = len(result)
            elif hasattr(result, "__len__"):
                telemetry_data["result_size"] = len(result)

        self._emit_telemetry_event(event_type, telemetry_data)

        # Emit performance metric
        if context.duration_ms:
            self.emit_metric(
                f"operation_duration_{context.operation_type.value}",
                context.duration_ms,
                unit="milliseconds",
                tags={"component": self.component_name, "operation": context.operation_type.value},
            )

        # Emit learning event for successful operations
        if success and context.operation_type in [
            SystemLearningOperationType.CACHE_SET,
            SystemLearningOperationType.EMBEDDING_GENERATE,
            SystemLearningOperationType.RETRIEVAL_QUERY,
        ]:
            _emit_records_learning_event(
                "p3lm", self.component_name, f"operation_completed:{context.operation_type.value}"
            )

    def emit_metric(
        self,
        name: str,
        value: int | float | str,
        unit: str | None = None,
        tags: dict[str, str] | None = None,
        is_counter: bool = False,
        is_gauge: bool = False,
        is_histogram: bool = False,
    ) -> None:
        """Emit a structured metric."""
        metric = SystemLearningMetric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {},
            is_counter=is_counter,
            is_gauge=is_gauge,
            is_histogram=is_histogram,
        )

        self._metrics[name] = metric

        # Emit evaluation metric
        _emit_captures_evaluation_metric("p4obs", self.component_name, metric.name)

        # Emit generic metric event
        self._emit_telemetry_event(
            SystemLearningEventType.PERFORMANCE_METRIC,
            {
                "metric_name": name,
                "metric_value": str(value),
                "metric_unit": unit,
                "metric_tags": tags,
                "component": self.component_name,
            },
        )

    def emit_learning_event(
        self,
        event_type: SystemLearningEventType,
        data: dict[str, Any],
        **additional_context: Any,
    ) -> None:
        """Emit a learning-specific event."""
        telemetry_data = {
            "event_type": event_type.value,
            "component": self.component_name,
            "session_id": self.session_id,
            **data,
            **additional_context,
        }

        # Emit learning event
        _emit_records_learning_event("p3lm", self.component_name, event_type.value)

        # Write learning snapshot for significant events
        if event_type in [
            SystemLearningEventType.LEARNING_SESSION_START,
            SystemLearningEventType.LEARNING_SESSION_END,
            SystemLearningEventType.MODEL_UPDATE,
        ]:
            _emit_writes_learning_snapshot("p3lm", self.component_name, event_type.value)

        # Feed meta-learning
        _emit_feeds_meta_learning("p3lm", self.component_name, event_type.value)

        # Store learning state
        _emit_stores_learning_state("p3lm", self.component_name, event_type.value)

        # Emit telemetry event
        self._emit_telemetry_event(event_type, telemetry_data)

    def emit_embedding_event(
        self,
        operation: str,
        text_length: int,
        embedding_dimension: int | None = None,
        model_version: str | None = None,
        **context: Any,
    ) -> None:
        """Emit embedding-specific telemetry."""
        # Store embedding
        _emit_stores_embedding("p4obs", self.component_name, f"embedding_{operation}")

        # Emit embedding telemetry
        self._emit_telemetry_event(
            SystemLearningEventType.EMBEDDING_OPERATION,
            {
                "operation": operation,
                "text_length": text_length,
                "embedding_dimension": embedding_dimension,
                "model_version": model_version,
                "component": self.component_name,
                **context,
            },
        )

        # Emit metrics
        self.emit_metric(
            f"embedding_{operation}_text_length",
            text_length,
            unit="characters",
            tags={"component": self.component_name},
        )

        if embedding_dimension:
            self.emit_metric(
                f"embedding_{operation}_dimension",
                embedding_dimension,
                unit="dimensions",
                tags={"component": self.component_name},
            )

    def emit_cache_event(
        self,
        operation: str,
        key: str,
        hit: bool | None = None,
        size_bytes: int | None = None,
        ttl_seconds: int | None = None,
        **context: Any,
    ) -> None:
        """Emit cache-specific telemetry."""
        telemetry_data = {
            "operation": operation,
            "cache_key": key[:64] + "..." if len(key) > 64 else key,  # Truncate for privacy
            "component": self.component_name,
            **context,
        }

        if hit is not None:
            telemetry_data["cache_hit"] = hit
            self.emit_metric(
                f"cache_{operation}_hit_rate",
                1 if hit else 0,
                unit="boolean",
                tags={"component": self.component_name, "operation": operation},
            )

        if size_bytes is not None:
            telemetry_data["size_bytes"] = size_bytes
            self.emit_metric(
                f"cache_{operation}_size", size_bytes, unit="bytes", tags={"component": self.component_name}
            )

        if ttl_seconds is not None:
            telemetry_data["ttl_seconds"] = ttl_seconds

        self._emit_telemetry_event(SystemLearningEventType.CACHE_OPERATION, telemetry_data)

    def emit_drift_event(
        self,
        drift_score: float,
        drift_type: str,
        indicators: dict[str, float],
        threshold: float,
        **context: Any,
    ) -> None:
        """Emit drift detection telemetry."""
        # Capture pattern for drift
        _emit_captures_pattern("p3lm", self.component_name, f"drift_detected:{drift_type}")

        # Emit drift telemetry
        self._emit_telemetry_event(
            SystemLearningEventType.DRIFT_DETECTION,
            {
                "drift_score": drift_score,
                "drift_type": drift_type,
                "indicators": indicators,
                "threshold": threshold,
                "component": self.component_name,
                **context,
            },
        )

        # Emit metrics
        self.emit_metric(
            f"drift_score_{drift_type}",
            drift_score,
            unit="score",
            tags={"component": self.component_name, "drift_type": drift_type},
        )

        # Alert if drift exceeds threshold
        if drift_score > threshold:
            _emit_triggers_alert("p4obs", self.component_name, f"drift_exceeded:{drift_type}")

    def _emit_telemetry_event(
        self,
        event_type: SystemLearningEventType,
        data: dict[str, Any],
    ) -> None:
        """Emit a structured telemetry event."""
        # Add common telemetry fields
        telemetry_data = {
            "timestamp": time.time(),
            "component": self.component_name,
            "session_id": self.session_id,
            **data,
        }

        # Emit telemetry event
        _emit_records_telemetry_event("p4", self.component_name, event_type.value)

        # Update monitoring state
        _emit_updates_monitoring_state("p4obs", self.component_name, event_type.value)

        # Write observability log
        _emit_writes_observability_log("p4obs", self.component_name, json.dumps(telemetry_data))

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        return {
            "component": self.component_name,
            "session_id": self.session_id,
            "total_metrics": len(self._metrics),
            "operation_counts": self._operation_counts,
            "error_counts": self._error_counts,
            "metrics": {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "tags": metric.tags,
                    "timestamp": metric.timestamp,
                }
                for name, metric in self._metrics.items()
            },
        }

    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self._metrics.clear()
        self._operation_counts.clear()
        self._error_counts.clear()
        _emit_records_telemetry_event("system_learning_telemetry", "p4obs", "telemetry_metrics_reset")


# Component telemetry emitters registry
_telemetry_emitters: dict[str, SystemLearningTelemetryEmitter] = {}


def get_telemetry_emitter(component_name: str) -> SystemLearningTelemetryEmitter:
    """Get or create a telemetry emitter for a component."""
    if component_name not in _telemetry_emitters:
        _telemetry_emitters[component_name] = SystemLearningTelemetryEmitter(component_name)
    return _telemetry_emitters[component_name]


def emit_system_learning_event(
    component_name: str,
    event_type: SystemLearningEventType,
    data: dict[str, Any],
) -> None:
    """Emit a system learning event from any component."""
    emitter = get_telemetry_emitter(component_name)
    emitter.emit_learning_event(event_type, data)


# Decorator for automatic telemetry
def telemetry_traced(
    operation_type: SystemLearningOperationType,
    include_result: bool = False,
    emit_on_error: bool = True,
):
    """Decorator for automatic telemetry tracing of methods."""

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Get component name from class
            component_name = getattr(self, "__class__", {}).get("__name__", "unknown")
            emitter = get_telemetry_emitter(component_name)

            # Start operation
            context = emitter.start_operation(operation_type)

            try:
                # Execute function
                result = func(self, *args, **kwargs)

                # End operation with success
                emitter.end_operation(
                    context,
                    success=True,
                    result=result if include_result else None,
                    args_count=len(args),
                    kwargs_count=len(kwargs),
                )

                return result

            except Exception as e:
                # End operation with error
                emitter.end_operation(
                    context,
                    success=False,
                    error=e,
                    args_count=len(args),
                    kwargs_count=len(kwargs),
                )

                if emit_on_error:
                    raise

                return None

        return wrapper

    return decorator


__all__ = [
    "SystemLearningEventType",
    "SystemLearningOperationType",
    "SystemLearningTelemetryContext",
    "SystemLearningMetric",
    "SystemLearningTelemetryEmitter",
    "get_telemetry_emitter",
    "emit_system_learning_event",
    "telemetry_traced",
]
