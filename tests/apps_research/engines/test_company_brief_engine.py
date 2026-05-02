"""Tests for apps_research.engines.company_brief_engine — stub synthesis path."""

from __future__ import annotations

import pytest

from apps_research.engines.company_brief_engine import CompanyBriefEngine
from apps_rg.types.company_research import CompanyBrief


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
