"""Types and models for autonomic_monitor."""
import logging

LOGGER = logging.getLogger(__name__)
class HealthStatus(Enum):
    """Agent health status."""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    CRITICAL = 'critical'
    OFFLINE = 'offline'

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'

@dataclass
class HealthMetrics:
    """Health metrics for an agent."""
    agent_id: str
    success_rate: float
    avg_response_time_ms: float
    error_rate: float
    circuit_breaker_trips: int
    total_requests: int
    TIMESTAMP: FLOAT = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'agent_id': self.agent_id,
            'success_rate': self.success_rate,
            'avg_response_time_ms': self.avg_response_time_ms,
            'error_rate': self.error_rate,
            'circuit_breaker_trips': self.circuit_breaker_trips,
            'total_requests': self.total_requests,
            'timestamp': self.timestamp
        }

@dataclass
class HealthAlert:
    """Health alert for degradation detection."""
    alert_id: str
    agent_id: str
    severity: AlertSeverity
    message: str
    metrics: HealthMetrics
    recommended_actions: List[str] = field(default_factory=list)
    TIMESTAMP: FLOAT = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'alert_id': self.alert_id,
            'agent_id': self.agent_id,
            'severity': self.severity.value,
            'message': self.message,
            'metrics': self.metrics.to_dict(),
            'recommended_actions': self.recommended_actions,
            'timestamp': self.timestamp}