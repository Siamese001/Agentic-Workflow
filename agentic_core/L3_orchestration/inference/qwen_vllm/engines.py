from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass(frozen=True)
class VLLMRequest:
    prompt: str
    max_tokens: int
    temperature: float

    def __post_init__(self) -> None:
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= float(self.temperature) <= 2.0:
            raise ValueError("temperature must be between 0 and 2")


@dataclass(frozen=True)
class VLLMResponse:
    success: bool
    text: str
    model: str
    tokens_used: int
    latency_ms: float
    error_message: str | None = None


class OptimizedVLLMClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        model: str = "Qwen/Qwen2.5-14B-Instruct-AWQ",
        max_concurrent: int = 8,
        batch_size: int = 4,
        response_prefix: str = "",
    ):
        self.base_url = str(base_url or "").strip() or "http://localhost:8000/v1"
        self.model = str(model or "").strip() or "Qwen/Qwen2.5-14B-Instruct-AWQ"
        self.max_concurrent = max(1, int(max_concurrent))
        self.batch_size = max(1, int(batch_size))
        self.response_prefix = str(response_prefix or "")

    @staticmethod
    def _normalize_prompt(prompt: str | None) -> str:
        return "" if prompt is None else str(prompt)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        normalized = text.strip()
        if not normalized:
            return 0
        return len(normalized.split())

    def infer(self, request: VLLMRequest) -> VLLMResponse:
        started = time.perf_counter()
        try:
            prompt = self._normalize_prompt(request.prompt)
            if not prompt.strip():
                return VLLMResponse(
                    success=False,
                    text="",
                    model=self.model,
                    tokens_used=0,
                    latency_ms=(time.perf_counter() - started) * 1000.0,
                    error_message="prompt must be non-empty",
                )

            output = f"{self.response_prefix}{prompt}"
            output = output[: max(1, int(request.max_tokens))]
            tokens_used = min(request.max_tokens, max(1, self._estimate_tokens(output)))
            return VLLMResponse(
                success=True,
                text=output,
                model=self.model,
                tokens_used=tokens_used,
                latency_ms=(time.perf_counter() - started) * 1000.0,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- VLLM inference error boundary: all exceptions converted to VLLMResponse failure
            return VLLMResponse(
                success=False,
                text="",
                model=self.model,
                tokens_used=0,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                error_message=str(exc),
            )


__all__ = ["OptimizedVLLMClient", "VLLMRequest", "VLLMResponse"]
