"""Unit tests for apps_rg targeting brief extraction in governed research runs."""

from __future__ import annotations

from apps_research.integrations.governed_research_run import _company_brief_text_from_fec


def test_company_brief_text_prefers_company_brief_text_when_multiple_keys() -> None:
    """Key walk order is fixed; both fields are usually identical after CompanyBriefEngine assembly."""
    fec = {
        "company_brief": {
            "company_brief_text": "legacy json brief",
            "apps_rg_targeting_brief_markdown": "=== STRATEGIC MANDATE ===\nRun-specific targeting.",
        }
    }
    assert _company_brief_text_from_fec(fec) == "legacy json brief"


def test_company_brief_text_uses_targeting_markdown_when_primary_key_absent() -> None:
    fec = {
        "company_brief": {
            "apps_rg_targeting_brief_markdown": "=== STRATEGIC MANDATE ===\nRun-specific targeting.",
        }
    }
    assert _company_brief_text_from_fec(fec) == "=== STRATEGIC MANDATE ===\nRun-specific targeting."


def test_company_brief_text_falls_back_to_apps_rg_targeting_text_key() -> None:
    fec = {
        "company_brief": {
            "apps_rg_targeting_brief_text": "Targeting body from text key.",
        }
    }
    assert _company_brief_text_from_fec(fec) == "Targeting body from text key."


def test_company_brief_text_uses_company_brief_text_when_no_targeting_keys() -> None:
    fec = {"company_brief": {"company_brief_text": "Standard company brief prose."}}
    assert _company_brief_text_from_fec(fec) == "Standard company brief prose."


def test_company_brief_text_empty_when_missing_or_whitespace() -> None:
    assert _company_brief_text_from_fec({}) == ""
    assert _company_brief_text_from_fec({"company_brief": {}}) == ""
    assert _company_brief_text_from_fec({"company_brief": {"apps_rg_targeting_brief_text": "   "}}) == ""


def test_company_brief_text_ignores_non_dict_company_brief() -> None:
    assert _company_brief_text_from_fec({"company_brief": "not a dict"}) == ""
