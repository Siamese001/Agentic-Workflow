"""Contract: commercial MEDIUM claim output containment harness."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.validate_commercial_medium_claim_output_containment import (
    BLOCKED_FACT_IDS,
    BULLET_NARRATIVE_SECTIONS,
    HEADLINE_EXEC_SECTIONS,
    OUT_JSON,
    build_containment_payload,
)

REPO = Path(__file__).resolve().parents[4]


def test_containment_harness_passes() -> None:
    payload = build_containment_payload()
    assert payload["status"] == "PASS", payload.get("violations")
    assert not payload["blocked_facts_proof"]["in_any_section_pool"]
    for sec in HEADLINE_EXEC_SECTIONS:
        for row in payload["headline_executive_high_only_proof"][sec]:
            assert row["confidence"] == "HIGH"
    for row in payload["overclaim_verdicts"]:
        assert row["overclaim_verdict"] == "PASS"
    assert payload["claim_eligible_medium_by_section"]["unify_bullets"] or payload[
        "claim_eligible_medium_by_section"
    ]["ibm_bullets"]


def test_bullet_sections_only_medium_commercial_when_eligible() -> None:
    payload = build_containment_payload()
    for sec in BULLET_NARRATIVE_SECTIONS:
        for claim in payload["fixture_claims_by_section"][sec]:
            if claim["candidate_fact_id"].startswith("fact_sales") or claim[
                "candidate_fact_id"
            ].startswith("fact_partnerships") or claim["candidate_fact_id"].startswith(
                "fact_revenue"
            ):
                if claim["confidence"] == "MEDIUM":
                    assert claim["claim_eligible_medium"] is True
                    assert claim["verification_status"] == "eligible_medium_with_source_trace"


def test_containment_report_on_disk() -> None:
    assert OUT_JSON.is_file()
    on_disk = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert on_disk["status"] in ("PASS", "PARTIAL", "FAIL")
    assert set(on_disk["blocked_facts_proof"]["blocked_ids"]) >= BLOCKED_FACT_IDS
