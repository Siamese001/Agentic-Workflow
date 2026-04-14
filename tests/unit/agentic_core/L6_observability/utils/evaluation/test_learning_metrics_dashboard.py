"""
tests/unit/agentic_core/L6_observability/evaluation/test_learning_metrics_dashboard.py

Unit tests for Wave 2.4: Learning Metrics Dashboard
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability.utils.evaluation.learning_metrics_dashboard import (
    AlertSeverity,
    DashboardMetrics,
    LearningMetricsDashboard,
    get_dashboard,
    reset_dashboard,
)


class TestLearningMetricsDashboard:
    """Test suite for LearningMetricsDashboard."""

    def test_record_metric(self):
        """Test recording metrics."""
        dashboard = LearningMetricsDashboard()

        dashboard.record_metric("faithfulness", 0.85)
        dashboard.record_metric("groundedness", 0.90)

        summary = dashboard.get_dashboard_summary()
        assert summary.total_evaluations == 2
        assert "faithfulness" in summary.metrics_by_type
        assert "groundedness" in summary.metrics_by_type

    def test_alert_generation_warning(self):
        """Test warning alert generation."""
        dashboard = LearningMetricsDashboard(alert_threshold_low=0.7)

        dashboard.record_metric("test", 0.6)  # Below warning threshold

        alerts = dashboard.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_alert_generation_critical(self):
        """Test critical alert generation."""
        dashboard = LearningMetricsDashboard(alert_threshold_critical=0.5)

        dashboard.record_metric("test", 0.4)  # Below critical threshold

        alerts = dashboard.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_dashboard_summary(self):
        """Test dashboard summary generation."""
        dashboard = LearningMetricsDashboard()

        for i in range(10):
            dashboard.record_metric("test", 0.8 + i * 0.01)

        summary = dashboard.get_dashboard_summary()
        assert isinstance(summary, DashboardMetrics)
        assert summary.total_evaluations == 10
        assert summary.avg_score > 0.0

    def test_metric_history(self):
        """Test retrieving metric history."""
        dashboard = LearningMetricsDashboard()

        for i in range(5):
            dashboard.record_metric("test", 0.8 + i * 0.01, time.time() + i)

        history = dashboard.get_metric_history("test")
        assert len(history) == 5

    def test_clear_old_alerts(self):
        """Test clearing old alerts."""
        dashboard = LearningMetricsDashboard(alert_threshold_low=0.7)

        # Generate alerts
        dashboard.record_metric("test", 0.6, time.time() - 100000)  # Old
        dashboard.record_metric("test", 0.6, time.time())  # Recent

        cleared = dashboard.clear_old_alerts(max_age_sec=3600)
        assert cleared == 1

    def test_reset(self):
        """Test resetting dashboard."""
        dashboard = LearningMetricsDashboard()

        dashboard.record_metric("test", 0.85)
        dashboard.reset()

        summary = dashboard.get_dashboard_summary()
        assert summary.total_evaluations == 0


class TestGlobalInstance:
    """Test global instance management."""

    def test_singleton_pattern(self):
        """Test dashboard singleton pattern."""
        reset_dashboard()

        dashboard1 = get_dashboard()
        dashboard2 = get_dashboard()

        assert dashboard1 is dashboard2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
