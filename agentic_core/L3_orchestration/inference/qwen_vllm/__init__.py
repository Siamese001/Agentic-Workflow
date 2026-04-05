"""Qwen vLLM Inference Service for L3 Orchestration.

This module provides optimized Qwen v2.5 vLLM inference capabilities
for the L3 orchestration layer, including:
- Configuration management
- vLLM client engines (optimized and hardened)
- Inference gateway with pooling and batching
- GPU memory monitoring
- Telemetry collection

Example usage:
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        QwenInferenceGateway,
        QwenInferenceRequest,
        QwenInferenceConfig,
    )

    gateway = QwenInferenceGateway()
    request = QwenInferenceRequest(app_name="my_app", prompt="Hello")
    response = await gateway.infer(request)
"""

# Configuration
from .config import (
    QwenInferenceConfig,
    QwenModelConfig,
    QwenPromptConfig,
    QwenInferenceTelemetry,
    QwenInferenceMetric,
    QwenSessionMetrics,
    qwen_inference_telemetry,
)

# Engines
from .engines import (
    OptimizedVLLMClient,
    VLLMRequest,
    VLLMResponse,
    HardenedVLLMClient,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    RetryConfig,
    HardeningMetrics,
    QwenInferenceWorker,
    get_vllm_client,
    close_vllm_client,
)

# Reasoning/Gateway
from .reasoning import (
    QwenInferenceGateway,
    QwenInferenceRequest,
    QwenInferenceResponse,
    get_qwen_inference_gateway,
    close_qwen_inference_gateway,
)

# Tools
from .tools import (
    GPUMemoryInfo,
    GPUMemoryMonitor,
    GPURecommendation,
    get_gpu_monitor,
    stop_gpu_monitor,
)

# Backward compatibility re-exports (for gradual migration)
from .config import (
    AppsQwenConfig,
    AppsQwenModelConfig,
    AppsQwenPromptConfig,
    AppsQwenTelemetry,
    AppsQwenMetric,
    AppsQwenSessionMetrics,
    apps_qwen_telemetry,
)
from .engines import AppsQwenInferenceWorker
from .reasoning import (
    AppsQwenGateway,
    AppsQwenRequest,
    AppsQwenResponse,
    get_apps_qwen_gateway,
    close_apps_qwen_gateway,
)

__all__ = [
    # Configuration
    "QwenInferenceConfig",
    "QwenModelConfig",
    "QwenPromptConfig",
    "QwenInferenceTelemetry",
    "QwenInferenceMetric",
    "QwenSessionMetrics",
    "qwen_inference_telemetry",
    # Engines
    "OptimizedVLLMClient",
    "VLLMRequest",
    "VLLMResponse",
    "HardenedVLLMClient",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerOpenError",
    "CircuitState",
    "RetryConfig",
    "HardeningMetrics",
    "QwenInferenceWorker",
    "get_vllm_client",
    "close_vllm_client",
    # Reasoning/Gateway
    "QwenInferenceGateway",
    "QwenInferenceRequest",
    "QwenInferenceResponse",
    "get_qwen_inference_gateway",
    "close_qwen_inference_gateway",
    # Tools
    "GPUMemoryInfo",
    "GPUMemoryMonitor",
    "GPURecommendation",
    "get_gpu_monitor",
    "stop_gpu_monitor",
    # Backward compatibility
    "AppsQwenConfig",
    "AppsQwenModelConfig",
    "AppsQwenPromptConfig",
    "AppsQwenTelemetry",
    "AppsQwenMetric",
    "AppsQwenSessionMetrics",
    "apps_qwen_telemetry",
    "AppsQwenInferenceWorker",
    "AppsQwenGateway",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "get_apps_qwen_gateway",
    "close_apps_qwen_gateway",
]