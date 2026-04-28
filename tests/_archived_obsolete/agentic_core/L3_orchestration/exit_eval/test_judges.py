"""Tests for concrete JudgeProtocol adapters.

HTTP is stubbed via monkeypatch — no real network calls. Covers:

- Prompt composition (delimiter wrap, abstain clause, bypass clause).
- Response parsing: PASS / FAIL / UNKNOWN (abstain) / malformed.
- Timeout → TimeoutError; HTTPError → GraderError.
- Score clamping to scale.
- Provider-specific request shape.
"""

from __future__ import annotations

import json
import socket
import urllib.error
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges import (
    AnthropicJudge,
    HttpJudge,
    OpenAIJudge,
    RUBRIC_PROMPTS,
    build_judge_prompt,
)
from agentic_core.L3_orchestration.exit_eval.judges.prompt_templates import (
    ABSTAIN_CLAUSE,
    AGENT_CONTENT_DELIMITER,
    BYPASS_RESISTANCE_CLAUSE,
)


GROUND_DIM = Dimension(
    name="groundedness",
    grader_class=GraderClass.MODEL_BASED,
    scale=(0.0, 1.0),
    weight=0.4,
    is_hard_gate=False,
    threshold=0.8,
    abstain_allowed=True,
)


# ---------------------------------------------------------------- #
# Prompt-template tests
# ---------------------------------------------------------------- #


class TestPromptTemplates:
    def test_all_rubric_prompts_have_abstain_clause(self) -> None:
        for prompt in RUBRIC_PROMPTS.values():
            assert ABSTAIN_CLAUSE in prompt.system_prompt, f"{prompt.dimension_name} missing abstain clause"

    def test_all_rubric_prompts_have_bypass_clause(self) -> None:
        for prompt in RUBRIC_PROMPTS.values():
            assert BYPASS_RESISTANCE_CLAUSE in prompt.system_prompt

    def test_build_prompt_wraps_agent_content_in_delimiters(self) -> None:
        system, user = build_judge_prompt(
            "groundedness",
            {"agent_output": "X", "reference": "Y", "question": "Q"},
        )
        assert AGENT_CONTENT_DELIMITER in user
        assert "X" in user
        assert "Y" in user

    def test_missing_context_key_renders_empty(self) -> None:
        """Missing key → empty string substitution, no KeyError."""
        _, user = build_judge_prompt("groundedness", {"agent_output": "x"})
        # 'reference' and 'question' missing — user still rendered
        assert isinstance(user, str)

    def test_unknown_dimension_raises(self) -> None:
        with pytest.raises(KeyError):
            build_judge_prompt("nonexistent_dim", {})


# ---------------------------------------------------------------- #
# Shared HTTP stub infrastructure
# ---------------------------------------------------------------- #


class _StubResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_StubResponse":
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _stub_urlopen_returning(body: dict | str):
    if isinstance(body, dict):
        raw = json.dumps(body).encode("utf-8")
    else:
        raw = body.encode("utf-8")

    def _stub(_req, timeout=None):  # noqa: ARG001
        return _StubResponse(raw)

    return _stub


def _anthropic_body(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _openai_body(text: str) -> dict[str, Any]:
    return {"choices": [{"message": {"content": text, "role": "assistant"}}]}


_JSON_PASS = '{"verdict": "PASS", "score": 0.95, "reasoning": "fully grounded"}'
_JSON_FAIL = '{"verdict": "FAIL", "score": 0.2, "reasoning": "hallucinated date"}'
_JSON_UNKNOWN = '{"verdict": "UNKNOWN", "reasoning": "not enough evidence"}'
_JSON_OVERSCALE = '{"verdict": "PASS", "score": 2.5, "reasoning": "ok"}'


# ---------------------------------------------------------------- #
# AnthropicJudge
# ---------------------------------------------------------------- #


class TestAnthropicJudge:
    def test_pass_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_anthropic_body(_JSON_PASS)),
        ):
            judge = AnthropicJudge(timeout=5.0)
            response = judge.judge(
                GROUND_DIM,
                {"agent_output": "Paris is the capital", "reference": "Paris...", "question": "?"},
            )
        assert response.score == pytest.approx(0.95)
        assert not response.abstain

    def test_unknown_abstain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_anthropic_body(_JSON_UNKNOWN)),
        ):
            judge = AnthropicJudge(timeout=5.0)
            response = judge.judge(GROUND_DIM, {"agent_output": "x"})
        assert response.abstain

    def test_missing_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        judge = AnthropicJudge(timeout=5.0)
        with pytest.raises(GraderError, match="no API key"):
            judge.judge(GROUND_DIM, {"agent_output": "x"})

    def test_timeout_mapped_to_TimeoutError(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        def _raises_timeout(_req, timeout=None):  # noqa: ARG001
            raise socket.timeout("slow")

        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _raises_timeout,
        ):
            judge = AnthropicJudge(timeout=1.0)
            with pytest.raises(TimeoutError):
                judge.judge(GROUND_DIM, {"agent_output": "x"})

    def test_http_error_mapped_to_GraderError(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-bad")

        def _raises_http_error(_req, timeout=None):  # noqa: ARG001
            raise urllib.error.HTTPError(
                "url",
                401,
                "Unauthorized",
                {},
                None,  # type: ignore[arg-type]
            )

        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _raises_http_error,
        ):
            judge = AnthropicJudge(timeout=1.0)
            with pytest.raises(GraderError, match="401"):
                judge.judge(GROUND_DIM, {"agent_output": "x"})

    def test_non_json_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning("<html>not json</html>"),
        ):
            judge = AnthropicJudge(timeout=1.0)
            with pytest.raises(GraderError, match="not JSON"):
                judge.judge(GROUND_DIM, {"agent_output": "x"})

    def test_malformed_verdict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        bad = '{"verdict": "maybe", "score": 0.5}'
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_anthropic_body(bad)),
        ):
            judge = AnthropicJudge(timeout=1.0)
            with pytest.raises(GraderError, match="PASS|FAIL|UNKNOWN"):
                judge.judge(GROUND_DIM, {"agent_output": "x"})

    def test_prose_wrapping_tolerated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        wrapped = f"Here is my evaluation:\n\n{_JSON_PASS}\n\nLet me know if you need more."
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_anthropic_body(wrapped)),
        ):
            judge = AnthropicJudge(timeout=1.0)
            response = judge.judge(GROUND_DIM, {"agent_output": "x"})
        assert response.score == pytest.approx(0.95)

    def test_score_clamped_to_scale(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_anthropic_body(_JSON_OVERSCALE)),
        ):
            judge = AnthropicJudge(timeout=1.0)
            response = judge.judge(GROUND_DIM, {"agent_output": "x"})
        assert response.score == 1.0

    def test_request_body_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        captured: dict[str, Any] = {}

        def _capture(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            captured["headers"] = dict(req.headers)
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _StubResponse(json.dumps(_anthropic_body(_JSON_PASS)).encode("utf-8"))

        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _capture,
        ):
            AnthropicJudge(timeout=1.0, model="claude-3-5-sonnet-latest").judge(
                GROUND_DIM, {"agent_output": "x"}
            )

        assert captured["url"].endswith("/v1/messages")
        assert "X-api-key" in captured["headers"] or "x-api-key" in captured["headers"]
        assert captured["body"]["model"] == "claude-3-5-sonnet-latest"
        assert "messages" in captured["body"]
        assert captured["body"]["system"]


# ---------------------------------------------------------------- #
# OpenAIJudge
# ---------------------------------------------------------------- #


class TestOpenAIJudge:
    def test_pass_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-o")
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_openai_body(_JSON_PASS)),
        ):
            judge = OpenAIJudge(timeout=5.0)
            response = judge.judge(GROUND_DIM, {"agent_output": "x"})
        assert response.score == pytest.approx(0.95)

    def test_fail_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-o")
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_openai_body(_JSON_FAIL)),
        ):
            response = OpenAIJudge(timeout=5.0).judge(GROUND_DIM, {"agent_output": "x"})
        assert response.score == pytest.approx(0.2)
        assert not response.abstain

    def test_missing_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(GraderError, match="no API key"):
            OpenAIJudge(timeout=1.0).judge(GROUND_DIM, {"agent_output": "x"})

    def test_request_uses_json_response_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-o")
        captured: dict[str, Any] = {}

        def _capture(req, timeout=None):  # noqa: ARG001
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _StubResponse(json.dumps(_openai_body(_JSON_PASS)).encode("utf-8"))

        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _capture,
        ):
            OpenAIJudge(timeout=1.0).judge(GROUND_DIM, {"agent_output": "x"})

        assert captured["body"]["response_format"]["type"] == "json_object"
        assert captured["body"]["temperature"] == 0.0


# ---------------------------------------------------------------- #
# HttpJudge
# ---------------------------------------------------------------- #


class TestHttpJudge:
    def test_default_extractor_on_openai_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning(_openai_body(_JSON_PASS)),
        ):
            judge = HttpJudge(
                endpoint="http://localhost:8080/v1/chat/completions",
                model="local-llama",
                timeout=5.0,
            )
            response = judge.judge(GROUND_DIM, {"agent_output": "x"})
        assert response.score == pytest.approx(0.95)

    def test_custom_extractor(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _stub_urlopen_returning({"text": _JSON_PASS}),
        ):
            judge = HttpJudge(
                endpoint="http://localhost:8080",
                model="local",
                timeout=5.0,
                extractor=lambda r: r["text"],
            )
            response = judge.judge(GROUND_DIM, {"agent_output": "x"})
        assert response.score == pytest.approx(0.95)

    def test_auth_header_forwarded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict[str, Any] = {}

        def _capture(req, timeout=None):  # noqa: ARG001
            captured["headers"] = dict(req.headers)
            return _StubResponse(json.dumps(_openai_body(_JSON_PASS)).encode("utf-8"))

        with patch(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _capture,
        ):
            judge = HttpJudge(
                endpoint="http://x/y",
                model="m",
                auth_header="Bearer custom-token",
                timeout=1.0,
            )
            judge.judge(GROUND_DIM, {"agent_output": "x"})

        # urllib normalizes header names to Title-Case
        assert captured["headers"].get("Authorization") == "Bearer custom-token"

    def test_invalid_timeout(self) -> None:
        with pytest.raises(ValueError):
            HttpJudge(endpoint="http://x", model="m", timeout=0)


# ---------------------------------------------------------------- #
# Cross-cutting: wrong dimension class → GraderError
# ---------------------------------------------------------------- #


def test_code_based_dim_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    code_dim = Dimension(
        name="policy_match",
        grader_class=GraderClass.CODE_BASED,
        scale=(0.0, 1.0),
        threshold=1.0,
    )
    with pytest.raises(GraderError, match="MODEL_BASED"):
        AnthropicJudge(timeout=1.0).judge(code_dim, {})
