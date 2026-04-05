"""Qwen vLLM Inference Gateway."""

from .qwen_inference_gateway import (
    QwenInferenceGateway,
    QwenInferenceRequest,
    QwenInferenceResponse,
    get_qwen_inference_gateway,
    close_qwen_inference_gateway,
)

# Backward compatibility re-exports
from .qwen_inference_gateway import (
    AppsQwenGateway,
    AppsQwenRequest,
    AppsQwenResponse,
    get_apps_qwen_gateway,
    close_apps_qwen_gateway,
)

__all__ = [
    "QwenInferenceGateway",
    "QwenInferenceRequest",
    "QwenInferenceResponse",
    "get_qwen_inference_gateway",
    "close_qwen_inference_gateway",
    # Backward compatibility
    "AppsQwenGateway",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "get_apps_qwen_gateway",
    "close_apps_qwen_gateway",
]
