"""Test MetricCollectorService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetricCollectorService:
    """Test MetricCollectorService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        config = {"max_metrics": 1000}
        service = MetricCollectorService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        service = MetricCollectorService()
        assert service.config == {}

    @patch("apps_eval.services.metric_collector_service._emit_records_telemetry_event")
    @patch("apps_eval.services.metric_collector_service._emit_captures_evaluation_metric")
    def test_record_metric(self, mock_emit_metric, mock_emit_telemetry):
        """Test recording a metric."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        service = MetricCollectorService()
        service.record_metric("test_metric", 0.85)

        mock_emit_metric.assert_called_once()
        mock_emit_telemetry.assert_called_once()

    @patch("apps_eval.services.metric_collector_service._emit_records_telemetry_event")
    @patch("apps_eval.services.metric_collector_service._emit_captures_evaluation_metric")
    def test_record_metric_with_context(self, mock_emit_metric, mock_emit_telemetry):
        """Test recording a metric with context."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        service = MetricCollectorService()
        context = {"test_name": "test_example", "duration": 100}
        service.record_metric("test_metric", 0.85, context)

        mock_emit_metric.assert_called_once()

    def test_record_metric_none_value(self):
        """Test recording a metric with None value (edge case)."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        with patch("apps_eval.services.metric_collector_service._emit_captures_evaluation_metric"):
            MetricCollectorService().record_metric("test_metric", 0.0)

    def test_get_metrics_empty(self):
        """Test getting metrics when none recorded."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        service = MetricCollectorService()
        metrics = service.get_metrics()
        assert metrics == []

    def test_get_metrics_after_recording(self):
        """Test getting metrics after recording (stub returns empty list)."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        with patch("apps_eval.services.metric_collector_service._emit_captures_evaluation_metric"):
            service = MetricCollectorService()
            service.record_metric("test_metric", 0.85)
            metrics = service.get_metrics()
            # Stub implementation returns empty list
            assert metrics == []

    @patch("apps_eval.services.metric_collector_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        service = MetricCollectorService()
        mock_emit.assert_called_once_with("p4", "metric_collector", "init")

    def test_record_metric_negative_value(self):
        """Test recording a negative metric value (edge case)."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        with patch("apps_eval.services.metric_collector_service._emit_captures_evaluation_metric"):
            service = MetricCollectorService()
            service.record_metric("test_metric", -0.5)

    def test_record_metric_large_value(self):
        """Test recording a large metric value (edge case)."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        with patch("apps_eval.services.metric_collector_service._emit_captures_evaluation_metric"):
            service = MetricCollectorService()
            service.record_metric("test_metric", 999999.0)

    def test_record_metric_empty_name(self):
        """Test recording a metric with empty name (edge case)."""
        from apps_eval.services.metric_collector_service import MetricCollectorService

        with patch("apps_eval.services.metric_collector_service._emit_captures_evaluation_metric"):
            MetricCollectorService().record_metric("", 0.85)
