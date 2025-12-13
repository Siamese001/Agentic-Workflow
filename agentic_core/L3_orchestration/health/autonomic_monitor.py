"""Autonomic Immune System for Agent Health Monitoring.

Phase 4 - Pillar 5: Capability Maturity (Self-Evolving System)
Monitors runtime metrics and triggers alerts or retraining on degradation.

Integrates with:
- Phase 2 Observability (Pillar 10) for metrics
- Phase 4 Agent Gym (Pillar 5) for retraining
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Agent health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthMetrics:
    """Health metrics for an agent."""
    agent_id: str
    success_rate: float
    avg_response_time_ms: float
    error_rate: float
    circuit_breaker_trips: int
    total_requests: int
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "success_rate": self.success_rate,
            "avg_response_time_ms": self.avg_response_time_ms,
            "error_rate": self.error_rate,
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "total_requests": self.total_requests,
            "timestamp": self.timestamp,
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
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "agent_id": self.agent_id,
            "severity": self.severity.value,
            "message": self.message,
            "metrics": self.metrics.to_dict(),
            "recommended_actions": self.recommended_actions,
            "timestamp": self.timestamp,
        }


class AutonomicMonitor:
    """Autonomic immune system for agent health monitoring.
    
    Features:
    - Runtime metrics monitoring
    - Degradation detection
    - Automatic alerting
    - Retraining triggers
    - Self-healing recommendations
    """
    
    def __init__(
        self,
        success_rate_threshold: float = 0.8,
        error_rate_threshold: float = 0.2,
        response_time_threshold_ms: float = 5000.0,
        enable_logging: bool = True,
    ):
        """Initialize autonomic monitor.
        
        Args:
            success_rate_threshold: Minimum acceptable success rate
            error_rate_threshold: Maximum acceptable error rate
            response_time_threshold_ms: Maximum acceptable response time
            enable_logging: Enable logging
        """
        self.success_rate_threshold = success_rate_threshold
        self.error_rate_threshold = error_rate_threshold
        self.response_time_threshold_ms = response_time_threshold_ms
        self.enable_logging = enable_logging
        
        self._metrics_history: Dict[str, List[HealthMetrics]] = {}
        self._alerts: List[HealthAlert] = []
        self._alert_callbacks: List[Callable[[HealthAlert], None]] = []
        
        if self.enable_logging:
            logger.info(
                "autonomic_monitor_initialized",
                extra={
                    "success_threshold": success_rate_threshold,
                    "error_threshold": error_rate_threshold,
                    "response_time_threshold": response_time_threshold_ms,
                }
            )
    
    def record_metrics(self, metrics: HealthMetrics) -> None:
        """Record health metrics for an agent.
        
        Args:
            metrics: Health metrics
        """
        agent_id = metrics.agent_id
        
        if agent_id not in self._metrics_history:
            self._metrics_history[agent_id] = []
        
        self._metrics_history[agent_id].append(metrics)
        
        # Keep only recent history (last 100 entries)
        if len(self._metrics_history[agent_id]) > 100:
            self._metrics_history[agent_id] = self._metrics_history[agent_id][-100:]
        
        # Check health status
        status = self.check_health(agent_id)
        
        if status != HealthStatus.HEALTHY:
            self._trigger_alert(metrics, status)
    
    def check_health(self, agent_id: str) -> HealthStatus:
        """Check health status of an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            HealthStatus
        """
        history = self._metrics_history.get(agent_id, [])
        
        if not history:
            return HealthStatus.OFFLINE
        
        # Get recent metrics (last 10)
        recent = history[-10:]
        
        # Calculate averages
        avg_success_rate = sum(m.success_rate for m in recent) / len(recent)
        avg_error_rate = sum(m.error_rate for m in recent) / len(recent)
        avg_response_time = sum(m.avg_response_time_ms for m in recent) / len(recent)
        
        # Determine status
        if (avg_success_rate < 0.5 or 
            avg_error_rate > 0.5 or 
            avg_response_time > self.response_time_threshold_ms * 2):
            return HealthStatus.CRITICAL
        
        elif (avg_success_rate < self.success_rate_threshold or
              avg_error_rate > self.error_rate_threshold or
              avg_response_time > self.response_time_threshold_ms):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def get_metrics(
        self,
        agent_id: str,
        limit: int = 10,
    ) -> List[HealthMetrics]:
        """Get recent metrics for an agent.
        
        Args:
            agent_id: Agent identifier
            limit: Number of recent metrics to return
            
        Returns:
            List of HealthMetrics
        """
        history = self._metrics_history.get(agent_id, [])
        return history[-limit:] if history else []
    
    def get_alerts(
        self,
        agent_id: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
    ) -> List[HealthAlert]:
        """Get health alerts.
        
        Args:
            agent_id: Optional agent ID filter
            severity: Optional severity filter
            
        Returns:
            List of HealthAlert
        """
        alerts = self._alerts
        
        if agent_id:
            alerts = [a for a in alerts if a.agent_id == agent_id]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return alerts
    
    def register_alert_callback(
        self,
        callback: Callable[[HealthAlert], None],
    ) -> None:
        """Register callback for health alerts.
        
        Args:
            callback: Callback function
        """
        self._alert_callbacks.append(callback)
    
    def _trigger_alert(
        self,
        metrics: HealthMetrics,
        status: HealthStatus,
    ) -> None:
        """Trigger health alert.
        
        Args:
            metrics: Current metrics
            status: Health status
        """
        # Determine severity
        if status == HealthStatus.CRITICAL:
            severity = AlertSeverity.CRITICAL
        elif status == HealthStatus.DEGRADED:
            severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO
        
        # Generate message
        message = f"Agent {metrics.agent_id} health is {status.value}"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, status)
        
        # Create alert
        alert = HealthAlert(
            alert_id=f"alert_{metrics.agent_id}_{int(time.time())}",
            agent_id=metrics.agent_id,
            severity=severity,
            message=message,
            metrics=metrics,
            recommended_actions=recommendations,
        )
        
        self._alerts.append(alert)
        
        # Keep only recent alerts (last 100)
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]
        
        # Trigger callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                if self.enable_logging:
                    logger.error(
                        "alert_callback_failed",
                        extra={"error": str(e)},
                        exc_info=True,
                    )
        
        if self.enable_logging:
            logger.warning(
                "health_alert_triggered",
                extra={
                    "alert_id": alert.alert_id,
                    "agent_id": metrics.agent_id,
                    "severity": severity.value,
                    "status": status.value,
                }
            )
    
    def _generate_recommendations(
        self,
        metrics: HealthMetrics,
        status: HealthStatus,
    ) -> List[str]:
        """Generate improvement recommendations.
        
        Args:
            metrics: Current metrics
            status: Health status
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if metrics.success_rate < self.success_rate_threshold:
            recommendations.append(
                f"Success rate ({metrics.success_rate:.1%}) below threshold - "
                "Consider retraining in Agent Gym"
            )
        
        if metrics.error_rate > self.error_rate_threshold:
            recommendations.append(
                f"Error rate ({metrics.error_rate:.1%}) above threshold - "
                "Review error logs and failure patterns"
            )
        
        if metrics.avg_response_time_ms > self.response_time_threshold_ms:
            recommendations.append(
                f"Response time ({metrics.avg_response_time_ms:.0f}ms) above threshold - "
                "Optimize performance or increase resources"
            )
        
        if metrics.circuit_breaker_trips > 5:
            recommendations.append(
                f"Circuit breaker trips ({metrics.circuit_breaker_trips}) high - "
                "Check external service health and implement fallbacks"
            )
        
        if status == HealthStatus.CRITICAL:
            recommendations.append(
                "CRITICAL: Consider taking agent offline for maintenance"
            )
        
        return recommendations


def create_autonomic_monitor(
    success_rate_threshold: float = 0.8,
    error_rate_threshold: float = 0.2,
) -> AutonomicMonitor:
    """Factory function to create autonomic monitor.
    
    Args:
        success_rate_threshold: Success rate threshold
        error_rate_threshold: Error rate threshold
        
    Returns:
        AutonomicMonitor instance
    """
    return AutonomicMonitor(
        success_rate_threshold=success_rate_threshold,
        error_rate_threshold=error_rate_threshold,
    )
