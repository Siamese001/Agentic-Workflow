"""Contract tests for targeting brief markdown extraction in governed_research_run.

Placed under tests/_apps_contract/ because tests/unit/apps_research/integrations/
shadows apps_research.integrations under pytest --import-mode=importlib.
"""

from __future__ import annotations

import pytest

from apps_research.integrations.governed_research_run import (
    GovernedE2ERunRecord,
    _company_brief_text_from_fec,
)


@pytest.mark.parametrize(
    ("fec_ctx", "expected"),
    [
        ({}, ""),
        ({"company_brief": "not-a-dict"}, ""),
        ({"company_brief": {}}, ""),
        (
            {"company_brief": {"company_brief_text": "  Primary brief markdown  "}},
            "Primary brief markdown",
        ),
        (
            {
                "company_brief": {
                    "apps_rg_targeting_brief_text": "Targeting brief v1 body",
                }
            },
            "Targeting brief v1 body",
        ),
        (
            {
                "company_brief": {
                    "apps_rg_targeting_brief_markdown": "# AIG VP Agentic AI\n\nMandate text",
                }
            },
            "# AIG VP Agentic AI\n\nMandate text",
        ),
    ],
)
def test_company_brief_text_from_fec_extracts_known_keys(
    fec_ctx: dict,
    expected: str,
) -> None:
    assert _company_brief_text_from_fec(fec_ctx) == expected


def test_company_brief_text_from_fec_prefers_first_non_empty_key() -> None:
    fec_ctx = {
        "company_brief": {
            "company_brief_text": "first wins",
            "apps_rg_targeting_brief_text": "second ignored",
            "apps_rg_targeting_brief_markdown": "third ignored",
        }
    }
    assert _company_brief_text_from_fec(fec_ctx) == "first wins"


def test_company_brief_text_from_fec_skips_blank_values_for_fallback_key() -> None:
    fec_ctx = {
        "company_brief": {
            "company_brief_text": "   ",
            "apps_rg_targeting_brief_text": "fallback brief",
        }
    }
    assert _company_brief_text_from_fec(fec_ctx) == "fallback brief"


def test_governed_e2e_run_record_accepts_company_brief_text_field() -> None:
    record = GovernedE2ERunRecord(
        run_id="run-001",
        topic="AIG company briefing",
        l1_sub_queries=("AIG agentic AI",),
        l1_fallback=False,
        l0_intent="research",
        l0_target="research_assembly",
        l0_confidence=0.9,
        l0_fallback=False,
        c0_raw_count=0,
        c0_shaped_count=0,
        c0_collection="",
        disposition="proceed",
        gate_disposition="allow_response",
        grounded=False,
        citation_count=0,
        support_coverage=0.0,
        l6_ingested=False,
        error="",
        company_brief_text="Delegated targeting brief markdown",
    )
    assert record.company_brief_text == "Delegated targeting brief markdown"
