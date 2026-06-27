"""Regression tests for apps_research retrieval-quality provenance."""

from __future__ import annotations

from apps_research.engines.query_decomposer import decompose, decompose_coverage_families
from apps_research.integrations.search_retrieval import retrieval_config_snapshot


def test_v2_decompose_standard_includes_partner_and_freshness_terms() -> None:
    queries = decompose("Anthropic", depth="standard")
    joined = " ".join(q.text.lower() for q in queries)

    assert len(queries) == 4
    assert "partner ecosystem" in joined or "partnerships" in joined
    assert "co-sell" in joined
    assert "valuation" in joined
    assert "funding" in joined


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

    assert "role_context" not in first_six
    assert first_six == [
        "company_basics",
        "financials_and_growth",
        "partner_ecosystem",
        "commercial_motion",
        "adoption_motion",
        "recent_news_and_signals",
    ]
    assert all(
        p.jd_boosted
        for p in plans
        if p.family in {
            "financials_and_growth",
            "partner_ecosystem",
            "commercial_motion",
            "adoption_motion",
            "recent_news_and_signals",
        }
    )


def test_non_partnership_jd_preserves_standard_role_context_boost() -> None:
    plans = decompose_coverage_families(
        "Acme",
        "COMPANY_BRIEF_STANDARD",
        {"job_title": "Director of Data Platform", "responsibilities": ["Own data platform"]},
    )
    families = [p.family for p in plans]

    assert "role_context" in families
    assert "partner_ecosystem" not in families
    assert "commercial_motion" not in families
    assert "adoption_motion" not in families


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
