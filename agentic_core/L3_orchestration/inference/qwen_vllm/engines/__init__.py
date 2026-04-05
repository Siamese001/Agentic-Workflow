"""Qwen vLLM Inference Engines."""

from .optimized_vllm_client import OptimizedVLLMClient, VLLMRequest, VLLMResponse, get_vllm_client, close_vllm_client
from .hardened_vllm_client import HardenedVLLMClient, CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenError, CircuitState, RetryConfig, HardeningMetrics
from .qwen_inference_worker import QwenInferenceWorker

# Backward compatibility re-exports
from .qwen_inference_worker import AppsQwenInferenceWorker

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