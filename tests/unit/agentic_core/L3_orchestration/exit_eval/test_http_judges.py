from __future__ import annotations

import json

import pytest

from agentic_core.L3_orchestration.exit_eval.dimension import Dimension, GraderClass
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges._base_http_judge import (
    BaseHttpJudge,
    _HttpRequest,
)
from agentic_core.L3_orchestration.exit_eval.judges.google_judge import GoogleJudge


class _ParseOnlyJudge(BaseHttpJudge):
    def __init__(self) -> None:
        super().__init__(model="test")

    def _build_request(self, system: str, user: str) -> _HttpRequest:
        return _HttpRequest(url="http://unused", method="POST", headers={}, body=b"{}")

    def _extract_text(self, response_json):
        return ""


def _dimension() -> Dimension:
    return Dimension(
        name="faithfulness",
        grader_class=GraderClass.MODEL_BASED,
        threshold=0.75,
        is_hard_gate=True,
        abstain_allowed=True,
    )


def test_base_http_judge_parses_fenced_json() -> None:
    response = _ParseOnlyJudge()._parse_response(
        _dimension(),
        '```json\n{"verdict":"PASS","score":0.91,"reasoning":"ok"}\n```',
    )

    assert response.score == pytest.approx(0.91)
    assert response.abstain is False
    assert response.reasoning == "ok"


def test_base_http_judge_reports_incomplete_json() -> None:
    with pytest.raises(GraderError, match="incomplete JSON object"):
        _ParseOnlyJudge()._parse_response(
            _dimension(),
            '```json\n{\n  "verdict": "PASS",\n  "score"',
        )


def test_base_http_judge_recovers_truncated_reasoning_after_score() -> None:
    response = _ParseOnlyJudge()._parse_response(
        _dimension(),
        '{\n  "verdict": "PASS",\n  "score": 1.0,\n  "reasoning": "',
    )

    assert response.score == pytest.approx(1.0)
    assert response.abstain is False
    assert response.reasoning == "judge_response_truncated_after_required_fields"


def test_google_judge_request_locks_json_output(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    judge = GoogleJudge(model="gemini-test", max_tokens=1024)

    request = judge._build_request("system", "user")
    body = json.loads(request.body.decode("utf-8"))
    generation_config = body["generationConfig"]

    assert generation_config["maxOutputTokens"] == 1024
    assert generation_config["responseMimeType"] == "application/json"
    assert generation_config["responseSchema"]["required"] == [
        "verdict",
        "score",
        "reasoning",
    ]
    assert generation_config["responseSchema"]["properties"]["verdict"]["enum"] == [
        "PASS",
        "FAIL",
        "UNKNOWN",
    ]
