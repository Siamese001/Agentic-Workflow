"""Tests for apps_rg.integrations.company_facet_extractor."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from apps_rg.integrations.company_facet_extractor import (
    DEFAULT_WEIGHTS,
    extract_company_facets,
    score_text_against_company,
)
from apps_rg.types.company_research import (
    CompanyBrief,
    CompanyOverview,
    CustomerProfile,
)


def _brief(**overrides) -> CompanyBrief:
    payload = {
        "company": "Blend360",
        "fetched_at": datetime.now(timezone.utc),
        "source": "user_uploaded",
        "freshness_ttl_days": 30,
        "overview": CompanyOverview(
            tagline="Talent and AI consulting", core_offerings=["consulting", "data engineering"]
        ),
        "strategic_priorities": ["agentic AI", "managed services"],
        "customer_profile": CustomerProfile(
            verticals=["financial services", "healthcare"],
            buyer_titles=["CDO", "CAIO"],
        ),
        "tech_stack_signals": ["AWS", "Snowflake"],
        "cultural_cues": ["partnership", "outcomes"],
        "language_to_mirror": ["consulting", "agentic", "outcomes"],
        "language_to_avoid": ["world-class"],
    }
    payload.update(overrides)
    return CompanyBrief(**payload)


def test_extract_company_facets_populates_all_buckets() -> None:
    facets = extract_company_facets(_brief())
    assert facets.company == "Blend360"
    assert "financial services" in facets.verticals
    assert "CDO" in facets.buyer_archetypes
    assert "AWS" in facets.tech_stack
    assert "consulting" in facets.differentiation
    assert "consulting" in facets.language_to_mirror
    assert facets.alignment_weights == DEFAULT_WEIGHTS


def test_facets_all_terms_dedupes_case_insensitive() -> None:
    facets = extract_company_facets(_brief())
    terms = [t.lower() for t in facets.all_terms()]
    assert len(terms) == len(set(terms))


def test_score_text_against_company_zero_for_empty() -> None:
    facets = extract_company_facets(_brief())
    assert score_text_against_company("", facets) == {
        "co_match": 0.0,
        "lang_score": 0.0,
        "mirror_density": 0.0,
    }


def test_score_text_hits_co_match() -> None:
    facets = extract_company_facets(_brief())
    text = (
        "Drove consulting engagements for financial services CDOs leveraging AWS data."
    )
    scores = score_text_against_company(text, facets)
    assert scores["co_match"] > 0.5
    assert scores["lang_score"] >= 0.33  # at least 'consulting' matches (1/3 with rounding)


def test_score_text_no_hits_returns_zero_co_match() -> None:
    facets = extract_company_facets(_brief())
    scores = score_text_against_company("entirely unrelated text about gardening", facets)
    assert scores["co_match"] == 0.0
    assert scores["lang_score"] == 0.0
