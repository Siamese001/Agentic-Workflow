"""Qwen vLLM Inference Engines."""

from .hardened_vllm_client import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    HardenedVLLMClient,
    HardeningMetrics,
    RetryConfig,
)
from .optimized_vllm_client import (
    OptimizedVLLMClient,
    VLLMRequest,
    VLLMResponse,
    close_vllm_client,
    get_vllm_client,
)

# Backward compatibility re-exports
from .qwen_inference_worker import AppsQwenInferenceWorker, QwenInferenceWorker

__all__ = [
    "OptimizedVLLMClient",
    "VLLMRequest",
    "VLLMResponse",
    "get_vllm_client",
    "close_vllm_client",
    "HardenedVLLMClient",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerOpenError",
    "CircuitState",
    "RetryConfig",
    "HardeningMetrics",
    "QwenInferenceWorker",
    # Backward compatibility
    "AppsQwenInferenceWorker",
]
