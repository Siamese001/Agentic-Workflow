from __future__ import annotations

import os
from dataclasses import dataclass
import time

from .engines import OptimizedVLLMClient, VLLMRequest


@dataclass(frozen=True)
class QwenInferenceRequest:
    app_name: str
    prompt: str
    max_tokens: int
    temperature: float
    confidence_threshold: float = 0.5

    def __post_init__(self) -> None:
        if not isinstance(self.app_name, str) or not self.app_name.strip():
            raise ValueError("app_name must be a non-empty string")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= float(self.temperature) <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if not 0.0 <= float(self.confidence_threshold) <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")


@dataclass(frozen=True)
class QwenInferenceResponse:
    success: bool
    response: str | None
    confidence: float
    model_used: str
    latency_ms: float
    error_message: str | None = None


class QwenInferenceGateway:
    def __init__(
        self,
        model_id: str | None = None,
        base_url: str | None = None,
        max_concurrent: int = 8,
        batch_size: int = 4,
        client: OptimizedVLLMClient | None = None,
    ):
        self.model_id = str(model_id or "").strip() or os.getenv("VLLM_MODEL_NAME") or "Qwen/Qwen2.5-14B-Instruct-AWQ"
        self.base_url = str(base_url or "").strip() or os.getenv("VLLM_BASE_URL") or "http://localhost:8000/v1"
        self.max_concurrent = max(1, int(max_concurrent))
        self.batch_size = max(1, int(batch_size))
        self._client = client or OptimizedVLLMClient(
            base_url=self.base_url,
            model=self.model_id,
            max_concurrent=self.max_concurrent,
            batch_size=self.batch_size,
        )

    def infer(self, request: QwenInferenceRequest) -> QwenInferenceResponse:
        started = time.perf_counter()
        try:
            engine_response = self._client.infer(
                VLLMRequest(
                    prompt=request.prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )
            )
            if not engine_response.success:
                return QwenInferenceResponse(
                    success=False,
                    response=None,
                    confidence=0.0,
                    model_used=self.model_id,
                    latency_ms=(time.perf_counter() - started) * 1000.0,
                    error_message=engine_response.error_message,
                )
            return QwenInferenceResponse(
                success=True,
                response=engine_response.text,
                confidence=max(0.0, min(1.0, float(request.confidence_threshold))),
                model_used=self.model_id,
                latency_ms=(time.perf_counter() - started) * 1000.0,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- Qwen inference error boundary: all exceptions converted to QwenInferenceResponse failure
            return QwenInferenceResponse(
                success=False,
                response=None,
                confidence=0.0,
                model_used=self.model_id,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                error_message=str(exc),
            )


AppsQwenGateway = QwenInferenceGateway
AppsQwenRequest = QwenInferenceRequest
AppsQwenResponse = QwenInferenceResponse

__all__ = [
    "AppsQwenGateway",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "QwenInferenceGateway",
    "QwenInferenceRequest",
    "QwenInferenceResponse",
]
