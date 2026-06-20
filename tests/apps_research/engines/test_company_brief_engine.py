"""Tests for apps_research.engines.company_brief_engine — stub synthesis path."""

from __future__ import annotations

import json
import sys
import types

import pytest

from apps_research.engines.company_brief_engine import CompanyBriefEngine, _v2_enabled


def test_v2_flag_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """V2 retrieval pipeline is opt-in via APPS_RESEARCH_RETRIEVAL_V2 (plan §P1.4)."""
    monkeypatch.delenv("APPS_RESEARCH_RETRIEVAL_V2", raising=False)
    assert _v2_enabled() is False


def test_v2_flag_on_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", "1")
    assert _v2_enabled() is True


def test_v2_path_offline_degrades_gracefully(monkeypatch: pytest.MonkeyPatch) -> None:
    """V2 path with no TAVILY_API_KEY degrades to stub synthesis (plan §P1.4 acceptance).

    Ensures the feature-flag ON case does not regress offline test environments.
    """
    for k in ("TAVILY_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", "1")
    engine = CompanyBriefEngine()
    payload = engine.execute({"topic": "TestCo", "depth": "shallow"})
    assert payload["company"] == "TestCo"


@pytest.fixture
def offline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in (
        "TAVILY_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    ):
        monkeypatch.delenv(k, raising=False)


def test_engine_produces_schema_valid_brief_offline(offline_env: None) -> None:
    engine = CompanyBriefEngine()
    payload = engine.execute({"topic": "TestCo", "depth": "shallow"})
    assert payload["company"] == "TestCo"
    assert payload["overview"]["tagline"].startswith("TestCo")
    assert len(payload["strategic_priorities"]) >= 2
    assert len(payload["language_to_mirror"]) >= 3


def test_engine_rejects_empty_topic(offline_env: None) -> None:
    engine = CompanyBriefEngine()
    with pytest.raises(ValueError):
        engine.execute({"topic": ""})


def test_engine_uses_jd_facets_into_mirror_seed(tmp_path, offline_env: None) -> None:
    jd_path = tmp_path / "jd.json"
    jd_path.write_text(
        json.dumps({"must_have": ["consulting", "agentic", "data"], "keywords": ["AI"]}),
        encoding="utf-8",
    )
    engine = CompanyBriefEngine()
    payload = engine.execute({"topic": "TestCo", "jd_anchor": jd_path, "depth": "shallow"})
    # JD facets should leak into mirror seed via the stub.
    assert any(facet in payload["language_to_mirror"] for facet in ("consulting", "agentic", "data"))


def test_gemini_synthesis_uses_google_ai_max_output_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_AI_MAX_OUTPUT_TOKENS", "777")

    import agentic_core.config.google_ai_env as google_env

    monkeypatch.setattr(
        google_env,
        "google_ai_pro_model_id",
        lambda environ=None, *, default="": ("gemini-3.1-pro-preview", "test"),
    )
    monkeypatch.setattr(
        google_env,
        "google_ai_flash_model_id",
        lambda environ=None, *, default="": ("", ""),
    )

    captured: list[dict[str, object]] = []
    responses = iter(
        [
            types.SimpleNamespace(
                text=json.dumps(
                    {
                        "company_archetype": "consulting",
                        "company_dna": {},
                        "tagline": "TestCo",
                    }
                )
            ),
            types.SimpleNamespace(text="TestCo targeting brief"),
        ]
    )

    class _FakeModels:
        def generate_content(self, *, model, contents, config):
            captured.append({"model": model, "config": dict(config)})
            return next(responses)

    class _FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = _FakeModels()

    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = _FakeClient
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)

    engine = CompanyBriefEngine()
    json_out = engine._gemini_synthesize(
        prompt="prompt", topic="TestCo", jd_facets=["partnerships"]
    )
    plain_out = engine._gemini_synthesize_plain(prompt="prompt")

    assert json_out is not None
    assert json_out["tagline"] == "TestCo"
    assert plain_out == "TestCo targeting brief"
    assert [row["model"] for row in captured] == [
        "gemini-3.1-pro-preview",
        "gemini-3.1-pro-preview",
    ]
    assert all(row["config"]["max_output_tokens"] == 777 for row in captured)
