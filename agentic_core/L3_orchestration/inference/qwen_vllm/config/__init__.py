"""Qwen vLLM Inference Configuration."""

# Backward compatibility re-exports
from .qwen_config import (
    AppsQwenConfig,
    AppsQwenModelConfig,
    AppsQwenPromptConfig,
    QwenInferenceConfig,
    QwenModelConfig,
    QwenPromptConfig,
)
from .qwen_telemetry import (
    AppsQwenMetric,
    AppsQwenSessionMetrics,
    AppsQwenTelemetry,
    QwenInferenceMetric,
    QwenInferenceTelemetry,
    QwenSessionMetrics,
    apps_qwen_telemetry,
    qwen_inference_telemetry,
)

__all__ = [
    "QwenInferenceConfig",
    "QwenModelConfig",
    "QwenPromptConfig",
    "QwenInferenceTelemetry",
    "QwenInferenceMetric",
    "QwenSessionMetrics",
    "qwen_inference_telemetry",
    # Backward compatibility
    "AppsQwenConfig",
    "AppsQwenModelConfig",
    "AppsQwenPromptConfig",
    "AppsQwenTelemetry",
    "AppsQwenMetric",
    "AppsQwenSessionMetrics",
    "apps_qwen_telemetry",
]
