"""Unit tests for LocalVLLMProvider (Wave A of qwen-adoption-waves-a7f3c2).

Tests the async->sync bridge, prompt composition, and error propagation
without depending on a live vLLM server. The QwenInferenceGateway is
patched out; behavior is verified against the contract its consumers rely on.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

import pytest

from agentic_core.L2_execution.enforcement._provider_local_vllm import (
    LocalVLLMProvider,
    _run_async,
)


@dataclass
class _FakeResponse:
    success: bool = True
    response: str | None = "mock qwen answer"
    model_used: str = "Qwen/Qwen2.5-14B-Instruct-AWQ"
    latency_ms: float = 42.0
    cached: bool = False
    tokens_used: int = 17
    confidence: float = 0.88
    error_message: str | None = None


def test_defaults_resolve_from_ssot() -> None:
    provider = LocalVLLMProvider()
    assert "Qwen" in provider._model, "must default to Qwen SSOT model id"


def test_model_override_wins_over_ssot() -> None:
    provider = LocalVLLMProvider(model="custom/model-1")
    assert provider._model == "custom/model-1"


def test_compose_prompt_system_plus_user_includes_role_markers() -> None:
    composed = LocalVLLMProvider._compose_prompt("SYS", "USR")
    assert "SYS" in composed
    assert "USR" in composed
    # Role markers are built from chr() so string equality at any specific
    # literal is brittle; check for the known separators instead.
    assert "system" in composed
    assert "user" in composed
    assert "assistant" in composed


def test_compose_prompt_system_only_returns_user_empty() -> None:
    assert LocalVLLMProvider._compose_prompt("SYS_ONLY", "") == "SYS_ONLY"


def test_compose_prompt_user_only_returns_system_empty() -> None:
    assert LocalVLLMProvider._compose_prompt("", "USER_ONLY") == "USER_ONLY"


def test_get_token_count_uses_4_char_heuristic() -> None:
    provider = LocalVLLMProvider()
    assert provider.get_token_count("") == 0
    assert provider.get_token_count("abcd") == 1
    assert provider.get_token_count("a" * 40) == 10


def test_generate_success_shape() -> None:
    """Happy path: LocalVLLMProvider.generate returns the LLMProvider-shaped dict."""
    provider = LocalVLLMProvider()
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(return_value=_FakeResponse(success=True))

    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        out = provider.generate("SYS", "USR", None, max_tokens=512)

    assert out["success"] is True
    assert out["content"] == "mock qwen answer"
    assert out["model"] == "Qwen/Qwen2.5-14B-Instruct-AWQ"
    assert out["tokens_used"] == 17
    assert out["cached"] is False
    assert out["latency_ms"] == 42.0


def test_generate_failure_raises_runtimeerror() -> None:
    provider = LocalVLLMProvider()
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(
        return_value=_FakeResponse(success=False, error_message="network down"),
    )

    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        with pytest.raises(RuntimeError, match="network down"):
            provider.generate("sys", "usr", None)


def test_run_async_without_running_loop_returns_value() -> None:
    async def _coro() -> int:
        return 42

    assert _run_async(_coro()) == 42


def test_run_async_propagates_exception() -> None:
    async def _coro() -> int:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        _run_async(_coro())
