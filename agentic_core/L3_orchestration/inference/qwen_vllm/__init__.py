"""Stable compatibility exports for the qwen_vllm shim package."""

from .config import QwenInferenceConfig, QwenModelConfig, QwenPromptConfig
from .engines import OptimizedVLLMClient, VLLMRequest, VLLMResponse
from .reasoning import (
    AppsQwenGateway,
    AppsQwenRequest,
    AppsQwenResponse,
    QwenInferenceGateway,
    QwenInferenceRequest,
    QwenInferenceResponse,
)
from .telemetry import (
    AppsQwenMetric,
    AppsQwenSessionMetrics,
    AppsQwenTelemetry,
    QwenInferenceMetric,
    QwenInferenceTelemetry,
    QwenSessionMetrics,
)

# Module-level singleton for backward-compat with apps_* importing
# `apps_qwen_telemetry` (lowercase instance). Class-level name
# `AppsQwenTelemetry` remains canonical for type usage.
from .tools import GPUMemoryInfo, GPUMemoryMonitor, GPURecommendation

apps_qwen_telemetry = AppsQwenTelemetry()

__all__ = [
    "AppsQwenGateway",
    "AppsQwenMetric",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "AppsQwenSessionMetrics",
    "AppsQwenTelemetry",
    "GPUMemoryInfo",
    "GPUMemoryMonitor",
    "GPURecommendation",
    "OptimizedVLLMClient",
    "QwenInferenceConfig",
    "QwenInferenceGateway",
    "QwenInferenceMetric",
    "QwenInferenceRequest",
    "QwenInferenceResponse",
    "QwenInferenceTelemetry",
    "QwenModelConfig",
    "QwenPromptConfig",
    "QwenSessionMetrics",
    "VLLMRequest",
    "VLLMResponse",
    "apps_qwen_telemetry",
]
