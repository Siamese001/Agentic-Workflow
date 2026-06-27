"""Regression tests for apps_research retrieval-quality provenance."""

from __future__ import annotations

from apps_research.engines.query_decomposer import (
    decompose,
    decompose_coverage_families,
    describe_jd_retrieval_contract,
)
from apps_research.integrations.search_retrieval import retrieval_config_snapshot


def test_v2_decompose_standard_stays_neutral_without_jd_context() -> None:
    queries = decompose("Acme Health", depth="standard")
    joined = " ".join(q.text.lower() for q in queries)

    assert len(queries) == 4
    assert "co-sell" not in joined
    assert "gsi" not in joined
    assert "isv" not in joined
    assert "valuation" not in joined


def test_partnership_jd_promotes_explicit_partner_retrieval_families() -> None:
    plans = decompose_coverage_families(
        "Anthropic",
        "COMPANY_BRIEF_STANDARD",
        {
            "company_name": "Anthropic",
            "job_title": "Manager of Applied AI Architecture, Partnerships",
            "responsibilities": [
                "Drive co-sell solution design with GSI, ISV, and cloud partners",
                "Lead partner enablement and technical close for enterprise adoption",
            ],
        },
    )
    first_six = [p.family for p in plans[:6]]

    assert first_six == [
        "company_basics",
        "partner_ecosystem",
        "commercial_motion",
        "adoption_motion",
        "tech_stack_and_tools",
        "recent_news_and_signals",
    ]
    assert all(
        p.jd_boosted
        for p in plans
        if p.family in {
            "partner_ecosystem",
            "commercial_motion",
            "adoption_motion",
            "tech_stack_and_tools",
        }
    )


def test_platform_jd_promotes_platform_relevant_families_without_partner_bias() -> None:
    plans = decompose_coverage_families(
        "Acme",
        "COMPANY_BRIEF_STANDARD",
        {
            "job_title": "Director of Data Platform",
            "responsibilities": ["Own platform architecture and infrastructure reliability"],
        },
    )
    first_six = [p.family for p in plans[:6]]
    families = [p.family for p in plans]

    assert "tech_stack_and_tools" in first_six
    assert "adoption_motion" in first_six
    assert "partner_ecosystem" not in first_six
    assert "commercial_motion" not in families


def test_ambiguous_partner_word_does_not_force_partnership_retrieval() -> None:
    for jd in (
        {"job_title": "People Partner", "responsibilities": ["Partner with managers on employee relations"]},
        {"job_title": "Security Architect", "responsibilities": ["Partner with engineering to improve security posture"]},
    ):
        plans = decompose_coverage_families("Acme", "COMPANY_BRIEF_STANDARD", jd)
        first_six = [p.family for p in plans[:6]]
        contract = describe_jd_retrieval_contract(jd)

        assert "partnerships" not in contract["intent_ids"]
        assert "partner_ecosystem" not in first_six
        assert "commercial_motion" not in first_six


def test_jd_retrieval_contract_records_general_intents() -> None:
    contract = describe_jd_retrieval_contract(
        {
            "job_title": "Security Architect",
            "responsibilities": ["Own platform security, compliance, privacy, and deployment governance"],
        }
    )

    assert "security_trust" in contract["intent_ids"]
    assert "platform_engineering" in contract["intent_ids"]
    assert "regulatory_and_legal" in contract["required_evidence_families"]
    assert "tech_stack_and_tools" in contract["required_evidence_families"]


def test_retrieval_config_snapshot_records_material_routing_inputs(monkeypatch) -> None:
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080/internal/path")
    monkeypatch.setenv("SEARXNG_TIMEOUT_SECONDS", "7")
    monkeypatch.setenv("SEARXNG_CATEGORIES", "general,news")
    monkeypatch.setenv("SEARXNG_ENGINES", "google,bing")
    monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", "1")

    snapshot = retrieval_config_snapshot(query_families=["company_basics", "partner_ecosystem"])

    assert snapshot["schema_version"] == "apps_research.retrieval_config_snapshot/v1"
    assert snapshot["provider"] == "searxng"
    assert snapshot["base_url_configured"] is True
    assert snapshot["base_url_origin"] == "http://localhost:8080"
    assert snapshot["timeout_seconds"] == 7.0
    assert snapshot["categories"] == "general,news"
    assert snapshot["engines"] == "google,bing"
    assert snapshot["retrieval_v2_enabled"] is True
    assert snapshot["experimental_retrieval_v2"] is True
    assert snapshot["query_families"] == ["company_basics", "partner_ecosystem"]
