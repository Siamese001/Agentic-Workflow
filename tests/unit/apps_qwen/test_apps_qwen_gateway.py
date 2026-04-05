"""Tests for apps_qwen gateway module."""
from __future__ import annotations

import unittest

import pytest

# Check if apps_qwen is available
try:
    from apps_qwen import AppsQwenGateway, AppsQwenRequest, AppsQwenResponse
    APPS_QWEN_AVAILABLE = True
except ImportError:
    APPS_QWEN_AVAILABLE = False


@pytest.mark.skipif(not APPS_QWEN_AVAILABLE, reason="apps_qwen modules not available")
class TestAppsQwenGateway(unittest.TestCase):
    """Test class for AppsQwenGateway."""

    def test_AppsQwenRequest_init(self):
        """Test AppsQwenRequest initialization."""
        instance = AppsQwenRequest(
            app_name="test_app",
            prompt="Test prompt",
            confidence_threshold=0.7,
            max_tokens=1024,
            temperature=0.3,
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.app_name, "test_app")
        self.assertEqual(instance.prompt, "Test prompt")

    def test_AppsQwenResponse_init(self):
        """Test AppsQwenResponse initialization."""
        instance = AppsQwenResponse(
            success=True,
            response="Test response",
            confidence=0.85,
            model_used="Qwen/Qwen2.5-7B-Instruct",
            latency_ms=100.0,
        )
        self.assertIsNotNone(instance)
        self.assertEqual(instance.success, True)
        self.assertEqual(instance.confidence, 0.85)


if __name__ == "__main__":
    unittest.main()
