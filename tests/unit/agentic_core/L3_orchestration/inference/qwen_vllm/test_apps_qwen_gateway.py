"""Tests for Qwen vLLM gateway module."""
from __future__ import annotations

import unittest

import pytest

# Check if qwen_vllm is available
try:
    # Also import backward compatibility aliases
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        AppsQwenGateway,
        AppsQwenRequest,
        AppsQwenResponse,
        QwenInferenceGateway,
        QwenInferenceRequest,
        QwenInferenceResponse,
    )
    QWEN_VLLM_AVAILABLE = True
except ImportError:
    QWEN_VLLM_AVAILABLE = False


@pytest.mark.skipif(not QWEN_VLLM_AVAILABLE, reason="qwen_vllm modules not available")
class TestQwenInferenceGateway(unittest.TestCase):
    """Test class for QwenInferenceGateway."""

    def test_QwenInferenceRequest_init(self):
        """Test QwenInferenceRequest initialization."""
        instance = QwenInferenceRequest(
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
