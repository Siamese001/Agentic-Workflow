"""Apps Qwen Package - Backward Compatibility Wrapper.

DEPRECATED: This package has been moved to agentic_core.L3_orchestration.inference.qwen_vllm.
This module provides backward compatibility by re-exporting from the new location.

Please update your imports to:
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        QwenInferenceGateway,
        QwenInferenceRequest,
        QwenInferenceResponse,
    )

This compatibility layer will be removed in a future version.
"""

from __future__ import annotations

# Re-export from new location for backward compatibility
from agentic_core.L3_orchestration.inference.qwen_vllm import (
    # Configuration
    AppsQwenConfig,
    QwenInferenceConfig,
    QwenModelConfig,
    QwenPromptConfig,
    # Core gateway and request/response types
    AppsQwenGateway,
    AppsQwenRequest,
    AppsQwenResponse,
    QwenInferenceGateway,
    QwenInferenceRequest,
    QwenInferenceResponse,
    get_apps_qwen_gateway,
    close_apps_qwen_gateway,
    get_qwen_inference_gateway,
    close_qwen_inference_gateway,
    # Telemetry
    apps_qwen_telemetry,
    AppsQwenMetric,
    AppsQwenSessionMetrics,
    AppsQwenTelemetry,
    QwenInferenceMetric,
    QwenSessionMetrics,
    QwenInferenceTelemetry,
    qwen_inference_telemetry,
    # GPU memory monitoring
    GPUMemoryInfo,
    GPUMemoryMonitor,
    GPURecommendation,
    get_gpu_monitor,
    stop_gpu_monitor,
    # Engines
    AppsQwenInferenceWorker,
    QwenInferenceWorker,
    OptimizedVLLMClient,
    VLLMRequest,
    VLLMResponse,
    get_vllm_client,
    close_vllm_client,
    HardenedVLLMClient,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    RetryConfig,
    HardeningMetrics,
)

__all__ = [
    # Configuration
    "AppsQwenConfig",
    "QwenInferenceConfig",
    "QwenModelConfig",
    "QwenPromptConfig",
    # Core gateway and request/response types
    "AppsQwenGateway",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "QwenInferenceGateway",
    "QwenInferenceRequest",
    "QwenInferenceResponse",
    "get_apps_qwen_gateway",
    "close_apps_qwen_gateway",
    "get_qwen_inference_gateway",
    "close_qwen_inference_gateway",
    # Telemetry
    "apps_qwen_telemetry",
    "AppsQwenMetric",
    "AppsQwenSessionMetrics",
    "AppsQwenTelemetry",
    "QwenInferenceMetric",
    "QwenSessionMetrics",
    "QwenInferenceTelemetry",
    "qwen_inference_telemetry",
    # GPU memory monitoring
    "GPUMemoryInfo",
    "GPUMemoryMonitor",
    "GPURecommendation",
    "get_gpu_monitor",
    "stop_gpu_monitor",
    # Engines
    "AppsQwenInferenceWorker",
    "QwenInferenceWorker",
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
]

__version__ = "1.0.0"
