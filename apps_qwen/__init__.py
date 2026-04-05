"""Apps Qwen Package - Optimized vLLM Integration for Applications Layer.

Provides high-performance Qwen v2.5 inference capabilities with:
- Connection pooling and HTTP keep-alive
- Request batching for throughput optimization
- Response caching for identical prompts
- Dynamic GPU memory monitoring
- Async concurrency controls

Usage:
    from apps_qwen import AppsQwenGateway, AppsQwenRequest

    gateway = AppsQwenGateway()
    request = AppsQwenRequest(
        app_name="my_app",
        prompt="What is 2+2?",
        max_tokens=100,
        temperature=0.1,
    )
    response = await gateway.infer(request)
    print(response.response)
"""

from __future__ import annotations

# Configuration
from apps_qwen.config.apps_qwen_config import AppsQwenConfig

# Core gateway and request/response types
from apps_qwen.reasoning.apps_qwen_gateway import (
    AppsQwenGateway,
    AppsQwenRequest,
    AppsQwenResponse,
    close_apps_qwen_gateway,
    get_apps_qwen_gateway,
)

# Telemetry
from apps_qwen.config.apps_qwen_telemetry import apps_qwen_telemetry

# GPU memory monitoring
from apps_qwen.tools.gpu_memory_monitor import (
    GPUMemoryInfo,
    GPUMemoryMonitor,
    GPURecommendation,
    get_gpu_monitor,
    stop_gpu_monitor,
)

# Hardened vLLM client
from apps_qwen.engines.hardened_vllm_client import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    HardenedVLLMClient,
    HardeningMetrics,
    RetryConfig,
)

# Optimized vLLM client
from apps_qwen.engines.optimized_vllm_client import (
    OptimizedVLLMClient,
    VLLMRequest,
    VLLMResponse,
    close_vllm_client,
    get_vllm_client,
)

__version__ = "1.0.0"

__all__ = [
    # Gateway
    "AppsQwenGateway",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "get_apps_qwen_gateway",
    "close_apps_qwen_gateway",
    # Optimized vLLM Client
    "OptimizedVLLMClient",
    "VLLMRequest",
    "VLLMResponse",
    "get_vllm_client",
    "close_vllm_client",
    # Hardened vLLM Client
    "HardenedVLLMClient",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "RetryConfig",
    "HardeningMetrics",
    "CircuitState",
    "CircuitBreakerOpenError",
    # GPU Monitoring
    "GPUMemoryInfo",
    "GPURecommendation",
    "GPUMemoryMonitor",
    "get_gpu_monitor",
    "stop_gpu_monitor",
    # Configuration
    "AppsQwenConfig",
    # Telemetry
    "apps_qwen_telemetry",
]
