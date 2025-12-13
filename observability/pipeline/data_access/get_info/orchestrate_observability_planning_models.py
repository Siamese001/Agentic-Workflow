"""Dataclass models for orchestrate_observability_planning."""

from dataclasses import dataclass, field
# from .orchestrate_observability_planning_enums import *  # Star import removed

@dataclass
class MetricDefinition:
    """Definition of a metric to be collected."""
    name: str
    metric_type: MetricType
    description: str
    labels: Dict[str, str] = field(default_factory=dict)
    sampling_rate: float = 1.0
    aggregation: Optional[str] = None

@dataclass
class LogConfiguration:
    """Configuration for log collection."""
    service_name: str
    log_level: LogLevel
    format: str = 'json'
    include_timestamp: bool = True
    include_trace_id: bool = True
    filters: List[str] = field(default_factory=list)

@dataclass
class TraceConfiguration:
    """Configuration for distributed tracing."""
    service_name: str
    sampling_rate: float = 0.1
    include_payload: bool = False
    max_spans_per_trace: int = 1000
    export_batch_size: int = 100

@dataclass
class AlertRule:
    """Definition of an alert rule."""
    name: str
    condition: str
    severity: AlertSeverity
    threshold: float
    duration: int
    notification_channels: List[str] = field(default_factory=list)

@dataclass
class ObservabilityPlanningConfig:
    """Configuration for observability planning orchestrator."""
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_tracing: bool = True
    enable_alerts: bool = True
    default_sampling_rate: float = 0.1
    log_retention_days: int = 30
    metric_retention_days: int = 90
    log_level: str = 'INFO'
