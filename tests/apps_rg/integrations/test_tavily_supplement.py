"""Tests for apps_rg.integrations.tavily_supplement (offline / fail-soft paths)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from apps_rg.integrations.tavily_supplement import supplement_company_brief
from apps_rg.types.company_research import CompanyBrief, CompanyOverview


def _stub_brief() -> CompanyBrief:
    return CompanyBrief(
        company="TestCo",
        fetched_at=datetime.now(timezone.utc),
        source="user_uploaded",
        freshness_ttl_days=30,
        overview=CompanyOverview(tagline="(stub synthesis — research unavailable)", core_offerings=[]),
        strategic_priorities=["a", "b"],
        language_to_mirror=["one", "two", "three"],
    )


def test_supplement_returns_brief_unchanged_when_no_tavily() -> None:
    """No TAVILY_API_KEY env -> Tavily client init fails -> brief unchanged."""
    brief = _stub_brief()
    result = supplement_company_brief(brief)
    # Returns the same instance (or a fail-soft copy with same content).
    assert result.company == "TestCo"
    assert result.overview.tagline == brief.overview.tagline


def test_supplement_never_raises_on_failure() -> None:
    """The supplement adapter must be fail-soft per locked decision D3."""
    brief = _stub_brief()
    # Should not raise even if everything is missing.
    result = supplement_company_brief(brief)
    assert result is not None
