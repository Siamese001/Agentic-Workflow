"""W1.1: vLLMRequest messages[] cache key and payload shape."""

from __future__ import annotations

from agentic_core.L3_orchestration.inference.qwen_vllm.engines.optimized_vllm_client import (
    VLLMRequest,
)


def test_vllm_request_messages_cache_key_differs_from_flat_prompt() -> None:
    client_messages = __import__(
        "agentic_core.L3_orchestration.inference.qwen_vllm.engines.optimized_vllm_client",
        fromlist=["OptimizedVLLMClient"],
    ).OptimizedVLLMClient(base_url="http://127.0.0.1:8000/v1", model="test-model")
    flat = VLLMRequest(prompt="hello", max_tokens=100)
    threaded = VLLMRequest(
        prompt="",
        max_tokens=100,
        messages=(
            {"role": "system", "content": "SYS"},
            {"role": "user", "content": "U1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "REGEN_DELTA"},
        ),
    )
    assert client_messages._compute_cache_key(flat) != client_messages._compute_cache_key(
        threaded,
    )


def test_local_vllm_provider_accepts_messages_kwarg() -> None:
    from unittest.mock import AsyncMock, MagicMock, patch

    from agentic_core.L2_execution.enforcement._provider_local_vllm import LocalVLLMProvider

    provider = LocalVLLMProvider(model="test-model")
    messages = [
        {"role": "system", "content": "SYS"},
        {"role": "user", "content": "ask"},
        {"role": "assistant", "content": "draft"},
        {"role": "user", "content": "REGEN_DELTA"},
    ]

    mock_response = MagicMock()
    mock_response.success = True
    mock_response.response = "revised"
    mock_response.tokens_used = 10
    mock_response.model_used = "test-model"
    mock_response.cached = False
    mock_response.latency_ms = 1.0
    mock_response.confidence = 0.9

    mock_gateway = MagicMock()
    mock_gateway.infer = AsyncMock(return_value=mock_response)

    async def _fake_get_gateway(*_a: object, **_k: object) -> MagicMock:
        return mock_gateway

    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=_fake_get_gateway,
    ):
        result = provider.generate(
            "",
            "",
            messages=messages,
            max_tokens=512,
        )

    assert result["success"] is True
    assert result["content"] == "revised"
    assert result["messages"] == messages
    call_args = mock_gateway.infer.await_args[0][0]
    assert call_args.messages is not None
    assert len(call_args.messages) == 4
    assert call_args.prompt == ""
