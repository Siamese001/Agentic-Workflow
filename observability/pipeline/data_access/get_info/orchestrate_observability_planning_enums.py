"""Enum types for orchestrate_observability_planning."""

from enum import Enum

class MetricType(Enum):
    """Types of metrics for observability."""
    COUNTER = 'counter'
    GAUGE = 'gauge'
    HISTOGRAM = 'histogram'
    TIMER = 'timer'

class LogLevel(Enum):
    """Log levels for observability."""
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'

class AlertSeverity(Enum):
    """Severity levels for alerts."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
