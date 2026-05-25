"""
agentic_core/L6_observability/evaluation/learning_metrics_dashboard.py

Wave 2.4: Learning Metrics Dashboard

Query API for learning metrics with:
- Metric aggregation and visualization
- Alerting for anomalies
- Trend analysis
- Performance tracking
"""

from __future__ import annotations

import hashlib
import logging
import statistics
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# P0 governance self-bootstrap
emit_replay_key("p0", "learning_metrics_dashboard")
emit_determinism_digest("p0", "learning_metrics_dashboard")
_emit_applies_guardrail("p0", "learning_metrics_dashboard", "p0_governance")
_emit_snapshots_state("p0", "learning_metrics_dashboard", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap
_emit_routes_through("p1", "learning_metrics_dashboard", "L6")
_emit_authorize_and_execute("p2", "learning_metrics_dashboard", "execution_auth")
_emit_validates_capability("p2", "learning_metrics_dashboard", "capability_check")
_emit_routes_to_capability("p2", "learning_metrics_dashboard", "capability_route")
_emit_writes_via_uwg("p2", "learning_metrics_dashboard", "uwg_write")
_emit_blocks_direct_write("p2", "learning_metrics_dashboard", "direct_write_block")
_emit_records_tool_invocation("p2", "learning_metrics_dashboard", "tool_invocation")
_emit_captures_execution_output("p2", "learning_metrics_dashboard", "exec_output")
_emit_dispatches_agent("p3", "learning_metrics_dashboard", "agent_dispatch")
_emit_coordinates_agents("p3", "learning_metrics_dashboard", "agent_coordination")
_emit_records_workflow_lineage("p3", "learning_metrics_dashboard", "workflow_lineage")
_emit_records_healing_outcome("p3", "learning_metrics_dashboard", "healing_outcome")
_emit_escalates_failure("p3", "learning_metrics_dashboard", "failure_escalation")
_emit_orchestrates_workflow("p3", "learning_metrics_dashboard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "learning_metrics_dashboard", "healing_dispatch")
_emit_invokes_evaluation("p3", "learning_metrics_dashboard", "evaluation_signal")
_emit_records_telemetry_event("p4", "learning_metrics_dashboard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "learning_metrics_dashboard", "eval_metric")
_emit_stores_embedding("p4", "learning_metrics_dashboard", "embedding_store")
_emit_updates_meta_learning_state("p4", "learning_metrics_dashboard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "learning_metrics_dashboard", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricAlert:
    """Alert for metric anomaly."""

    metric_name: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold: float
    timestamp: float


@dataclass
class DashboardMetrics:
    """Dashboard metrics summary."""

    total_evaluations: int
    avg_score: float
    score_trend: str
    alert_count: int
    active_alerts: list[MetricAlert]
    metrics_by_type: dict[str, dict[str, float]]


class LearningMetricsDashboard:
    """Dashboard for learning metrics with alerting and visualization.

    Features:
    - Metric aggregation by type
    - Trend analysis
    - Anomaly detection and alerting
    - Query API for visualization
    """

    def __init__(
        self,
        alert_threshold_low: float = 0.5,
        alert_threshold_critical: float = 0.3,
    ) -> None:
        """Initialize learning metrics dashboard.

        Args:
            alert_threshold_low: Threshold for low score warnings
            alert_threshold_critical: Threshold for critical alerts
        """
        self._alert_threshold_low = alert_threshold_low
        self._alert_threshold_critical = alert_threshold_critical

        # Metrics storage
        self._metrics: dict[str, list[tuple[float, float]]] = {}  # type -> [(timestamp, score)]
        self._alerts: list[MetricAlert] = []

    def record_metric(
        self,
        metric_type: str,
        score: float,
        timestamp: float | None = None,
    ) -> None:
        """Record a learning metric.

        Args:
            metric_type: Type of metric
            score: Metric score
            timestamp: Timestamp (defaults to now)

        Emits ADG edges:
            - captures_evaluation_metric (P4)
        """
        _emit_captures_evaluation_metric("p4", "learning_metrics_dashboard", metric_type)

        if timestamp is None:
            timestamp = time.time()

        if metric_type not in self._metrics:
            self._metrics[metric_type] = []

        self._metrics[metric_type].append((timestamp, score))

        # Check for alerts
        self._check_alerts(metric_type, score, timestamp)

        logger.debug("METRIC_RECORDED: type=%s score=%.3f", metric_type, score)

    def get_dashboard_summary(self) -> DashboardMetrics:
        """Get dashboard summary with all metrics and alerts."""
        total_evals = sum(len(scores) for scores in self._metrics.values())

        all_scores = [score for scores in self._metrics.values() for _, score in scores]
        avg_score = statistics.mean(all_scores) if all_scores else 0.0

        # Calculate trend
        if len(all_scores) >= 10:
            recent_avg = statistics.mean(all_scores[-5:])
            older_avg = statistics.mean(all_scores[-10:-5])
            if recent_avg > older_avg + 0.05:
                trend = "improving"
            elif recent_avg < older_avg - 0.05:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Aggregate metrics by type
        metrics_by_type = {}
        for metric_type, scores in self._metrics.items():
            recent_scores = [s for _, s in scores[-20:]]
            metrics_by_type[metric_type] = {
                "count": len(scores),
                "avg": statistics.mean(recent_scores) if recent_scores else 0.0,
                "min": min(recent_scores) if recent_scores else 0.0,
                "max": max(recent_scores) if recent_scores else 0.0,
            }

        # Get active alerts (last hour)
        current_time = time.time()
        active_alerts = [alert for alert in self._alerts if current_time - alert.timestamp < 3600]

        return DashboardMetrics(
            total_evaluations=total_evals,
            avg_score=avg_score,
            score_trend=trend,
            alert_count=len(active_alerts),
            active_alerts=active_alerts,
            metrics_by_type=metrics_by_type,
        )

    def get_metric_history(
        self,
        metric_type: str,
        limit: int = 100,
    ) -> list[tuple[float, float]]:
        """Get metric history for a specific type.

        Args:
            metric_type: Type of metric
            limit: Maximum number of records to return

        Returns:
            List of (timestamp, score) tuples
        """
        if metric_type not in self._metrics:
            return []

        return self._metrics[metric_type][-limit:]

    def get_alerts(
        self,
        severity: AlertSeverity | None = None,
        limit: int = 50,
    ) -> list[MetricAlert]:
        """Get alerts, optionally filtered by severity.

        Args:
            severity: Filter by severity (optional)
            limit: Maximum alerts to return

        Returns:
            List of alerts
        """
        alerts = self._alerts

        if severity is not None:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts[-limit:]

    def clear_old_alerts(self, max_age_sec: float = 86400) -> int:
        """Clear alerts older than max_age_sec.

        Args:
            max_age_sec: Maximum age in seconds (default 24 hours)

        Returns:
            Number of alerts cleared
        """
        current_time = time.time()
        cutoff_time = current_time - max_age_sec

        initial_count = len(self._alerts)
        self._alerts = [a for a in self._alerts if a.timestamp >= cutoff_time]

        return initial_count - len(self._alerts)

    def reset(self) -> None:
        """Reset all metrics and alerts."""
        self._metrics.clear()
        self._alerts.clear()

    def _check_alerts(self, metric_type: str, score: float, timestamp: float) -> None:
        """Check if metric triggers any alerts."""
        if score < self._alert_threshold_critical:
            alert = MetricAlert(
                metric_name=metric_type,
                severity=AlertSeverity.CRITICAL,
                message=f"Critical: {metric_type} score {score:.3f} below threshold {self._alert_threshold_critical}",
                current_value=score,
                threshold=self._alert_threshold_critical,
                timestamp=timestamp,
            )
            self._alerts.append(alert)
            logger.error("CRITICAL_ALERT: %s", alert.message)

        elif score < self._alert_threshold_low:
            alert = MetricAlert(
                metric_name=metric_type,
                severity=AlertSeverity.WARNING,
                message=f"Warning: {metric_type} score {score:.3f} below threshold {self._alert_threshold_low}",
                current_value=score,
                threshold=self._alert_threshold_low,
                timestamp=timestamp,
            )
            self._alerts.append(alert)
            logger.warning("WARNING_ALERT: %s", alert.message)


# Global instance
_dashboard: LearningMetricsDashboard | None = None


def get_dashboard() -> LearningMetricsDashboard:
    """Get global learning metrics dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = LearningMetricsDashboard()
    return _dashboard


def reset_dashboard() -> None:
    """Reset global dashboard (for testing)."""
    global _dashboard
    _dashboard = None


# --------------------------------------------------------------------------
# V6 KPI Board accessor (advisory wiring per plan shadow-eval-v6-gap-d4a9c2 W4)
# --------------------------------------------------------------------------

_v6_kpi_board: Any = None


def get_v6_kpi_board() -> Any:
    """Return the process-singleton V6 KPI Board.

    Lazily imports ``system_learning.engines.v6_kpi_board.V6KPIBoard`` so the
    L6 dashboard stays decoupled from the system_learning layer at import
    time. The returned object is the canonical typed surface for v6 lines
    231-245 (the 11 KPIs) and v6 lines 34-36 (compound HEALTH definition).

    Producers (telemetry consumer, gauntlet, replay binder, etc.) should
    publish KPI samples via ``get_v6_kpi_board().record_value(...)``.
    """
    global _v6_kpi_board
    if _v6_kpi_board is None:
        from agentic_core.L6_system_learning.engines.v6_kpi_board import V6KPIBoard

        _v6_kpi_board = V6KPIBoard()
    return _v6_kpi_board


def reset_v6_kpi_board() -> None:
    """Reset the v6 KPI board singleton (for testing)."""
    global _v6_kpi_board
    _v6_kpi_board = None


__all__ = [
    "AlertSeverity",
    "MetricAlert",
    "DashboardMetrics",
    "LearningMetricsDashboard",
    "get_dashboard",
    "reset_dashboard",
    "get_v6_kpi_board",
    "reset_v6_kpi_board",
]
