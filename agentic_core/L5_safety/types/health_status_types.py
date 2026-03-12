from __future__ import annotations
'Types and models for AutonomicMonitorAgent.'
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger: Any = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Agent health status."""
    HEALTHY: Any = 'healthy'
    DEGRADED: Any = 'degraded'
    CRITICAL: Any = 'critical'
    OFFLINE: Any = 'offline'

class AlertSeverity(Enum):
    """Alert Severity levels."""
    INFO: Any = 'info'
    WARNING: Any = 'warning'
    ERROR: Any = 'error'
    CRITICAL: Any = 'critical'

@dataclass
class health_metrics:
    """Health metrics for an agent."""
    agent_id: str
    success_rate: float
    avg_response_time_ms: float
    error_rate: float
    circuit_breaker_trips: int
    total_requests: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {'agent_id': self.agent_id, 'success_rate': self.success_rate, 'avg_response_time_ms': self.avg_response_time_ms, 'error_rate': self.error_rate, 'circuit_breaker_trips': self.circuit_breaker_trips, 'total_requests': self.total_requests, 'timestamp': self.timestamp}

@dataclass
class HealthAlert:
    """Health alert for degradation detection."""
    alert_id: str
    agent_id: str
    Severity: AlertSeverity
    message: str
    metrics: health_metrics
    recommended_actions: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {'alert_id': self.alert_id, 'agent_id': self.agent_id, 'Severity': self.Severity.value, 'message': self.message, 'metrics': self.metrics.to_dict(), 'recommended_actions': self.recommended_actions, 'timestamp': self.timestamp}
