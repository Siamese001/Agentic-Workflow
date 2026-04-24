"""Unit tests for QwenJudgeProvider (Wave A of qwen-adoption-waves-a7f3c2).

Verifies the JudgeProvider contract (provider_id, cost_per_eval, judge shape)
without depending on a live vLLM server.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

import pytest

from agentic_core.evaluation.judges.qwen_judge_provider import QwenJudgeProvider


@dataclass
class _FakeResponse:
    success: bool = True
    response: str | None = '{"faithfulness": 4, "relevance": 5, "reasoning": "looks good"}'
    model_used: str = "Qwen/Qwen2.5-14B-Instruct-AWQ"
    latency_ms: float = 50.0
    cached: bool = False
    tokens_used: int = 42
    confidence: float = 0.9
    error_message: str | None = None


def test_provider_id_is_qwen() -> None:
    assert QwenJudgeProvider().provider_id == "qwen"


def test_cost_per_eval_is_zero() -> None:
    assert QwenJudgeProvider().cost_per_eval == 0.0


def test_model_id_resolves_from_ssot() -> None:
    assert "Qwen" in QwenJudgeProvider().model_id


def test_model_override_wins() -> None:
    assert QwenJudgeProvider(model="pinned/qwen-7b").model_id == "pinned/qwen-7b"


def test_clean_strips_markdown_fences() -> None:
    raw = '```json\n{"score": 4}\n```'
    assert QwenJudgeProvider._clean(raw) == '{"score": 4}'


def test_parse_accepts_raw_json() -> None:
    out = QwenJudgeProvider._parse('{"a": 1}')
    assert out == {"a": 1}


def test_parse_accepts_fenced_json() -> None:
    out = QwenJudgeProvider._parse('```json\n{"a": 2}\n```')
    assert out == {"a": 2}


@pytest.mark.asyncio
async def test_judge_happy_path_aggregates_criteria() -> None:
    judge = QwenJudgeProvider()
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(return_value=_FakeResponse())

    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        result = await judge.judge("prompt text", "RUBRIC-001")

    assert result["provider"] == "qwen"
    assert result["rubric_id"] == "RUBRIC-001"
    # Aggregate = (4+5)/2 = 4.5
    assert result["score"] == pytest.approx(4.5)
    assert result["criteria_scores"] == {"faithfulness": 4.0, "relevance": 5.0}
    assert result["reasoning"] == "looks good"
    assert result["model"] == "Qwen/Qwen2.5-14B-Instruct-AWQ"


@pytest.mark.asyncio
async def test_judge_inference_failure_returns_error_shape() -> None:
    judge = QwenJudgeProvider()
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(
        return_value=_FakeResponse(success=False, error_message="connection refused"),
    )

    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        result = await judge.judge("prompt", "R-002")

    assert result["score"] == 0.0
    assert "connection refused" in result["error"]
    assert result["provider"] == "qwen"


@pytest.mark.asyncio
async def test_judge_parse_failure_returns_parse_error_shape() -> None:
    judge = QwenJudgeProvider()
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(
        return_value=_FakeResponse(response="not valid json"),
    )

    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        result = await judge.judge("prompt", "R-003")

    assert result["score"] == 0.0
    assert "Parse error" in result["reasoning"]
    assert result["raw_response"].startswith("not valid json")


def test_judge_sync_wrapper_runs_to_completion() -> None:
    judge = QwenJudgeProvider()
    fake_gateway = AsyncMock()
    fake_gateway.infer = AsyncMock(return_value=_FakeResponse())

    with patch(
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway.get_qwen_inference_gateway",
        new=AsyncMock(return_value=fake_gateway),
    ):
        result = judge.judge_sync("prompt", "R-SYNC")

    assert result["provider"] == "qwen"
    assert result["rubric_id"] == "R-SYNC"
