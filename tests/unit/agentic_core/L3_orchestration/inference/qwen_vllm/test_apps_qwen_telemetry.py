"""Tests for Qwen vLLM telemetry module."""

from __future__ import annotations

import time
import unittest

import pytest

# Check if qwen_vllm is available
try:
    # Also import backward compatibility aliases
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        AppsQwenMetric,
        AppsQwenSessionMetrics,
        AppsQwenTelemetry,
        QwenInferenceMetric,
        QwenInferenceTelemetry,
        QwenSessionMetrics,
    )

    QWEN_VLLM_AVAILABLE = True
except ImportError:
    QWEN_VLLM_AVAILABLE = False


@pytest.mark.skipif(not QWEN_VLLM_AVAILABLE, reason="qwen_vllm modules not available")
class TestQwenInferenceTelemetry(unittest.TestCase):
    """Test class for QwenInferenceTelemetry."""

    def test_start_session(self):
        """Test start_session method."""
        telemetry = QwenInferenceTelemetry()
        result = telemetry.start_session("test_app")
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("test_app_"))

    def test_end_session(self):
        """Test end_session method."""
        telemetry = QwenInferenceTelemetry()
        session_id = telemetry.start_session("test_app")
        result = telemetry.end_session(session_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.session_id, session_id)

    def test_QwenInferenceMetric_init(self):
        """Test QwenInferenceMetric initialization."""
        instance = QwenInferenceMetric(
            timestamp=time.time(),
            app_name="test_app",
            model_id="Qwen/Qwen2.5-7B-Instruct",
            metric_name="confidence",
            value=0.95,
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.app_name, "test_app")
        self.assertEqual(instance.metric_name, "confidence")

    def test_QwenSessionMetrics_init(self):
        """Test QwenSessionMetrics initialization."""
        instance = QwenSessionMetrics(
            session_id="test_session_123",
            app_name="test_app",
            start_time=time.time(),
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.session_id, "test_session_123")
        self.assertEqual(instance.app_name, "test_app")


if __name__ == "__main__":
    unittest.main()
