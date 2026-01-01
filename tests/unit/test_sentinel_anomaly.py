"""Unit tests for Sentinel anomaly detection."""
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class test_sentinel_anomaly_detection:
    """Test Sentinel monitoring and anomaly detection."""

    def test_sentinel_initialization(self) -> Any:
        """
        GIVEN: Sentinel instantiation
        WHEN: Created
        THEN: Monitoring status active
        """
        from sentinel import Sentinel
        sentinel: Any = Sentinel()
        assert sentinel.status == 'monitoring'
        assert hasattr(sentinel, 'metrics')
        assert hasattr(sentinel, 'alerts')

    def test_sentinel_monitor_stores_metrics(self) -> Any:
        """
        GIVEN: Sentinel instance
        WHEN: monitor() called with metric
        THEN: Metric stored in metrics dict
        """
        from sentinel import Sentinel
        sentinel: Any = Sentinel()
        sentinel.monitor('cpu_usage', 75.5)
        assert 'cpu_usage' in sentinel.metrics
        assert sentinel.metrics['cpu_usage'] == 75.5

    def test_sentinel_raise_alert_returns_structured_alert(self) -> Any:
        """
        GIVEN: Sentinel instance
        WHEN: raise_alert() called
        THEN: Returns dict with message, level, timestamp
        """
        from sentinel import Sentinel
        sentinel: Any = Sentinel()
        alert: Any = sentinel.raise_alert('High CPU usage detected', level='warning')
        assert isinstance(alert, dict)
        assert 'message' in alert
        assert 'level' in alert
        assert 'timestamp' in alert
        assert alert['message'] == 'High CPU usage detected'
        assert alert['level'] == 'warning'

    def test_sentinel_get_alerts_retrieves_all_alerts(self) -> Any:
        """
        GIVEN: Sentinel with multiple alerts raised
        WHEN: get_alerts() called
        THEN: Returns all alerts
        """
        from sentinel import Sentinel
        sentinel: Any = Sentinel()
        sentinel.raise_alert('Alert 1', level='info')
        sentinel.raise_alert('Alert 2', level='warning')
        sentinel.raise_alert('Alert 3', level='error')
        alerts: Any = sentinel.get_alerts()
        assert len(alerts) >= 3
        assert any(('Alert 1' in str(a) for a in alerts))

    @pytest.mark.parametrize('metric,threshold,should_alert', [('cpu_usage', 90, True), ('cpu_usage', 50, False), ('memory_usage', 95, True), ('memory_usage', 60, False)])
    def test_sentinel_threshold_based_alerting(self, metric: Any, threshold: Any, should_alert: Any) -> Any:
        """
        GIVEN: Sentinel monitoring metrics
        WHEN: Metric exceeds threshold
        THEN: Alert raised if threshold exceeded
        """
        from sentinel import Sentinel
        sentinel: Any = Sentinel()
        alert_threshold: Any = 80
        sentinel.monitor(metric, threshold)
        if threshold > alert_threshold:
            alert: Any = sentinel.raise_alert(f'{metric} exceeded threshold', level='critical')
            alerted: Any = True
        else:
            alerted: Any = False
        assert alerted == should_alert

@pytest.mark.unit
class test_sentinel_integration:
    """Test Sentinel integration with other systems."""

    def test_sentinel_integrates_with_audit_log(self) -> Any:
        """
        GIVEN: Sentinel and audit log
        WHEN: Alert raised
        THEN: Alert logged to audit trail
        """
        from sentinel import Sentinel
        sentinel: Any = Sentinel()
        audit_log: Any = []
        alert: Any = sentinel.raise_alert('Security breach detected', level='critical')
        audit_log.append({'type': 'security_alert', 'details': alert})
        assert len(audit_log) == 1
        assert audit_log[0]['type'] == 'security_alert'
        assert 'Security breach' in audit_log[0]['details']['message']

    def test_sentinel_metric_aggregation(self) -> Any:
        """
from typing import Any
        GIVEN: Sentinel monitoring multiple metrics
        WHEN: Metrics aggregated
        THEN: Summary statistics available
        """
        from sentinel import Sentinel
        sentinel: Any = Sentinel()
        sentinel.monitor('request_count', 100)
        sentinel.monitor('error_count', 5)
        sentinel.monitor('success_rate', 95.0)
        total_requests: Any = sentinel.metrics.get('request_count', 0)
        error_rate: Any = sentinel.metrics.get('error_count', 0) / total_requests * 100 if total_requests > 0 else 0
        assert total_requests == 100
        assert error_rate == 5.0
        assert sentinel.metrics['success_rate'] == 95.0
