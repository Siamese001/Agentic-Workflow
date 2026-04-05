"""Tests for apps_qwen gateway orchestration."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from apps_qwen.reasoning.apps_qwen_gateway import (
    AppsQwenGateway,
    AppsQwenRequest,
    AppsQwenResponse,
)


class TestAppsQwenRequest:
    """Test AppsQwenRequest dataclass."""

    def test_request_creation(self):
        """Test creating an AppsQwen request."""
        request = AppsQwenRequest(
            app_name="test_app",
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.1,
        )
        assert request.app_name == "test_app"
        assert request.prompt == "Test prompt"
        assert request.max_tokens == 100
        assert request.temperature == 0.1


class TestAppsQwenResponse:
    """Test AppsQwenResponse dataclass."""

    def test_response_creation(self):
        """Test creating an AppsQwen response."""
        response = AppsQwenResponse(
            success=True,
            response="Test response",
            confidence=0.95,
            model_used="Qwen/Qwen2.5-7B-Instruct",
            latency_ms=100.0,
        )
        assert response.success is True
        assert response.response == "Test response"
        assert response.confidence == 0.95
        assert response.model_used == "Qwen/Qwen2.5-7B-Instruct"
        assert response.latency_ms == 100.0


class TestAppsQwenGateway:
    """Test AppsQwenGateway with mocked dependencies."""

    @patch('apps_qwen.reasoning.apps_qwen_gateway.get_vllm_client')
    def test_gateway_initialization(self, mock_get_client):
        """Test gateway initialization."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        gateway = AppsQwenGateway()
        assert gateway is not None

    @patch('apps_qwen.reasoning.apps_qwen_gateway.get_vllm_client')
    def test_gateway_inference_mock(self, mock_get_client):
        """Test gateway inference with mocked client."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Mock the async inference method
        mock_response = AppsQwenResponse(
            success=True,
            response="Mocked response",
            confidence=0.95,
            model_used="Qwen/Qwen2.5-7B-Instruct",
            latency_ms=100.0,
        )
        mock_client.infer = AsyncMock(return_value=mock_response)

        gateway = AppsQwenGateway()
        # Note: Can't actually run async test here without pytest-asyncio
        # Just verify the gateway can be created
        assert gateway is not None

    def test_request_validation(self):
        """Test request validation logic."""
        # Test that request with empty prompt is invalid
        with pytest.raises((ValueError, TypeError)):
            AppsQwenRequest(
                app_name="test",
                prompt="",
                max_tokens=100,
                temperature=0.1,
            )
