"""Qwen vLLM Inference Service for L3 Orchestration.

This module provides Qwen/Qwen2.5-7B-Instruct vLLM inference for apps_* orchestrators.

Supported runtime path (apps_rg, apps_exec, apps_research, apps_rfp, apps_lic):
    app → routing predicates → VLLMGatewayAdapter → AppsQwenGateway
        → HardenedVLLMClient → OptimizedVLLMClient → local vLLM

apps_eval uses AppsQwenGateway directly (controlled/opt-in, no adapter gate).

Canonical topology reference: docs/architecture/qwen-vllm-topology.md

Supported app-facing imports:
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        AppsQwenGateway,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )

    gateway = AppsQwenGateway(model_id="Qwen/Qwen2.5-7B-Instruct")
    request = AppsQwenRequest(app_name="my_app", prompt="Hello", confidence_threshold=0.8)
    response = await gateway.infer(request)
"""

# Configuration
# Apps-level aliases (migration complete; retained for external configuration use)
from .config import (
    AppsQwenConfig,
    AppsQwenMetric,
    AppsQwenModelConfig,
    AppsQwenPromptConfig,
    AppsQwenSessionMetrics,
    AppsQwenTelemetry,
    QwenInferenceConfig,
    QwenInferenceMetric,
    QwenInferenceTelemetry,
    QwenModelConfig,
    QwenPromptConfig,
    QwenSessionMetrics,
    apps_qwen_telemetry,
    qwen_inference_telemetry,
)

# Engines
from .engines import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    HardenedVLLMClient,
    HardeningMetrics,
    OptimizedVLLMClient,
    RetryConfig,
    VLLMRequest,
    VLLMResponse,
    close_vllm_client,
    get_vllm_client,
)

# Reasoning/Gateway
from .reasoning import (
    AppsQwenGateway,
    AppsQwenRequest,
    AppsQwenResponse,
    QwenInferenceGateway,
    QwenInferenceRequest,
    QwenInferenceResponse,
    close_apps_qwen_gateway,
    close_qwen_inference_gateway,
    get_apps_qwen_gateway,
    get_qwen_inference_gateway,
)

# Tools
from .tools import (
    GPUMemoryInfo,
    GPUMemoryMonitor,
    GPURecommendation,
    get_gpu_monitor,
    stop_gpu_monitor,
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
    "AppsQwenGateway",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "get_apps_qwen_gateway",
    "close_apps_qwen_gateway",
]
