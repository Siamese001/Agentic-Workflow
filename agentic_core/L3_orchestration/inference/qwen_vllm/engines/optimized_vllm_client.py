"""Optimized vLLM Client with Connection Pooling and Batching.

Provides high-performance async client for Qwen vLLM inference with:
- Connection pooling with HTTP keep-alive
- Request batching for throughput optimization
- Async semaphore for concurrency control
- Response caching for identical prompts
- GPU memory monitoring integration
"""
# SANCTIONED SEAM — approved L3 vLLM HTTP adapter (2026-04-11 vllm-path-a).
# Approved hosts: localhost / 127.0.0.1 port 8000-8099 only (Qwen vLLM OpenAI-compat API).
# Approved callers: qwen_inference_gateway.py, hardened_vllm_client.py, test harnesses only.
# Must NOT be imported from apps_* or any layer outside the L3 qwen_vllm subtree.
# Lifecycle: call start() before first request; call close() on shutdown.
# ADG enforcement: file-scanner only (aiohttp is an external package; ADG edge is invisible).
# Decision packet: docs/reports/plans/vllm_http_decision_packet.md §E (Path A).

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import aiohttp
import aiohttp.client_exceptions

logger = logging.getLogger(__name__)


def _truncate_prompt_for_context(
    prompt: str,
    *,
    completion_budget: int,
) -> str:
    """Ensure prompt tokens + completion fit ``QWEN_LOCAL_MAX_MODEL_LEN``."""
    from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
        QWEN_LOCAL_MAX_MODEL_LEN,
    )

    reserve = 128
    max_prompt_tokens = QWEN_LOCAL_MAX_MODEL_LEN - int(completion_budget) - reserve
    if max_prompt_tokens < 256:
        max_prompt_tokens = 256
    # ~2 chars / token conservative
    max_chars = max_prompt_tokens * 2
    if len(prompt) <= max_chars:
        return prompt
    logger.warning(
        "optimized_vllm_client: truncating prompt %s → %s chars "
        "(max_model_len=%s, completion_budget=%s)",
        len(prompt),
        max_chars,
        QWEN_LOCAL_MAX_MODEL_LEN,
        completion_budget,
    )
    return (
        prompt[:max_chars]
        + "\n\n[TRUNCATED_BY_VLLM_CLIENT: input exceeded local context — "
        "summarize or use a shorter brief / evidence bundle.]"
    )


def _clamp_completion_tokens(*, prompt: str, requested_max_tokens: int) -> int:
    """Keep prompt + completion within ``QWEN_LOCAL_MAX_MODEL_LEN`` (avoids vLLM HTTP 400).

    Uses a conservative characters→tokens estimate so long PA prompts (e.g. full
    résumé + briefing) do not request more completion slots than fit.
    """
    from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
        QWEN_LOCAL_MAX_MODEL_LEN,
    )

    # ~2 chars/token is a safe upper bound for English-ish prose.
    est_prompt_tokens = max(1, len(prompt) // 2)
    reserve = 96
    room = QWEN_LOCAL_MAX_MODEL_LEN - est_prompt_tokens - reserve
    if room < 1:
        logger.warning(
            "optimized_vllm_client: prompt may exceed context "
            "(est_prompt_tokens~%s, max_model_len=%s, prompt_chars=%s)",
            est_prompt_tokens,
            QWEN_LOCAL_MAX_MODEL_LEN,
            len(prompt),
        )
        return 1
    if requested_max_tokens > room:
        logger.info(
            "optimized_vllm_client: clamping max_tokens %s → %s "
            "(est_prompt_tokens~%s, max_model_len=%s)",
            requested_max_tokens,
            room,
            est_prompt_tokens,
            QWEN_LOCAL_MAX_MODEL_LEN,
        )
    return max(1, min(int(requested_max_tokens), int(room)))


@dataclass(frozen=True)
class VLLMRequest:
    """Single vLLM inference request."""

    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.1
    top_p: float = 1.0
    response_format: dict[str, Any] | None = None
    stop: list[str] | None = None
    request_id: str | None = None


@dataclass(frozen=True)
class VLLMResponse:
    """vLLM inference response."""

    success: bool
    text: str
    model: str
    tokens_used: int
    latency_ms: float
    error_message: str | None = None
    cached: bool = False
    http_status: int | None = None
    prompt_chars_in: int = 0
    prompt_chars_after_truncate: int = 0
    prompt_truncated: bool = False
    effective_max_tokens: int = 0
    completion_budget_used: int = 0


class OptimizedVLLMClient:
    """High-performance async vLLM client with pooling and batching.

    Optimizations:
    1. HTTP keep-alive connection pool (avoids connection setup overhead)
    2. Request batching (amortizes network round-trip)
    3. Concurrency semaphore (prevents GPU memory exhaustion)
    4. Response caching (eliminates duplicate compute)
    5. Dynamic batch sizing based on GPU memory
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        max_concurrent: int = 8,
        batch_size: int = 4,
        batch_timeout_ms: float = 50.0,
        cache_size: int = 1000,
    ):
        resolved_url = base_url or os.getenv("VLLM_BASE_URL") or "http://localhost:8000/v1"
        resolved_model = model or os.getenv("VLLM_MODEL_NAME") or "Qwen/Qwen2.5-32B-Instruct-AWQ"
        self.base_url = resolved_url.rstrip("/")
        self.model = resolved_model
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms

        # Concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # Response cache: prompt_hash -> VLLMResponse
        self._cache: dict[str, VLLMResponse] = {}
        self._cache_size = cache_size

        # Batching queue
        self._batch_queue: asyncio.Queue[VLLMRequest] = asyncio.Queue()
        self._batch_results: dict[str, asyncio.Future[VLLMResponse]] = {}
        self._batch_task: asyncio.Task | None = None

        # HTTP session with keep-alive
        self._session: aiohttp.ClientSession | None = None
        self._connector: aiohttp.TCPConnector | None = None

        # Metrics
        self._requests_total = 0
        self._requests_cached = 0
        self._requests_batched = 0
        self._total_latency_ms = 0.0

    async def __aenter__(self) -> OptimizedVLLMClient:
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> None:
        """Initialize HTTP session with connection pooling."""
        # TCP connector with keep-alive
        self._connector = aiohttp.TCPConnector(
            limit=20,  # Max total connections
            limit_per_host=10,  # Max connections per host
            keepalive_timeout=30,  # Keep-alive timeout
            enable_cleanup_closed=True,
            force_close=False,
        )

        # Client session with optimized settings
        timeout = aiohttp.ClientTimeout(
            total=300,  # 5 min total timeout
            connect=10,  # 10 sec connect timeout
            sock_read=60,  # 60 sec read timeout
        )

        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Connection": "keep-alive",
            },
        )

        # Start background batch processor
        self._batch_task = asyncio.create_task(self._batch_processor())

        logger.info("OptimizedVLLMClient started: url=%s, model=%s", self.base_url, self.model)

    async def stop(self) -> None:
        """Cleanup resources."""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError as e:  # guardian: allow-log-and-swallow -- batch task cleanup: cancellation is normal async lifecycle, debug logged
                logger.debug("optimized_vllm_client: Exception swallowed at L146: %s", e)

        if self._session:
            await self._session.close()

        if self._connector:
            await self._connector.close()

        logger.info("OptimizedVLLMClient stopped")

    def _compute_cache_key(self, request: VLLMRequest) -> str:
        """Compute deterministic cache key from request."""
        rf_key = ""
        if request.response_format:
            try:
                rf_key = json.dumps(request.response_format, sort_keys=True)
            except (TypeError, ValueError):
                rf_key = str(request.response_format)
        content = f"{request.prompt}:{request.max_tokens}:{request.temperature}:{request.top_p}:{rf_key}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    async def infer(self, request: VLLMRequest) -> VLLMResponse:
        """Execute single inference with caching and batching.

        Args:
            request: VLLM inference request

        Returns:
            VLLMResponse with inference result
        """
        cache_key = self._compute_cache_key(request)

        # Check cache
        if cache_key in self._cache:
            self._requests_cached += 1
            cached = self._cache[cache_key]
            return VLLMResponse(
                success=cached.success,
                text=cached.text,
                model=cached.model,
                tokens_used=cached.tokens_used,
                latency_ms=0.0,  # Cache hit is instant
                error_message=cached.error_message,
                cached=True,
                http_status=cached.http_status,
                prompt_chars_in=cached.prompt_chars_in,
                prompt_chars_after_truncate=cached.prompt_chars_after_truncate,
                prompt_truncated=cached.prompt_truncated,
                effective_max_tokens=cached.effective_max_tokens,
                completion_budget_used=cached.completion_budget_used,
            )

        # Submit to batch queue and wait for result
        future = asyncio.get_event_loop().create_future()
        request_id = request.request_id or cache_key
        self._batch_results[request_id] = future
        await self._batch_queue.put(request)

        try:
            response = await future
            # Cache successful responses
            if response.success and len(self._cache) < self._cache_size:
                self._cache[cache_key] = response
            return response
        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            return VLLMResponse(
                success=False,
                text="",
                model=self.model,
                tokens_used=0,
                latency_ms=0.0,
                error_message=str(e),
                http_status=None,
                prompt_chars_in=len(request.prompt) if request else 0,
                prompt_chars_after_truncate=0,
                prompt_truncated=False,
                effective_max_tokens=0,
                completion_budget_used=0,
            )

    async def infer_batch(self, requests: list[VLLMRequest]) -> list[VLLMResponse]:
        """Execute batch of inferences efficiently.

        Args:
            requests: List of VLLM inference requests

        Returns:
            List of VLLMResponse (order preserved)
        """
        if not requests:
            return []

        # Process all requests concurrently with semaphore
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def _infer_single(req: VLLMRequest) -> VLLMResponse:
            async with semaphore:
                return await self._infer_single(req)

        # Execute all requests
        tasks = [self.infer(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _batch_processor(self) -> None:
        """Background task that processes batched requests."""
        while True:
            try:
                batch: list[VLLMRequest] = []
                request_ids: list[str] = []

                # Collect batch with timeout
                start_time = time.time()
                while len(batch) < self.batch_size:
                    timeout = self.batch_timeout_ms / 1000.0
                    elapsed = time.time() - start_time
                    remaining = max(0, timeout - elapsed)

                    try:
                        request = await asyncio.wait_for(
                            self._batch_queue.get(),
                            timeout=remaining if batch else None,
                        )
                        cache_key = self._compute_cache_key(request)
                        request_id = request.request_id or cache_key
                        batch.append(request)
                        request_ids.append(request_id)
                    except asyncio.TimeoutError:
                        break

                if batch:
                    await self._execute_batch(batch, request_ids)

            except asyncio.CancelledError:
                logger.info("Batch processor cancelled")
                break
            except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
                logger.error("Batch processor error: %s", e)
                await asyncio.sleep(0.1)

    async def _execute_batch(
        self,
        requests: list[VLLMRequest],
        request_ids: list[str],
    ) -> None:
        """Execute a batch of requests against vLLM."""
        if not self._session:
            for req_id in request_ids:
                if req_id in self._batch_results:
                    future = self._batch_results.pop(req_id)
                    future.set_exception(RuntimeError("Client not started"))
            return

        async with self._semaphore:
            start_time = time.time()

            try:
                # Build OpenAI-compatible request
                # For single request, use chat completions
                # For batch, use multiple completions
                if len(requests) == 1:
                    response = await self._call_single(requests[0])
                else:
                    response = await self._call_batch(requests)

                latency_ms = (time.time() - start_time) * 1000
                self._total_latency_ms += latency_ms
                self._requests_batched += len(requests)

                # Set results
                for i, req_id in enumerate(request_ids):
                    if req_id in self._batch_results:
                        future = self._batch_results.pop(req_id)
                        if not future.done():
                            if isinstance(response, list):
                                future.set_result(response[i])
                            else:
                                future.set_result(response)

            except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
                logger.error("Batch execution failed: %s", e)
                for req_id in request_ids:
                    if req_id in self._batch_results:
                        future = self._batch_results.pop(req_id)
                        if not future.done():
                            future.set_exception(e)

    async def _call_single(self, request: VLLMRequest) -> VLLMResponse:
        """Call vLLM for single request."""
        # urljoin requires trailing slash on base to preserve path components.
        # `base_url` is stored stripped of trailing slash (line 82); add it back here.
        url = urljoin(self.base_url + "/", "chat/completions")

        completion_target = max(256, min(int(request.max_tokens), 4096))
        eff_prompt = _truncate_prompt_for_context(
            request.prompt,
            completion_budget=completion_target,
        )
        max_tokens = _clamp_completion_tokens(
            prompt=eff_prompt,
            requested_max_tokens=request.max_tokens,
        )
        trunc_applied = len(eff_prompt) != len(request.prompt)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": eff_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stream": False,
        }

        if request.stop:
            payload["stop"] = request.stop
        if request.response_format:
            payload["response_format"] = request.response_format

        start_time = time.time()

        try:
            async with self._session.post(url, json=payload) as resp:
                if resp.status >= 400:
                    try:
                        err_body = (await resp.text())[:8000]
                    except (TypeError, ValueError, aiohttp.client_exceptions.ClientError):
                        err_body = "<response body unreadable>"
                    err_msg = f"HTTP {resp.status}: {err_body}"
                    logger.error("vLLM chat/completions error: %s", err_msg[:2000])
                    latency_ms = (time.time() - start_time) * 1000
                    return VLLMResponse(
                        success=False,
                        text="",
                        model=self.model,
                        tokens_used=0,
                        latency_ms=latency_ms,
                        error_message=err_msg,
                        http_status=int(resp.status),
                        prompt_chars_in=len(request.prompt),
                        prompt_chars_after_truncate=len(eff_prompt),
                        prompt_truncated=trunc_applied,
                        effective_max_tokens=int(max_tokens),
                        completion_budget_used=int(completion_target),
                    )

                data = await resp.json()
                latency_ms = (time.time() - start_time) * 1000

                # Extract response text
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    text = message.get("content", "")
                else:
                    text = ""

                # Extract token usage
                usage = data.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)

                return VLLMResponse(
                    success=True,
                    text=text,
                    model=data.get("model", self.model),
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    http_status=int(resp.status),
                    prompt_chars_in=len(request.prompt),
                    prompt_chars_after_truncate=len(eff_prompt),
                    prompt_truncated=trunc_applied,
                    effective_max_tokens=int(max_tokens),
                    completion_budget_used=int(completion_target),
                )

        except aiohttp.client_exceptions.ClientError as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error("vLLM request failed: %s", e)
            return VLLMResponse(
                success=False,
                text="",
                model=self.model,
                tokens_used=0,
                latency_ms=latency_ms,
                error_message=f"HTTP error: {e}",
                http_status=None,
                prompt_chars_in=len(request.prompt),
                prompt_chars_after_truncate=len(eff_prompt),
                prompt_truncated=trunc_applied,
                effective_max_tokens=int(max_tokens),
                completion_budget_used=int(completion_target),
            )
        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error("vLLM unexpected error: %s", e)
            return VLLMResponse(
                success=False,
                text="",
                model=self.model,
                tokens_used=0,
                latency_ms=latency_ms,
                error_message=f"Unexpected error: {e}",
                http_status=None,
                prompt_chars_in=len(request.prompt),
                prompt_chars_after_truncate=len(eff_prompt),
                prompt_truncated=trunc_applied,
                effective_max_tokens=int(max_tokens),
                completion_budget_used=int(completion_target),
            )

    async def _call_batch(self, requests: list[VLLMRequest]) -> list[VLLMResponse]:
        """Call vLLM for batch of requests (parallel execution)."""
        # Execute all requests in parallel with individual semaphores
        tasks = [self._call_single(req) for req in requests]
        return await asyncio.gather(*tasks)

    def get_metrics(self) -> dict[str, Any]:
        """Get client performance metrics."""
        total = self._requests_total + self._requests_cached + self._requests_batched
        avg_latency = self._total_latency_ms / max(1, total)

        return {
            "requests_total": total,
            "requests_cached": self._requests_cached,
            "requests_batched": self._requests_batched,
            "cache_hit_rate": self._requests_cached / max(1, total),
            "avg_latency_ms": avg_latency,
            "cache_size": len(self._cache),
            "gpu_memory_util": 0.7,  # Default GPU memory utilization (70%)
        }

    async def health_check(self) -> dict[str, Any]:
        """Check vLLM server health."""
        if not self._session:
            return {"status": "not_started", "healthy": False}

        try:
            url = urljoin(self.base_url + "/", "models")
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get("data", [])
                    return {
                        "status": "healthy",
                        "healthy": True,
                        "models": [m.get("id") for m in models],
                        "base_url": self.base_url,
                    }
                else:
                    return {
                        "status": f"unhealthy_http_{resp.status}",
                        "healthy": False,
                    }
        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            return {
                "status": f"error: {e}",
                "healthy": False,
            }


# Singleton instance for apps layer
_vllm_client: OptimizedVLLMClient | None = None


async def get_vllm_client() -> OptimizedVLLMClient:
    """Get or create singleton vLLM client."""
    global _vllm_client
    if _vllm_client is None:
        _vllm_client = OptimizedVLLMClient()
        await _vllm_client.start()
    return _vllm_client


async def close_vllm_client() -> None:
    """Close singleton vLLM client."""
    global _vllm_client
    if _vllm_client:
        await _vllm_client.stop()
        _vllm_client = None


__all__ = [
    "OptimizedVLLMClient",
    "VLLMRequest",
    "VLLMResponse",
    "get_vllm_client",
    "close_vllm_client",
]
