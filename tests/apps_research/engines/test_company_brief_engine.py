"""Tests for apps_research.engines.company_brief_engine — stub synthesis path."""

from __future__ import annotations

import pytest

from apps_research.engines.company_brief_engine import CompanyBriefEngine, _v2_enabled
from apps_rg.types.company_research import CompanyBrief


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
    brief = CompanyBrief.model_validate(payload)
    assert brief.company == "TestCo"


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
    # Round-trip through pydantic to confirm schema-valid stub
    brief = CompanyBrief.model_validate(payload)
    assert brief.company == "TestCo"
    assert len(brief.strategic_priorities) >= 2
    assert len(brief.language_to_mirror) >= 3


def test_engine_rejects_empty_topic(offline_env: None) -> None:
    engine = CompanyBriefEngine()
    with pytest.raises(ValueError):
        engine.execute({"topic": ""})


def test_engine_uses_jd_facets_into_mirror_seed(tmp_path, offline_env: None) -> None:
    import json

    jd_path = tmp_path / "jd.json"
    jd_path.write_text(
        json.dumps({"must_have": ["consulting", "agentic", "data"], "keywords": ["AI"]}),
        encoding="utf-8",
    )
    engine = CompanyBriefEngine()
    payload = engine.execute({"topic": "TestCo", "jd_anchor": jd_path, "depth": "shallow"})
    brief = CompanyBrief.model_validate(payload)
    # JD facets should leak into mirror seed via the stub.
    assert any(facet in brief.language_to_mirror for facet in ("consulting", "agentic", "data"))
