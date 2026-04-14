"""Tests for Qwen vLLM gateway orchestration."""

from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning import (
    QwenInferenceGateway,
    QwenInferenceRequest,
    QwenInferenceResponse,
)


class TestQwenInferenceRequest:
    """Test QwenInferenceRequest dataclass."""

    def test_request_creation(self):
        """Test creating an AppsQwen request."""
        request = QwenInferenceRequest(
            app_name="test_app",
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.1,
        )
        assert request.app_name == "test_app"
        assert request.prompt == "Test prompt"
        assert request.max_tokens == 100
        assert request.temperature == 0.1


class TestQwenInferenceResponse:
    """Test QwenInferenceResponse dataclass."""

    def test_response_creation(self):
        """Test creating an AppsQwen response."""
        response = QwenInferenceResponse(
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

    def test_response_creation_failure(self):
        """Test creating a failed AppsQwen response."""
        response = QwenInferenceResponse(
            success=False,
            response=None,
            confidence=0.0,
            model_used="Qwen/Qwen2.5-7B-Instruct",
            latency_ms=100.0,
            error_message="Inference failed",
        )
        assert response.success is False
        assert response.response is None
        assert response.error_message == "Inference failed"


class TestQwenInferenceGateway:
    """Test QwenInferenceGateway with mocked dependencies."""

    def test_gateway_initialization(self):
        """Test gateway initialization."""
        gateway = QwenInferenceGateway()
        assert gateway is not None
        assert gateway.model_id == "Qwen/Qwen2.5-14B-Instruct-AWQ"
        assert gateway.base_url == "http://localhost:8000/v1"

    def test_gateway_initialization_with_params(self):
        """Test gateway initialization with custom parameters."""
        gateway = QwenInferenceGateway(
            model_id="custom_model",
            base_url="http://localhost:9000/v1",
            max_concurrent=16,
            batch_size=8,
        )
        assert gateway.model_id == "custom_model"
        assert gateway.base_url == "http://localhost:9000/v1"
        assert gateway.max_concurrent == 16
        assert gateway.batch_size == 8

    def test_request_validation(self):
        """Test request validation logic."""
        # Test that request accepts empty string (dataclass has no validation)
        request = QwenInferenceRequest(
            app_name="test",
            prompt="",
            max_tokens=100,
            temperature=0.1,
        )
        assert request.prompt == ""  # Dataclass accepts empty string
