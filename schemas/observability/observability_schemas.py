#!/usr/bin/env python3
"""
Observability Schemas
Section 10: Schema Layer - Schemas for observability operations
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..core.base_schemas import BaseRequest, BaseResponse

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

class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class ObservabilityEvent(BaseModel):
    """Structured observability event."""
    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(..., description="Event timestamp")
    severity: SeverityLevel = Field(..., description="Event severity")
    source: str = Field(..., description="Event source")
    message: str = Field(..., description="Event message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    task_id: Optional[str] = Field(None, description="Task identifier")
    tags: List[str] = Field(default_factory=list, description="Event tags")

class ObservabilityRequest(BaseRequest):
    """Request schema for observability operations."""
    event_type: EventType = Field(..., description="Type of event to record")
    message: str = Field(..., description="Event message")
    source: str = Field(..., description="Event source")
    severity: SeverityLevel = Field(SeverityLevel.INFO, description="Event severity")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event data")
    tags: Optional[List[str]] = Field(default_factory=list, description="Event tags")

class ObservabilityResponse(BaseResponse):
    """Response schema for observability operations."""
    event_id: str = Field(..., description="Recorded event identifier")
    event_type: EventType = Field(..., description="Type of event recorded")
    timestamp: datetime = Field(..., description="Event timestamp")
    severity: SeverityLevel = Field(..., description="Event severity")

class MetricData(BaseModel):
    """Metric data schema."""
    metric_name: str = Field(..., description="Metric name")
    metric_type: MetricType = Field(..., description="Metric type")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    timestamp: datetime = Field(..., description="Metric timestamp")
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags")
    dimensions: Dict[str, str] = Field(default_factory=dict, description="Metric dimensions")

class MetricRequest(BaseRequest):
    """Request schema for metric operations."""
    metric_name: str = Field(..., description="Metric name")
    metric_type: MetricType = Field(..., description="Metric type")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Metric tags")
    dimensions: Optional[Dict[str, str]] = Field(default_factory=dict, description="Metric dimensions")

class MetricResponse(BaseResponse):
    """Response schema for metric operations."""
    metric_id: str = Field(..., description="Recorded metric identifier")
    metric_name: str = Field(..., description="Metric name")
    metric_type: MetricType = Field(..., description="Metric type")
    value: float = Field(..., description="Recorded metric value")
    timestamp: datetime = Field(..., description="Metric timestamp")

class TraceData(BaseModel):
    """Trace data schema."""
    trace_id: str = Field(..., description="Trace identifier")
    span_id: str = Field(..., description="Span identifier")
    parent_span_id: Optional[str] = Field(None, description="Parent span identifier")
    operation_name: str = Field(..., description="Operation name")
    start_time: datetime = Field(..., description="Span start time")
    end_time: Optional[datetime] = Field(None, description="Span end time")
    duration_ms: Optional[float] = Field(None, description="Duration in milliseconds")
    status: str = Field(..., description="Span status")
    tags: Dict[str, str] = Field(default_factory=dict, description="Span tags")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Span logs")

class TraceRequest(BaseRequest):
    """Request schema for trace operations."""
    trace_id: str = Field(..., description="Trace identifier")
    span_id: str = Field(..., description="Span identifier")
    operation_name: str = Field(..., description="Operation name")
    parent_span_id: Optional[str] = Field(None, description="Parent span identifier")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Span tags")

class TraceResponse(BaseResponse):
    """Response schema for trace operations."""
    trace_id: str = Field(..., description="Trace identifier")
    span_id: str = Field(..., description="Span identifier")
    operation_name: str = Field(..., description="Operation name")
    start_time: datetime = Field(..., description="Span start time")
    end_time: Optional[datetime] = Field(None, description="Span end time")
    duration_ms: Optional[float] = Field(None, description="Duration in milliseconds")
    status: str = Field(..., description="Span status")

class AlertData(BaseModel):
    """Alert data schema."""
    alert_id: str = Field(..., description="Alert identifier")
    alert_name: str = Field(..., description="Alert name")
    severity: SeverityLevel = Field(..., description="Alert severity")
    condition: str = Field(..., description="Alert condition")
    threshold: float = Field(..., description="Alert threshold")
    current_value: float = Field(..., description="Current metric value")
    triggered_at: datetime = Field(..., description="Alert trigger timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Alert resolution timestamp")
    status: str = Field(..., description="Alert status")
    description: str = Field(..., description="Alert description")
    tags: Dict[str, str] = Field(default_factory=dict, description="Alert tags")

class AlertRequest(BaseRequest):
    """Request schema for alert operations."""
    alert_name: str = Field(..., description="Alert name")
    severity: SeverityLevel = Field(..., description="Alert severity")
    condition: str = Field(..., description="Alert condition")
    threshold: float = Field(..., description="Alert threshold")
    description: str = Field(..., description="Alert description")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Alert tags")

class AlertResponse(BaseResponse):
    """Response schema for alert operations."""
    alert_id: str = Field(..., description="Alert identifier")
    alert_name: str = Field(..., description="Alert name")
    severity: SeverityLevel = Field(..., description="Alert severity")
    status: str = Field(..., description="Alert status")
    triggered_at: datetime = Field(..., description="Alert trigger timestamp")

class LogData(BaseModel):
    """Log data schema."""
    log_id: str = Field(..., description="Log identifier")
    timestamp: datetime = Field(..., description="Log timestamp")
    level: SeverityLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    source: str = Field(..., description="Log source")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    task_id: Optional[str] = Field(None, description="Task identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Log metadata")

class LogRequest(BaseRequest):
    """Request schema for log operations."""
    level: SeverityLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    source: str = Field(..., description="Log source")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Log metadata")

class LogResponse(BaseResponse):
    """Response schema for log operations."""
    log_id: str = Field(..., description="Log identifier")
    timestamp: datetime = Field(..., description="Log timestamp")
    level: SeverityLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
