"""Unit tests for qwen_pass_factories (Wave C of qwen-adoption-waves-a7f3c2)."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

import pytest

from agentic_core.L0_routing.config.model_registry import QWEN_LOCAL_MODEL_ID
from agentic_core.knowledge.retrieval.qwen_pass_factories import (
    build_qwen_pass1_fn,
    build_qwen_pass2_fn,
)


@dataclass
class _FakeResponse:
    success: bool = True
    response: str | None = '{"result": "ok"}'
    model_used: str = QWEN_LOCAL_MODEL_ID
    latency_ms: float = 30.0
    cached: bool = False
    tokens_used: int = 20
    confidence: float = 0.9
    error_message: str | None = None


def test_build_qwen_pass2_fn_returns_callable() -> None:
    p2 = build_qwen_pass2_fn()
    assert callable(p2)


def test_build_qwen_pass1_fn_returns_callable() -> None:
    p1 = build_qwen_pass1_fn()
    assert callable(p1)


def test_pass2_returns_response_text_on_success() -> None:
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(return_value=_FakeResponse(response="clean json text"))

    p2 = build_qwen_pass2_fn()
    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        out = p2("reshape this answer")
    assert out == "clean json text"


def test_pass2_returns_empty_on_failure() -> None:
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(
        return_value=_FakeResponse(success=False, response=None, error_message="oom"),
    )
    p2 = build_qwen_pass2_fn()
    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        out = p2("reshape")
    assert out == ""


def test_pass1_returns_anthropic_shaped_dict() -> None:
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(
        return_value=_FakeResponse(response="a grounded answer"),
    )
    p1 = build_qwen_pass1_fn()
    payload = {
        "system": "you are a helpful assistant",
        "messages": [{"role": "user", "content": "what is the revenue?"}],
    }
    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        out = p1(payload)

    assert out["stop_reason"] == "end_turn"
    assert out["model"] == QWEN_LOCAL_MODEL_ID
    assert out["content"][0]["type"] == "text"
    assert out["content"][0]["text"] == "a grounded answer"
    # Qwen pass 1 never emits citations — always empty list per factory contract.
    assert out["content"][0]["citations"] == []


def test_pass1_flattens_list_content_blocks() -> None:
    """Anthropic-style messages may carry content as a list of blocks; Qwen
    sees a single flattened prompt string."""
    fake_gateway = AsyncMock()
    captured: dict[str, object] = {}

    async def _capture_infer(req):
        captured["prompt"] = req.prompt
        return _FakeResponse(response="ok")

    fake_gateway.infer = _capture_infer
    p1 = build_qwen_pass1_fn()
    payload = {
        "system": [{"type": "text", "text": "sys instructions"}],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "first block"},
                    {"type": "text", "text": "second block"},
                ],
            },
        ],
    }
    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        out = p1(payload)

    assert "sys instructions" in captured["prompt"]
    assert "first block" in captured["prompt"]
    assert "second block" in captured["prompt"]
    assert out["stop_reason"] == "end_turn"


def test_pass1_returns_error_shape_on_failure() -> None:
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(
        return_value=_FakeResponse(success=False, response=None, error_message="timeout"),
    )
    p1 = build_qwen_pass1_fn()
    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        out = p1({"system": "", "messages": []})

    assert out["stop_reason"] == "error"
    assert out["content"][0]["text"] == ""
    assert out["content"][0]["citations"] == []
