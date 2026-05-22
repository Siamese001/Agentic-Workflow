"""Bounded X1D judge retries and OpenAI empty-content (reasoning budget) handling."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from apps_rg.runtime.judges.executive_summary_x1d import (
    JudgeOutput,
    _call_openai,
    _extract_json_from_text,
    _invoke_judge_with_bounded_retries,
    _is_retriable_judge_output,
    _resolved_openai_judge_max_completion_tokens,
    _x1d_judge_max_attempts,
)


def test_openai_completion_token_budget_escalates_on_retry() -> None:
    assert _resolved_openai_judge_max_completion_tokens(attempt=1) >= 4096
    assert _resolved_openai_judge_max_completion_tokens(attempt=2) >= _resolved_openai_judge_max_completion_tokens(
        attempt=1
    )


def test_is_retriable_parse_error() -> None:
    out = JudgeOutput(
        judge_id="x1d_openai_chatgpt_headline",
        provider_name="OpenAI",
        provider_key="openai_chatgpt",
        evaluator_mode="BLOCKED_RESPONSE_PARSE_ERROR",
        provider_status="BLOCKED_RESPONSE_PARSE_ERROR",
        model_name="gpt-5.5",
        provider_available=False,
        provider_blocked=True,
        exact_provider_error="Failed to extract JSON from openai_chatgpt response",
    )
    assert _is_retriable_judge_output(out) is True


def test_bounded_retries_stop_after_success() -> None:
    calls: list[int] = []

    def invoke(attempt: int) -> JudgeOutput:
        calls.append(attempt)
        if attempt < 2:
            return JudgeOutput(
                judge_id="x1d_openai",
                provider_name="OpenAI",
                provider_key="openai_chatgpt",
                evaluator_mode="BLOCKED_RESPONSE_PARSE_ERROR",
                provider_status="BLOCKED_RESPONSE_PARSE_ERROR",
                model_name="gpt-5.5",
                provider_available=False,
                provider_blocked=True,
                exact_provider_error="Failed to extract JSON from openai_chatgpt response",
            )
        return JudgeOutput(
            judge_id="x1d_openai",
            provider_name="OpenAI",
            provider_key="openai_chatgpt",
            evaluator_mode="MODEL_BACKED",
            provider_status="MODEL_BACKED_PASS",
            model_name="gpt-5.5",
            provider_available=True,
            provider_blocked=False,
            exact_provider_error=None,
            pass_=True,
        )

    with (
        patch.dict("os.environ", {"APPS_RG_X1D_JUDGE_MAX_ATTEMPTS": "3"}),
        patch("apps_rg.runtime.judges.executive_summary_x1d.time.sleep"),
    ):
        out = _invoke_judge_with_bounded_retries(invoke, provider_key="openai_chatgpt")
    assert out.pass_ is True
    assert calls == [1, 2]


def test_extract_json_from_markdown_fence() -> None:
    text = '```json\n{"score_scale":"0_to_5","score":4.0,"threshold":4.0,"pass":true,"decisive_failure":false,"findings":[],"cited_sentence_indexes":[],"remediation_suggestions":[]}\n```'
    parsed = _extract_json_from_text(text)
    assert parsed is not None
    assert parsed.get("score_scale") == "0_to_5"


@patch("apps_rg.runtime.judges.executive_summary_x1d._judge_live_https_allowed_under_pytest", return_value=True)
@patch("apps_rg.runtime.judges.executive_summary_x1d.urllib.request.urlopen")
def test_openai_empty_length_finish_reason_is_retriable_message(
    mock_urlopen: MagicMock,
    _pytest_net: MagicMock,
) -> None:
    empty_completion = {
        "choices": [
            {
                "message": {"role": "assistant", "content": ""},
                "finish_reason": "length",
            }
        ],
        "usage": {"completion_tokens": 900, "completion_tokens_details": {"reasoning_tokens": 900}},
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(empty_completion).encode()
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    out = _call_openai(
        "sk-test",
        "grade this headline",
        "gpt-5.5",
        "abc123",
        "openai_chatgpt",
        artifact_base=None,
        attempt=1,
    )
    assert out.provider_status == "BLOCKED_RESPONSE_PARSE_ERROR"
    assert _is_retriable_judge_output(out)
    assert "finish_reason=length" in (out.exact_provider_error or "").lower()


@patch("apps_rg.runtime.judges.executive_summary_x1d._judge_live_https_allowed_under_pytest", return_value=True)
@patch("apps_rg.runtime.judges.executive_summary_x1d.urllib.request.urlopen")
def test_openai_retry_escalates_max_completion_tokens(
    mock_urlopen: MagicMock,
    _pytest_net: MagicMock,
) -> None:
    good = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "score_scale": "0_to_5",
                            "score": 4.5,
                            "threshold": 4.0,
                            "pass": True,
                            "decisive_failure": False,
                            "findings": ["ok"],
                            "cited_sentence_indexes": [1],
                            "remediation_suggestions": [],
                        }
                    ),
                },
                "finish_reason": "stop",
            }
        ]
    }
    empty = {
        "choices": [
            {"message": {"role": "assistant", "content": ""}, "finish_reason": "length"}
        ]
    }
    payloads: list[int] = []

    def side_effect(req: object, timeout: float = 60) -> MagicMock:
        body = json.loads(getattr(req, "data", b"{}"))
        if body.get("max_completion_tokens"):
            payloads.append(int(body["max_completion_tokens"]))
        elif body.get("max_tokens"):
            payloads.append(int(body["max_tokens"]))
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            empty if len(payloads) == 1 else good
        ).encode()
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    mock_urlopen.side_effect = side_effect

    with (
        patch.dict("os.environ", {"APPS_RG_X1D_JUDGE_MAX_ATTEMPTS": "2"}),
        patch("apps_rg.runtime.judges.executive_summary_x1d.time.sleep"),
    ):
        out = _invoke_judge_with_bounded_retries(
            lambda attempt: _call_openai(
                "sk-test",
                "grade",
                "gpt-5.5",
                "hash1",
                "openai_chatgpt",
                attempt=attempt,
            ),
            provider_key="openai_chatgpt",
        )
    assert out.evaluator_mode == "MODEL_BACKED"
    assert len(payloads) == 2
    assert payloads[1] >= payloads[0]
