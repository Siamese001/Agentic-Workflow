"""Health Monitoring - Real-time architectural health assessment.

This module provides real-time health monitoring capabilities that enable
continuous assessment of architectural health and early warning systems.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..phase2.contextual_engine import ContextualIntelligenceEngine, AnalysisResult

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Types of health metrics."""

    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    COMPLEXITY = "complexity"
    DEPENDENCY = "dependency"


@dataclass
class HealthMetric:
    """Represents a health metric."""

    metric_id: str
    metric_type: MetricType
    name: str
    value: float  # 0.0 to 1.0
    threshold_warning: float
    threshold_critical: float
    status: HealthStatus
    timestamp: datetime
    description: str
    trend: str  # improving, stable, degrading
    historical_values: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class HealthAlert:
    """Represents a health alert."""

    alert_id: str
    severity: str  # low, medium, high, critical
    title: str
    description: str
    metric_id: str
    current_value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    recommendations: List[str] = field(default_factory=list)


@dataclass
class HealthReport:
    """Comprehensive health report."""

    overall_status: HealthStatus
    overall_score: float  # 0.0 to 1.0
    metrics: Dict[str, HealthMetric]
    alerts: List[HealthAlert]
    trends: Dict[str, str]
    recommendations: List[str]
    generated_at: datetime
    execution_time_seconds: float = 0.0


class ArchitecturalHealthMonitor:
    """Real-time architectural health monitoring system."""

    def __init__(self, contextual_engine: ContextualIntelligenceEngine):
        """Initialize health monitoring system.

        Args:
            contextual_engine: Contextual intelligence engine for analysis
        """
        self.contextual_engine = contextual_engine

        # Health metrics storage
        self.health_metrics: Dict[str, HealthMetric] = {}
        self.active_alerts: List[HealthAlert] = []
        self.alert_history: deque[HealthAlert] = deque(maxlen=1000)

        # Health thresholds
        self.health_thresholds = {
            MetricType.PERFORMANCE: {"warning": 0.7, "critical": 0.5},
            MetricType.RELIABILITY: {"warning": 0.8, "critical": 0.6},
            MetricType.SECURITY: {"warning": 0.9, "critical": 0.7},
            MetricType.COMPLIANCE: {"warning": 0.8, "critical": 0.6},
            MetricType.COMPLEXITY: {"warning": 0.6, "critical": 0.4},
            MetricType.DEPENDENCY: {"warning": 0.7, "critical": 0.5},
        }

        # Monitoring configuration
        self.monitoring_config = {
            "alert_cooldown_minutes": 30,
            "trend_analysis_window": 10,
            "health_check_interval_seconds": 60,
            "max_alerts_per_metric": 5,
        }

        # Initialize health metrics
        self._initialize_health_metrics()

        logger.info("ArchitecturalHealthMonitor initialized")

    def monitor_health(self, context: Optional[ArchitecturalContext] = None) -> HealthReport:
        """Perform comprehensive health monitoring.

        Args:
            context: Optional architectural context for targeted monitoring

        Returns:
            HealthReport with comprehensive health assessment
        """
        start_time = time.time()

        logger.info("Starting comprehensive health monitoring")

        # Collect health metrics
        self._collect_health_metrics(context)

        # Analyze trends
        trends = self._analyze_health_trends()

        # Generate alerts
        self._generate_health_alerts()

        # Calculate overall health
        overall_status, overall_score = self._calculate_overall_health()

        # Generate recommendations
        recommendations = self._generate_health_recommendations()

        report = HealthReport(
            overall_status=overall_status,
            overall_score=overall_score,
            metrics=self.health_metrics,
            alerts=self.active_alerts,
            trends=trends,
            recommendations=recommendations,
            generated_at=datetime.now(),
            execution_time_seconds=time.time() - start_time,
        )

        logger.info(f"Health monitoring completed in {report.execution_time_seconds:.3f}s")

        return report

    def get_health_dashboard(self) -> Dict[str, Any]:
        """Get real-time health dashboard data.

        Returns:
            Health dashboard data for visualization
        """
        dashboard = {
            "overall_status": self._get_overall_status(),
            "overall_score": self._get_overall_score(),
            "metric_summary": self._get_metric_summary(),
            "active_alerts": len(self.active_alerts),
            "alert_summary": self._get_alert_summary(),
            "trend_summary": self._get_trend_summary(),
            "last_updated": datetime.now().isoformat(),
        }

        return dashboard

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a health alert.

        Args:
            alert_id: ID of the alert to acknowledge

        Returns:
            True if alert was acknowledged, False if not found
        """
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged")
                return True

        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a health alert.

        Args:
            alert_id: ID of the alert to resolve

        Returns:
            True if alert was resolved, False if not found
        """
        for i, alert in enumerate(self.active_alerts):
            if alert.alert_id == alert_id:
                alert.resolved = True
                self.alert_history.append(alert)
                self.active_alerts.pop(i)
                logger.info(f"Alert {alert_id} resolved")
                return True

        return False

    def get_health_trends(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get health trends over time.

        Args:
            time_window_hours: Time window in hours for trend analysis

        Returns:
            Health trends data
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        trends = {}
        for metric_id, metric in self.health_metrics.items():
            # Filter historical values by time window
            recent_values = [
                (value, timestamp) for value, timestamp in metric.historical_values if timestamp > cutoff_time
            ]

            if len(recent_values) >= 2:
                values = [v for v, _ in recent_values]
                trend_direction = self._calculate_trend_direction(values)

                trends[metric_id] = {
                    "trend": trend_direction,
                    "current_value": metric.value,
                    "change_percent": self._calculate_change_percent(values),
                    "data_points": len(recent_values),
                }

        return trends

    def _initialize_health_metrics(self) -> None:
        """Initialize health metrics."""
        metrics_config = [
            {
                "metric_id": "performance_score",
                "metric_type": MetricType.PERFORMANCE,
                "name": "Performance Score",
                "description": "Overall system performance metric",
            },
            {
                "metric_id": "reliability_score",
                "metric_type": MetricType.RELIABILITY,
                "name": "Reliability Score",
                "description": "System reliability and availability",
            },
            {
                "metric_id": "security_score",
                "metric_type": MetricType.SECURITY,
                "name": "Security Score",
                "description": "Security posture and vulnerability assessment",
            },
            {
                "metric_id": "compliance_score",
                "metric_type": MetricType.COMPLIANCE,
                "name": "Compliance Score",
                "description": "Architectural governance compliance",
            },
            {
                "metric_id": "complexity_score",
                "metric_type": MetricType.COMPLEXITY,
                "name": "Complexity Score",
                "description": "Architectural complexity assessment",
            },
            {
                "metric_id": "dependency_score",
                "metric_type": MetricType.DEPENDENCY,
                "name": "Dependency Score",
                "description": "Dependency health and coupling assessment",
            },
        ]

        for config in metrics_config:
            thresholds = self.health_thresholds[config["metric_type"]]
            metric = HealthMetric(
                metric_id=config["metric_id"],
                metric_type=config["metric_type"],
                name=config["name"],
                value=0.8,  # Initial value
                threshold_warning=thresholds["warning"],
                threshold_critical=thresholds["critical"],
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                description=config["description"],
                trend="stable",
            )
            self.health_metrics[metric.metric_id] = metric

    def _collect_health_metrics(self, context: Optional[ArchitecturalContext]) -> None:
        """Collect current health metrics."""
        # Performance metric
        performance_value = self._calculate_performance_metric(context)
        self._update_metric("performance_score", performance_value)

        # Reliability metric
        reliability_value = self._calculate_reliability_metric(context)
        self._update_metric("reliability_score", reliability_value)

        # Security metric
        security_value = self._calculate_security_metric(context)
        self._update_metric("security_score", security_value)

        # Compliance metric
        compliance_value = self._calculate_compliance_metric(context)
        self._update_metric("compliance_score", compliance_value)

        # Complexity metric
        complexity_value = self._calculate_complexity_metric(context)
        self._update_metric("complexity_score", complexity_value)

        # Dependency metric
        dependency_value = self._calculate_dependency_metric(context)
        self._update_metric("dependency_score", dependency_value)

    def _calculate_performance_metric(self, context: Optional[ArchitecturalContext]) -> float:
        """Calculate performance health metric."""
        # This would integrate with actual performance monitoring
        # For now, provide mock calculation

        base_score = 0.8

        # Factor in recent analysis performance
        if context:
            # Mock performance calculation based on context
            if len(context.target_modules) > 5:
                base_score -= 0.1  # Large scope affects performance
            if context.action_type in ["refactor", "analyze_code"]:
                base_score -= 0.05  # Complex actions affect performance

        return max(0.0, min(1.0, base_score))

    def _calculate_reliability_metric(self, context: Optional[ArchitecturalContext]) -> float:
        """Calculate reliability health metric."""
        # This would integrate with actual reliability monitoring
        # For now, provide mock calculation

        base_score = 0.9

        # Factor in error rates and availability
        # Mock calculation based on recent data
        error_rate = 0.02  # 2% error rate
        availability = 0.995  # 99.5% availability

        reliability_score = (availability * 0.7) + ((1 - error_rate) * 0.3)

        return max(0.0, min(1.0, reliability_score))

    def _calculate_security_metric(self, context: Optional[ArchitecturalContext]) -> float:
        """Calculate security health metric."""
        # This would integrate with actual security monitoring
        # For now, provide mock calculation

        base_score = 0.85

        # Factor in security vulnerabilities
        vulnerability_count = 2  # Mock vulnerability count
        if vulnerability_count > 5:
            base_score -= 0.2
        elif vulnerability_count > 2:
            base_score -= 0.1

        return max(0.0, min(1.0, base_score))

    def _calculate_compliance_metric(self, context: Optional[ArchitecturalContext]) -> float:
        """Calculate compliance health metric."""
        # This would integrate with actual compliance monitoring
        # For now, provide mock calculation

        base_score = 0.8

        # Factor in governance violations
        violation_count = 1  # Mock violation count
        if violation_count > 3:
            base_score -= 0.3
        elif violation_count > 0:
            base_score -= 0.1

        return max(0.0, min(1.0, base_score))

    def _calculate_complexity_metric(self, context: Optional[ArchitecturalContext]) -> float:
        """Calculate complexity health metric."""
        # This would integrate with actual complexity analysis
        # For now, provide mock calculation

        base_score = 0.7

        # Factor in architectural complexity
        if context:
            complexity_factors = len(context.target_modules)
            if complexity_factors > 10:
                base_score -= 0.2
            elif complexity_factors > 5:
                base_score -= 0.1

        return max(0.0, min(1.0, base_score))

    def _calculate_dependency_metric(self, context: Optional[ArchitecturalContext]) -> float:
        """Calculate dependency health metric."""
        # This would integrate with actual dependency analysis
        # For now, provide mock calculation

        base_score = 0.75

        # Factor in dependency health
        circular_deps = 0  # Mock circular dependencies
        tight_coupling = 2  # Mock tight couplings

        if circular_deps > 0:
            base_score -= 0.3
        if tight_coupling > 5:
            base_score -= 0.2
        elif tight_coupling > 2:
            base_score -= 0.1

        return max(0.0, min(1.0, base_score))

    def _update_metric(self, metric_id: str, new_value: float) -> None:
        """Update a health metric with new value."""
        if metric_id not in self.health_metrics:
            return

        metric = self.health_metrics[metric_id]

        # Store historical value
        metric.historical_values.append((new_value, datetime.now()))

        # Update current value
        metric.value = new_value
        metric.timestamp = datetime.now()

        # Update status based on thresholds
        if new_value <= metric.threshold_critical:
            metric.status = HealthStatus.CRITICAL
        elif new_value <= metric.threshold_warning:
            metric.status = HealthStatus.WARNING
        elif new_value <= 0.6:
            metric.status = HealthStatus.DEGRADED
        else:
            metric.status = HealthStatus.HEALTHY

        # Update trend
        if len(metric.historical_values) >= 2:
            recent_values = [v for v, _ in list(metric.historical_values)[-5:]]
            metric.trend = self._calculate_trend_direction(recent_values)

    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "stable"

        # Simple trend calculation
        recent_avg = statistics.mean(values[-3:])
        older_avg = statistics.mean(values[-6:-3]) if len(values) >= 6 else values[0]

        change = recent_avg - older_avg

        if change > 0.05:
            return "improving"
        elif change < -0.05:
            return "degrading"
        else:
            return "stable"

    def _analyze_health_trends(self) -> Dict[str, str]:
        """Analyze health trends across all metrics."""
        trends = {}

        for metric_id, metric in self.health_metrics.items():
            trends[metric_id] = metric.trend

        return trends

    def _generate_health_alerts(self) -> None:
        """Generate health alerts based on metrics."""
        current_time = datetime.now()
        cooldown_period = timedelta(minutes=self.monitoring_config["alert_cooldown_minutes"])

        for metric_id, metric in self.health_metrics.items():
            # Check if alert should be generated
            if metric.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                # Check cooldown period
                recent_alerts = [
                    alert
                    for alert in self.active_alerts
                    if alert.metric_id == metric_id and (current_time - alert.timestamp) < cooldown_period
                ]

                if not recent_alerts:
                    # Generate new alert
                    alert = HealthAlert(
                        alert_id=f"alert_{metric_id}_{int(current_time.timestamp())}",
                        severity="critical" if metric.status == HealthStatus.CRITICAL else "medium",
                        title=f"Health Alert: {metric.name}",
                        description=f"Metric {metric.name} is {metric.status.value} (value: {metric.value:.2f})",
                        metric_id=metric_id,
                        current_value=metric.value,
                        threshold=metric.threshold_warning
                        if metric.status == HealthStatus.WARNING
                        else metric.threshold_critical,
                        timestamp=current_time,
                        recommendations=self._generate_alert_recommendations(metric),
                    )

                    self.active_alerts.append(alert)
                    logger.warning(f"Generated health alert: {alert.title}")

    def _generate_alert_recommendations(self, metric: HealthMetric) -> List[str]:
        """Generate recommendations for health alerts."""
        recommendations = []

        if metric.metric_type == MetricType.PERFORMANCE:
            recommendations.extend(
                [
                    "Optimize slow-performing components",
                    "Consider caching strategies",
                    "Review resource utilization",
                ]
            )
        elif metric.metric_type == MetricType.RELIABILITY:
            recommendations.extend(
                ["Improve error handling", "Implement circuit breakers", "Enhance monitoring coverage"]
            )
        elif metric.metric_type == MetricType.SECURITY:
            recommendations.extend(
                ["Address security vulnerabilities", "Review access controls", "Update security patches"]
            )
        elif metric.metric_type == MetricType.COMPLIANCE:
            recommendations.extend(
                ["Address governance violations", "Update documentation", "Review architectural standards"]
            )
        elif metric.metric_type == MetricType.COMPLEXITY:
            recommendations.extend(["Simplify complex components", "Reduce coupling", "Improve modularity"])
        elif metric.metric_type == MetricType.DEPENDENCY:
            recommendations.extend(
                ["Resolve circular dependencies", "Reduce tight coupling", "Implement dependency injection"]
            )

        return recommendations

    def _calculate_overall_health(self) -> Tuple[HealthStatus, float]:
        """Calculate overall health status and score."""
        if not self.health_metrics:
            return HealthStatus.UNKNOWN, 0.0

        # Calculate overall score
        scores = [metric.value for metric in self.health_metrics.values()]
        overall_score = statistics.mean(scores)

        # Determine overall status
        critical_count = sum(
            1 for metric in self.health_metrics.values() if metric.status == HealthStatus.CRITICAL
        )
        warning_count = sum(
            1 for metric in self.health_metrics.values() if metric.status == HealthStatus.WARNING
        )

        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_count > 2:
            overall_status = HealthStatus.WARNING
        elif warning_count > 0:
            overall_status = HealthStatus.DEGRADED
        elif overall_score > 0.8:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        return overall_status, overall_score

    def _generate_health_recommendations(self) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []

        # Analyze critical metrics
        critical_metrics = [
            metric for metric in self.health_metrics.values() if metric.status == HealthStatus.CRITICAL
        ]

        for metric in critical_metrics:
            recommendations.extend(self._generate_alert_recommendations(metric))

        # Analyze trends
        degrading_metrics = [
            metric_id for metric_id, trend in self._analyze_health_trends().items() if trend == "degrading"
        ]

        if degrading_metrics:
            recommendations.append("Investigate degrading trends in: " + ", ".join(degrading_metrics))

        # General recommendations
        if len(self.active_alerts) > 5:
            recommendations.append("High number of active alerts: consider comprehensive health review")

        return recommendations

    def _get_overall_status(self) -> HealthStatus:
        """Get current overall health status."""
        status, _ = self._calculate_overall_health()
        return status

    def _get_overall_score(self) -> float:
        """Get current overall health score."""
        _, score = self._calculate_overall_health()
        return score

    def _get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of health metrics."""
        summary = {
            "total_metrics": len(self.health_metrics),
            "healthy": 0,
            "warning": 0,
            "degraded": 0,
            "critical": 0,
        }

        for metric in self.health_metrics.values():
            summary[metric.status.value] += 1

        return summary

    def _get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of active alerts."""
        summary = {
            "total_alerts": len(self.active_alerts),
            "acknowledged": 0,
            "unacknowledged": 0,
            "by_severity": defaultdict(int),
        }

        for alert in self.active_alerts:
            if alert.acknowledged:
                summary["acknowledged"] += 1
            else:
                summary["unacknowledged"] += 1
            summary["by_severity"][alert.severity] += 1

        return dict(summary)

    def _get_trend_summary(self) -> Dict[str, Any]:
        """Get summary of health trends."""
        trends = self._analyze_health_trends()

        summary = {"improving": 0, "stable": 0, "degrading": 0}

        for trend in trends.values():
            summary[trend] += 1

        return summary

    def _calculate_change_percent(self, values: List[float]) -> float:
        """Calculate percentage change in values."""
        if len(values) < 2:
            return 0.0

        old_value = values[0]
        new_value = values[-1]

        if old_value == 0:
            return 0.0

        return ((new_value - old_value) / old_value) * 100

    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get health monitoring statistics."""
        return {
            "total_metrics": len(self.health_metrics),
            "active_alerts": len(self.active_alerts),
            "alert_history_size": len(self.alert_history),
            "metric_types": {
                metric_type.value: len(
                    [m for m in self.health_metrics.values() if m.metric_type == metric_type]
                )
                for metric_type in MetricType
            },
            "average_metric_score": sum(m.value for m in self.health_metrics.values())
            / len(self.health_metrics)
            if self.health_metrics
            else 0.0,
        }
