"""VCR-style cassette tests for Anthropic + OpenAI judge adapters.

Exercises the full ``judge()`` path — including request building, prompt
templates, HTTP plumbing, and response parsing — using recorded JSON
fixtures (see ``cassettes/``).

The adapters use ``urllib.request.urlopen`` directly. We patch that
single call site with a ``_replay_urlopen`` shim that returns a recorded
body for a recorded status.

Tests cover:
- PASS / FAIL / UNKNOWN verdicts for each provider
- Required-header presence (auth + content-type)
- Non-2xx status surfacing as ``GraderError``
- JSON parse robustness when verdict is wrapped in prose

These tests do NOT contact the network, do NOT require API keys, and run
in <1 second.
"""

from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges.anthropic_judge import (
    AnthropicJudge,
)
from agentic_core.L3_orchestration.exit_eval.judges.openai_judge import (
    OpenAIJudge,
)

CASSETTE_DIR = Path(__file__).parent / "cassettes"


def _load_cassette(name: str) -> dict[str, Any]:
    return json.loads((CASSETTE_DIR / name).read_text(encoding="utf-8"))


def _faithfulness_dim() -> Dimension:
    return Dimension(
        name="faithfulness",
        grader_class=GraderClass.MODEL_BASED,
        threshold=0.6,
        weight=1.0,
        abstain_allowed=True,
    )


def _ctx() -> dict[str, str]:
    return {
        "query": "What is the population of France?",
        "context": "France has approximately 68 million inhabitants.",
        "answer": "About 68 million people live in France.",
    }


def _make_replay_urlopen(cassette: dict[str, Any]):
    """Build a urlopen replacement that returns the cassette body.

    Asserts that required headers are present; mismatched headers fail
    the test loudly so a regression dropping auth surfaces immediately.
    """

    expected = cassette.get("expected_request", {})
    expected_headers = {h.lower() for h in expected.get("headers_required", [])}
    expected_endpoint = cassette["_meta"]["endpoint"]
    status = int(cassette["response_status"])
    body_obj = cassette["response_body"]
    body_bytes = json.dumps(body_obj).encode("utf-8")

    class _FakeResponse:
        def __init__(self, payload: bytes) -> None:
            self._buf = io.BytesIO(payload)

        def read(self) -> bytes:
            return self._buf.read()

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

    def _replay(request, timeout=None):  # noqa: ARG001 — signature must match urlopen
        # urlopen accepts either a string url or a Request object.
        if hasattr(request, "full_url"):
            url = request.full_url
            headers = {k.lower(): v for k, v in (request.headers or {}).items()}
        else:
            url = str(request)
            headers = {}
        assert url == expected_endpoint, (
            f"cassette endpoint mismatch: expected {expected_endpoint!r}, "
            f"got {url!r}"
        )
        missing = expected_headers - set(headers.keys())
        if missing:
            raise AssertionError(f"missing required headers: {sorted(missing)}")
        if status >= 400:
            raise urllib.error.HTTPError(
                url=url,
                code=status,
                msg=str(body_obj.get("error", {}).get("message", "error")),
                hdrs=None,  # type: ignore[arg-type]
                fp=io.BytesIO(body_bytes),
            )
        return _FakeResponse(body_bytes)

    return _replay


# --------------------------------------------------------------------- #
# AnthropicJudge
# --------------------------------------------------------------------- #


class TestAnthropicCassettes:
    def test_pass_verdict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cassette = _load_cassette("anthropic_pass.json")
        monkeypatch.setattr(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _make_replay_urlopen(cassette),
        )
        judge = AnthropicJudge(api_key="test-key")
        response = judge.judge(_faithfulness_dim(), _ctx())
        assert not response.abstain
        assert response.score == pytest.approx(0.95)
        assert "supported" in response.reasoning.lower()

    def test_fail_verdict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cassette = _load_cassette("anthropic_fail.json")
        monkeypatch.setattr(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _make_replay_urlopen(cassette),
        )
        judge = AnthropicJudge(api_key="test-key")
        response = judge.judge(_faithfulness_dim(), _ctx())
        assert not response.abstain
        assert response.score == pytest.approx(0.15)

    def test_unknown_verdict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cassette = _load_cassette("anthropic_unknown.json")
        monkeypatch.setattr(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _make_replay_urlopen(cassette),
        )
        judge = AnthropicJudge(api_key="test-key")
        response = judge.judge(_faithfulness_dim(), _ctx())
        assert response.abstain
        assert response.score == 0.0

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        judge = AnthropicJudge()
        with pytest.raises(GraderError, match="no API key"):
            judge.judge(_faithfulness_dim(), _ctx())


# --------------------------------------------------------------------- #
# OpenAIJudge
# --------------------------------------------------------------------- #


class TestOpenAICassettes:
    def test_pass_verdict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cassette = _load_cassette("openai_pass.json")
        monkeypatch.setattr(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _make_replay_urlopen(cassette),
        )
        judge = OpenAIJudge(api_key="test-key")
        response = judge.judge(_faithfulness_dim(), _ctx())
        assert not response.abstain
        assert response.score == pytest.approx(0.92)

    def test_unknown_verdict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cassette = _load_cassette("openai_unknown.json")
        monkeypatch.setattr(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _make_replay_urlopen(cassette),
        )
        judge = OpenAIJudge(api_key="test-key")
        response = judge.judge(_faithfulness_dim(), _ctx())
        assert response.abstain

    def test_429_surfaces_grader_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cassette = _load_cassette("openai_429.json")
        monkeypatch.setattr(
            "agentic_core.L3_orchestration.exit_eval.judges._base_http_judge.urllib.request.urlopen",
            _make_replay_urlopen(cassette),
        )
        judge = OpenAIJudge(api_key="test-key")
        with pytest.raises(GraderError, match="429"):
            judge.judge(_faithfulness_dim(), _ctx())

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        judge = OpenAIJudge()
        with pytest.raises(GraderError, match="no API key"):
            judge.judge(_faithfulness_dim(), _ctx())


# --------------------------------------------------------------------- #
# Cross-provider invariants
# --------------------------------------------------------------------- #


class TestCassetteInfrastructure:
    def test_all_cassettes_load(self) -> None:
        """Every cassette must be valid JSON with the documented schema."""
        for cassette_path in CASSETTE_DIR.glob("*.json"):
            data = json.loads(cassette_path.read_text(encoding="utf-8"))
            assert "_meta" in data
            assert "endpoint" in data["_meta"]
            assert "response_status" in data
            assert "response_body" in data

    def test_replay_enforces_required_headers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Anthropic cassette requires x-api-key — calling without raises."""
        # Simulate a misconfigured judge that drops the api-key header.
        cassette = _load_cassette("anthropic_pass.json")
        replay = _make_replay_urlopen(cassette)

        class _FakeReq:
            full_url = cassette["_meta"]["endpoint"]
            headers: dict[str, str] = {}  # missing x-api-key

        with pytest.raises(AssertionError, match="missing required headers"):
            replay(_FakeReq())
