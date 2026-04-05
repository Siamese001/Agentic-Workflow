"""Tests for apps_qwen telemetry module."""
from __future__ import annotations

import time
import unittest

import pytest

# Check if apps_qwen is available
try:
    from apps_qwen import AppsQwenMetric, AppsQwenSessionMetrics, AppsQwenTelemetry
    APPS_QWEN_AVAILABLE = True
except ImportError:
    APPS_QWEN_AVAILABLE = False


@pytest.mark.skipif(not APPS_QWEN_AVAILABLE, reason="apps_qwen modules not available")
class TestAppsQwenTelemetry(unittest.TestCase):
    """Test class for AppsQwenTelemetry."""

    def test_start_session(self):
        """Test start_session method."""
        telemetry = AppsQwenTelemetry()
        result = telemetry.start_session("test_app")
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("test_app_"))

    def test_end_session(self):
        """Test end_session method."""
        telemetry = AppsQwenTelemetry()
        session_id = telemetry.start_session("test_app")
        result = telemetry.end_session(session_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.session_id, session_id)

    def test_AppsQwenMetric_init(self):
        """Test AppsQwenMetric initialization."""
        instance = AppsQwenMetric(
            timestamp=time.time(),
            app_name="test_app",
            model_id="Qwen/Qwen2.5-7B-Instruct",
            metric_name="confidence",
            value=0.95,
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.app_name, "test_app")
        self.assertEqual(instance.metric_name, "confidence")

    def test_AppsQwenSessionMetrics_init(self):
        """Test AppsQwenSessionMetrics initialization."""
        instance = AppsQwenSessionMetrics(
            session_id="test_session_123",
            app_name="test_app",
            start_time=time.time(),
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.session_id, "test_session_123")
        self.assertEqual(instance.app_name, "test_app")


if __name__ == "__main__":
    unittest.main()
