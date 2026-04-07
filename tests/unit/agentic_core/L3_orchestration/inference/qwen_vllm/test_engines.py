"""Tests for Qwen vLLM engine components."""


from agentic_core.L3_orchestration.inference.qwen_vllm.engines import (
    OptimizedVLLMClient,
    VLLMRequest,
    VLLMResponse,
)


class TestVLLMRequest:
    """Test VLLMRequest dataclass."""

    def test_request_creation(self):
        """Test creating a VLLM request."""
        request = VLLMRequest(
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.1,
        )
        assert request.prompt == "Test prompt"
        assert request.max_tokens == 100
        assert request.temperature == 0.1


class TestVLLMResponse:
    """Test VLLMResponse dataclass."""

    def test_response_creation(self):
        """Test creating a VLLM response."""
        response = VLLMResponse(
            success=True,
            text="Test response",
            model="Qwen/Qwen2.5-7B-Instruct",
            tokens_used=50,
            latency_ms=100.0,
        )
        assert response.success is True
        assert response.text == "Test response"
        assert response.tokens_used == 50
        assert response.latency_ms == 100.0

    def test_response_creation_failure(self):
        """Test creating a failed VLLM response."""
        response = VLLMResponse(
            success=False,
            text="",
            model="Qwen/Qwen2.5-7B-Instruct",
            tokens_used=0,
            latency_ms=100.0,
            error_message="Connection failed",
        )
        assert response.success is False
        assert response.text == ""
        assert response.error_message == "Connection failed"


class TestOptimizedVLLMClient:
    """Test OptimizedVLLMClient with mocked dependencies."""

    def test_client_initialization(self):
        """Test client initialization with default parameters."""
        client = OptimizedVLLMClient(
            base_url="http://localhost:8000/v1",
            model="Qwen/Qwen2.5-7B-Instruct",
            max_concurrent=8,
            batch_size=4,
        )
        assert client.base_url == "http://localhost:8000/v1"
        assert client.model == "Qwen/Qwen2.5-7B-Instruct"
        assert client.max_concurrent == 8
        assert client.batch_size == 4

    def test_request_validation(self):
        """Test VLLM request validation logic."""
        # Test that request accepts empty string (dataclass has no validation)
        request = VLLMRequest(
            prompt="",
            max_tokens=100,
            temperature=0.1,
        )
        assert request.prompt == ""  # Dataclass accepts empty string
