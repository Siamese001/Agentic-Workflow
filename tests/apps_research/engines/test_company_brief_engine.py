"""apps-test-model: APP CONTRACT.

Tests for apps_research.engines.company_brief_engine fail-closed retrieval.
"""

from __future__ import annotations

import json
import types

import pytest

from apps_research.engines.company_brief_engine import (
    APPS_RESEARCH_BRIEF_MODEL,
    CompanyBriefEngine,
    CompanyBriefUnavailableError,
    _v2_enabled,
)


def test_v2_flag_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """V2 retrieval pipeline is opt-in via APPS_RESEARCH_RETRIEVAL_V2 (plan §P1.4)."""
    monkeypatch.delenv("APPS_RESEARCH_RETRIEVAL_V2", raising=False)
    assert _v2_enabled() is False


def test_v2_flag_on_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", "1")
    assert _v2_enabled() is True


def test_v2_path_offline_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """V2 path with no web provider fails closed without network calls.

    Ensures the feature-flag ON case stays deterministic in offline test environments.
    """
    for k in ("SEARXNG_BASE_URL", "TAVILY_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", "1")
    engine = CompanyBriefEngine()
    with pytest.raises(CompanyBriefUnavailableError, match="v2 research returned no grounded findings"):
        engine.execute({"topic": "TestCo", "depth": "shallow"})


@pytest.fixture
def offline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in (
        "SEARXNG_BASE_URL",
        "TAVILY_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "APPS_RESEARCH_RETRIEVAL_V2",
    ):
        monkeypatch.delenv(k, raising=False)


def test_engine_fails_closed_without_live_research(offline_env: None) -> None:
    engine = CompanyBriefEngine()
    with pytest.raises(CompanyBriefUnavailableError, match="adaptive research returned no grounded findings"):
        engine.execute({"topic": "TestCo", "depth": "shallow"})


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
    with pytest.raises(CompanyBriefUnavailableError, match="adaptive research returned no grounded findings"):
        engine.execute({"topic": "TestCo", "jd_anchor": jd_path, "depth": "shallow"})


def test_c0_bundle_records_retrieval_provenance_and_jd_intent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", "1")
    engine = CompanyBriefEngine()
    jd_context = {
        "job_title": "Security Architect",
        "responsibilities": ["Own platform security, compliance, privacy, and deployment governance"],
    }
    findings = {
        "company_basics": "https://example.com/company\nCompany DNA and operating model",
        "role_context": "https://example.com/role\nRole context",
        "leadership_and_org": "https://example.com/leadership\nLeadership",
        "recent_news_and_signals": "https://example.com/news\nRecent news",
        "competitive_landscape": "https://example.com/market\nMarket",
        "regulatory_and_legal": "https://example.com/trust\nSecurity compliance privacy risk governance",
        "tech_stack_and_tools": "https://example.com/platform\nPlatform architecture",
    }

    bundle = engine._build_c0_bundle(
        topic="Acme",
        depth_profile="COMPANY_BRIEF_STANDARD",
        profile_cfg={},
        findings=findings,
        synthesis={},
        jd_context=jd_context,
    )

    assert bundle["retrieval_config"]["retrieval_v2_enabled"] is True
    assert "regulatory_and_legal" in bundle["retrieval_config"]["query_families"]
    assert "security_trust" in bundle["jd_retrieval_contract"]["intent_ids"]
    assert "regulatory_and_legal" in bundle["jd_retrieval_contract"]["required_evidence_families"]
    assert "regulatory_and_legal" in bundle["synthesis_guidance"]["ordered_sections"]


def test_openai_synthesis_uses_pinned_model_and_output_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RESEARCH_BRIEF_MODEL", "gpt-5.5")
    monkeypatch.setenv("APPS_RESEARCH_MAX_OUTPUT_TOKENS", "777")

    captured: list[dict[str, object]] = []
    responses = iter(
        [
            types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(
                            content=json.dumps(
                                {
                                    "company_archetype": "consulting",
                                    "company_dna": {},
                                    "tagline": "TestCo",
                                }
                            )
                        )
                    )
                ]
            ),
            types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(content="TestCo targeting brief")
                    )
                ]
            ),
        ]
    )

    class _FakeChatCompletions:
        def create(self, *, model, messages, temperature, max_completion_tokens):
            captured.append(
                {
                    "model": model,
                    "temperature": temperature,
                    "max_completion_tokens": max_completion_tokens,
                    "messages": tuple(messages),
                }
            )
            return next(responses)

    class _FakeClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=_FakeChatCompletions()
            )

    monkeypatch.setattr(
        "apps_research.engines.company_brief_engine.create_openai_sync_client",
        lambda: _FakeClient(),
    )

    engine = CompanyBriefEngine()
    json_out = engine._gemini_synthesize(
        prompt="prompt", topic="TestCo", jd_facets=["partnerships"]
    )
    plain_out = engine._gemini_synthesize_plain(prompt="prompt")

    assert json_out is not None
    assert json_out["tagline"] == "TestCo"
    assert plain_out == "TestCo targeting brief"
    assert [row["model"] for row in captured] == [
        APPS_RESEARCH_BRIEF_MODEL,
        APPS_RESEARCH_BRIEF_MODEL,
    ]
    assert all(row["max_completion_tokens"] == 777 for row in captured)
    assert APPS_RESEARCH_BRIEF_MODEL == "gpt-5.4-mini"
