"""Apps Qwen Gateway - L2 Execution Layer.

Provides optimized Qwen v2.5 vLLM inference capabilities for applications layer.
Uses connection pooling, batching, and caching for maximum throughput.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from apps_qwen.optimized_vllm_client import (
    OptimizedVLLMClient,
    VLLMRequest,
    VLLMResponse,
)
from agentic_core.L3_orchestration.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_evaluation_metric,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_agent,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppsQwenRequest:
    """Request structure for apps Qwen inference."""
    app_name: str
    prompt: str
    confidence_threshold: float = 0.7
    max_tokens: int = 2048
    temperature: float = 0.1
    use_cache: bool = True  # Enable response caching


@dataclass(frozen=True)
class AppsQwenResponse:
    """Response structure for apps Qwen inference."""
    success: bool
    response: str | None
    confidence: float
    model_used: str
    latency_ms: float
    error_message: str | None = None
    cached: bool = False  # Whether response was from cache
    tokens_used: int = 0


class AppsQwenGateway:
    """Optimized gateway for apps Qwen inference.

    Features:
    - Connection pooling with HTTP keep-alive
    - Request batching for throughput
    - Response caching for identical prompts
    - Dynamic GPU memory monitoring
    - Telemetry integration
    """

    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-14B-Instruct-AWQ",
        base_url: str = "http://localhost:8000/v1",
        max_concurrent: int = 8,
        batch_size: int = 4,
    ):
        self.model_id = model_id
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self._vllm_client: OptimizedVLLMClient | None = None
        self._initialized = False
        self._emit_lifecycle_events()

    def _emit_lifecycle_events(self) -> None:
        """Emit lifecycle trace events for gateway initialization."""
        _emit_agent_executes_agent("apps_qwen_gateway", "apps_qwen_gateway", "qwen_vllm_inference")
        _emit_records_execution_trace("apps_qwen_gateway", "L2_EXECUTION", "initialization")

    async def _ensure_initialized(self) -> None:
        """Lazy initialization of vLLM client."""
        if not self._initialized:
            self._vllm_client = OptimizedVLLMClient(
                base_url=self.base_url,
                model=self.model_id,
                max_concurrent=self.max_concurrent,
                batch_size=self.batch_size,
            )
            await self._vllm_client.start()
            self._initialized = True
            logger.info("AppsQwenGateway initialized: model=%s, url=%s", self.model_id, self.base_url)

    async def infer(self, request: AppsQwenRequest) -> AppsQwenResponse:
        """Perform Qwen inference for apps request.

        Args:
            request: Apps Qwen request with prompt and parameters

        Returns:
            AppsQwenResponse with inference result
        """
        start_time = time.time()

        try:
            await self._ensure_initialized()
            _emit_routes_to_agent(request.app_name, request.app_name, "apps_qwen_gateway")

            # Create vLLM request
            vllm_request = VLLMRequest(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                request_id=f"{request.app_name}_{int(start_time * 1000)}",
            )

            # Execute inference
            vllm_response = await self._vllm_client.infer(vllm_request)

            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(vllm_response, request)

            latency_ms = (time.time() - start_time) * 1000

            if vllm_response.success:
                _emit_captures_evaluation_metric(
                    request.app_name, "apps_qwen_gateway", "inference_success"
                )

                return AppsQwenResponse(
                    success=True,
                    response=vllm_response.text,
                    confidence=confidence,
                    model_used=vllm_response.model or self.model_id,
                    latency_ms=latency_ms,
                    cached=vllm_response.cached,
                    tokens_used=vllm_response.tokens_used,
                )
            else:
                _emit_records_telemetry_event(
                    request.app_name, "apps_qwen_gateway", "inference_error"
                )

                return AppsQwenResponse(
                    success=False,
                    response=None,
                    confidence=0.0,
                    model_used=self.model_id,
                    latency_ms=latency_ms,
                    error_message=vllm_response.error_message or "Inference failed",
                    cached=False,
                    tokens_used=0,
                )

        except (ValueError, TypeError, RuntimeError) as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Inference failed: {str(e)}"
            logger.error("[%s] Inference error: %s", request.app_name, error_msg)

            _emit_records_telemetry_event(
                request.app_name, "apps_qwen_gateway", "inference_exception"
            )

            return AppsQwenResponse(
                success=False,
                response=None,
                confidence=0.0,
                model_used=self.model_id,
                latency_ms=latency_ms,
                error_message=error_msg,
                cached=False,
                tokens_used=0,
            )

    def _calculate_confidence(
        self,
        vllm_response: VLLMResponse,
        request: AppsQwenRequest
    ) -> float:
        """Calculate confidence score based on response characteristics.

        Factors:
        - Response length appropriateness
        - Token efficiency
        - No error indicators in text
        """
        if not vllm_response.success:
            return 0.0

        confidence = 0.85  # Base confidence

        text = vllm_response.text or ""

        # Penalize very short responses (likely errors)
        if len(text.strip()) < 10:
            confidence -= 0.2

        # Penalize error keywords
        error_indicators = ["error", "failed", "unable to", "cannot", "sorry"]
        text_lower = text.lower()
        for indicator in error_indicators:
            if indicator in text_lower:
                confidence -= 0.1

        # Boost for good token efficiency
        if vllm_response.tokens_used > 0:
            chars_per_token = len(text) / vllm_response.tokens_used
            if 2.0 <= chars_per_token <= 6.0:  # Reasonable range
                confidence += 0.05

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))

    async def infer_batch(
        self,
        requests: list[AppsQwenRequest]
    ) -> list[AppsQwenResponse]:
        """Perform batch inference for multiple requests.

        Args:
            requests: List of AppsQwenRequest

        Returns:
            List of AppsQwenResponse (order preserved)
        """
        await self._ensure_initialized()

        # Convert to VLLM requests
        vllm_requests = [
            VLLMRequest(
                prompt=req.prompt,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                request_id=f"{req.app_name}_{i}_{int(time.time() * 1000)}",
            )
            for i, req in enumerate(requests)
        ]

        # Execute batch
        vllm_responses = await self._vllm_client.infer_batch(vllm_requests)

        # Convert back to AppsQwenResponse
        results = []
        for req, vllm_resp in zip(requests, vllm_responses):
            if isinstance(vllm_resp, Exception):
                results.append(AppsQwenResponse(
                    success=False,
                    response=None,
                    confidence=0.0,
                    model_used=self.model_id,
                    latency_ms=0.0,
                    error_message=str(vllm_resp),
                ))
            else:
                confidence = self._calculate_confidence(vllm_resp, req)
                results.append(AppsQwenResponse(
                    success=vllm_resp.success,
                    response=vllm_resp.text if vllm_resp.success else None,
                    confidence=confidence,
                    model_used=vllm_resp.model or self.model_id,
                    latency_ms=vllm_resp.latency_ms,
                    error_message=vllm_resp.error_message,
                    cached=vllm_resp.cached,
                    tokens_used=vllm_resp.tokens_used,
                ))

        return results

    def health_check(self) -> dict[str, Any]:
        """Perform health check on gateway.

        Returns:
            Health status dictionary
        """
        _emit_records_execution_trace("apps_qwen_gateway", "L2_EXECUTION", "health_check")

        if not self._initialized or not self._vllm_client:
            return {
                "status": "not_initialized",
                "healthy": False,
                "model_id": self.model_id,
            }

        # Get metrics from vLLM client
        metrics = self._vllm_client.get_metrics()

        return {
            "status": "healthy" if metrics else "degraded",
            "healthy": bool(metrics),
            "model_id": self.model_id,
            "gpu_utilization": QWEN_GPU_MEM_UTIL,
            "metrics": metrics,
            "timestamp": time.time(),
        }

    async def async_health_check(self) -> dict[str, Any]:
        """Async health check that queries vLLM server."""
        await self._ensure_initialized()

        vllm_health = await self._vllm_client.health_check()
        metrics = self._vllm_client.get_metrics()

        return {
            **vllm_health,
            "metrics": metrics,
            "model_id": self.model_id,
            "timestamp": time.time(),
        }

    async def close(self) -> None:
        """Cleanup resources."""
        if self._vllm_client:
            await self._vllm_client.stop()
            self._initialized = False
            logger.info("AppsQwenGateway closed")

    async def __aenter__(self) -> AppsQwenGateway:
        """Async context manager entry."""
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Singleton instance for apps layer
_apps_qwen_gateway: AppsQwenGateway | None = None


async def get_apps_qwen_gateway(
    model_id: str = "Qwen/Qwen2.5-14B-Instruct-AWQ",
) -> AppsQwenGateway:
    """Get or create singleton AppsQwenGateway."""
    global _apps_qwen_gateway
    if _apps_qwen_gateway is None:
        _apps_qwen_gateway = AppsQwenGateway(model_id=model_id)
        await _apps_qwen_gateway._ensure_initialized()
    return _apps_qwen_gateway


async def close_apps_qwen_gateway() -> None:
    """Close singleton AppsQwenGateway."""
    global _apps_qwen_gateway
    if _apps_qwen_gateway:
        await _apps_qwen_gateway.close()
        _apps_qwen_gateway = None


__all__ = [
    "AppsQwenGateway",
    "AppsQwenRequest",
    "AppsQwenResponse",
    "get_apps_qwen_gateway",
    "close_apps_qwen_gateway",
]
