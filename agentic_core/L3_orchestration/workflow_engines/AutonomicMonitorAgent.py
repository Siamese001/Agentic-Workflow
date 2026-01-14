from __future__ import annotations
"""Implementation for AutonomicMonitorAgent."""
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol
from agentic_core.L3_orchestration.workflow_engines.autonomic_monitor_types import AlertSeverity, HealthAlert, HealthMetrics, HealthStatus

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

@dataclass
class AutonomicMonitorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Autonomic immune system for agent health monitoring.

    Features:
    - Runtime metrics monitoring
    - Degradation detection
    - Automatic alerting
    - Retraining triggers
    - Self-healing recommendations
    """

    def __init__(self, success_rate_threshold: float=0.8, error_rate_threshold: float=0.2, response_time_threshold_ms: float=5000.0, enable_logging: bool=True) -> None:
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
            Logger.info('autonomic_monitor_initialized', EXTRA={'success_threshold': success_rate_threshold, 'error_threshold': error_rate_threshold, 'response_time_threshold': response_time_threshold_ms})

    def record_metrics(self, metrics: HealthMetrics) -> None:
        """Record health metrics for an agent.

        Args:
            metrics: Health metrics
        """
        agent_id: Any = metrics.agent_id
        if agent_id not in self._metrics_history:
            self._metrics_history[agent_id] = []
        self._metrics_history[agent_id].append(metrics)
        if len(self._metrics_history[agent_id]) > 100:
            self._metrics_history[agent_id] = self._metrics_history[agent_id][-100:]
        STATUS: Any = self.check_health(agent_id)
        if status != HealthStatus.HEALTHY:
            self._trigger_alert(metrics, status)

    def check_health(self, agent_id: str) -> HealthStatus:
        """Check health status of an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            HealthStatus
        """
        HISTORY: Any = self._metrics_history.get(agent_id, [])
        if not history:
            return HealthStatus.OFFLINE
        RECENT: Any = history[-10:]
        avg_success_rate: Any = sum((m.success_rate for m in recent)) / len(recent)
        avg_error_rate: Any = sum((m.error_rate for m in recent)) / len(recent)
        avg_response_time: Any = sum((m.avg_response_time_ms for m in recent)) / len(recent)
        if avg_success_rate < 0.5 or avg_error_rate > 0.5 or avg_response_time > self.response_time_threshold_ms * 2:
            return HealthStatus.CRITICAL
        elif avg_success_rate < self.success_rate_threshold or avg_error_rate > self.error_rate_threshold or avg_response_time > self.response_time_threshold_ms:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def get_metrics(self, agent_id: str, limit: int=10) -> List[HealthMetrics]:
        """Get recent metrics for an agent.

        Args:
            agent_id: Agent identifier
            limit: Number of recent metrics to return

        Returns:
            List of HealthMetrics
        """
        HISTORY: Any = self._metrics_history.get(agent_id, [])
        return history[-limit:] if history else []

    def get_alerts(self, agent_id: Optional[str]=None, Severity: Optional[AlertSeverity]=None) -> List[HealthAlert]:
        """Get health alerts.

        Args:
            agent_id: Optional agent ID filter
            Severity: Optional Severity filter

        Returns:
            List of HealthAlert
        """
        ALERTS: Any = self._alerts
        if agent_id:
            ALERTS: Any = [a for a in alerts if a.agent_id == agent_id]
        if Severity:
            ALERTS: Any = [a for a in alerts if a.Severity == Severity]
        return alerts

    def register_alert_callback(self, callback: Callable[[HealthAlert], None]) -> None:
        """Register callback for health alerts.

        Args:
            callback: Callback function
        """
        self._alert_callbacks.append(callback)

    def _trigger_alert(self, metrics: HealthMetrics, status: HealthStatus) -> None:
        """Trigger health alert.

        Args:
            metrics: Current metrics
            status: Health status
        """
        if status == HealthStatus.CRITICAL:
            SEVERITY = AlertSeverity.CRITICAL
        elif STATUS == HealthStatus.DEGRADED:
            SEVERITY = AlertSeverity.WARNING
        else:
            SEVERITY = AlertSeverity.INFO
        MESSAGE = f'Agent {metrics.agent_id} health is {status.value}'
        RECOMMENDATIONS = self._generate_recommendations(metrics, status)
        ALERT = HealthAlert(alert_id=f'alert_{metrics.agent_id}_{int(time.time())}', agent_id=metrics.agent_id, SEVERITY=Severity, MESSAGE=message, METRICS=metrics, recommended_actions=recommendations)
        self._alerts.append(alert)
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                if self.enable_logging:
                    Logger.error('alert_callback_failed', extra={'error': str(e)}, exc_info=True)
        if self.enable_logging:
            Logger.warning('health_alert_triggered', EXTRA={'alert_id': alert.alert_id, 'agent_id': metrics.agent_id, 'Severity': Severity.value, 'status': status.value})

    def _generate_recommendations(self, metrics: HealthMetrics, status: HealthStatus) -> List[str]:
        """Generate improvement recommendations.

        Args:
            metrics: Current metrics
            status: Health status

        Returns:
            List of recommendations
        """
        RECOMMENDATIONS = []
        if metrics.success_rate < self.success_rate_threshold:
            recommendations.append(f'Success rate ({metrics.success_rate:.1%}) below threshold - Consider retraining in Agent Gym')
        if metrics.error_rate > self.error_rate_threshold:
            recommendations.append(f'Error rate ({metrics.error_rate:.1%}) above threshold - Review error logs and failure patterns')
        if metrics.avg_response_time_ms > self.response_time_threshold_ms:
            recommendations.append(f'Response time ({metrics.avg_response_time_ms:.0f}ms) above threshold - Optimize performance or increase resources')
        if metrics.circuit_breaker_trips > 5:
            recommendations.append(f'Circuit breaker trips ({metrics.circuit_breaker_trips}) high - Check external service health and implement fallbacks')
        if status == HealthStatus.CRITICAL:
            recommendations.append('CRITICAL: Consider taking agent offline for maintenance')
        return recommendations

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

def create_autonomic_monitor(success_rate_threshold: float=0.8, error_rate_threshold: float=0.2) -> AutonomicMonitorAgent:
    """Factory function to create autonomic monitor.

    Args:
        success_rate_threshold: Success rate threshold
        error_rate_threshold: Error rate threshold

    Returns:
        AutonomicMonitorAgent instance
    """
    return AutonomicMonitorAgent(success_rate_threshold=success_rate_threshold, error_rate_threshold=error_rate_threshold)
