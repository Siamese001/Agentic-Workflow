"""Unit tests for executive_summary targeting-only JD/briefing cap."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    compile_executive_summary_evidence_capsule,
)
from apps_rg.runtime.sections.executive_summary_targeting_cap import (
    _CAP_NOTICE,
    apply_executive_summary_targeting_cap,
    compress_targeting_briefing_body,
    compress_targeting_jd_body,
    estimate_targeting_region_tokens,
)
from apps_rg.runtime.sections.executive_summary_token_budget import (
    estimate_tokens_approximate,
    evidence_contract_digest,
    extract_evidence_contract_snapshot,
    protected_fact_ids_from_payload,
)

REPO = Path(__file__).resolve().parents[5]


@pytest.fixture(autouse=True)
def _fec_fixture_dev_bypass() -> None:
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _brown_payload() -> dict:
    jd = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt").read_text(
        encoding="utf-8"
    )
    brief = (
        REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    ).read_text(encoding="utf-8")
    return {
        "product_visible": False,
        "run_id": "targeting_cap_unit",
        "target_title": "Senior Vice President, IT Strategy & Innovation",
        "target_company": "Brown & Brown",
        "jd_text": jd,
        "briefing": brief,
        "allowed_fact_ids": ["fact_governance_003", "fact_certs_001"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_governance_003",
                    "claim_text": "Implemented Basel III / CCAR data lineage frameworks.",
                    "confidence": "HIGH",
                },
                {
                    "fact_id": "fact_certs_001",
                    "claim_text": "Holds AWS and FSA credentials.",
                    "confidence": "HIGH",
                },
            ],
        },
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "graph_skills_proof_pool": True,
            "blocked_facts_count": 1,
            "facts_requiring_human_confirmation_count": 2,
            "unsupported_jd_needs_count": 3,
            "selection_scope": {"selection_id": "sel_brown_cap"},
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "skills_authority_status": "PASS",
            },
        },
    }


def _compiled_with_capsule(payload: dict) -> str:
    compile_executive_summary_evidence_capsule(payload)
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    return compiled.artifact.messages[0]["content"]


def test_targeting_cap_reduces_jd_and_briefing_deterministically():
    jd = "Line A\nLine A\n- Must lead AI strategy\n- Enterprise architecture\n"
    br = "=== STRATEGIC MANDATE ===\n- Theme one\n\n=== MARKET ===\n- Low signal\n"
    c1 = compress_targeting_jd_body(jd, 200)
    c2 = compress_targeting_jd_body(jd, 200)
    assert c1 == c2
    assert "Line A" not in c1 or len(c1) <= len(jd) + len(_CAP_NOTICE)
    assert c1.count("Line A") <= 1
    assert "Must lead AI" in c1 or "Enterprise architecture" in c1
    b1 = compress_targeting_briefing_body(br, 120)
    b2 = compress_targeting_briefing_body(br, 120)
    assert b1 == b2
    assert "STRATEGIC MANDATE" in b1


def test_protected_evidence_unchanged_after_targeting_cap():
    payload = _brown_payload()
    before = _compiled_with_capsule(payload)
    protected = protected_fact_ids_from_payload(payload)
    d0 = evidence_contract_digest(extract_evidence_contract_snapshot(before, protected))
    after, meta = apply_executive_summary_targeting_cap(
        before,
        runtime_payload=payload,
        available_input_tokens=14848,
    )
    d1 = evidence_contract_digest(extract_evidence_contract_snapshot(after, protected))
    assert d0 == d1
    assert meta["targeting_cap_applied"] is True
    for fid in protected:
        assert fid in after
    assert "ALLOWED_SOURCE_FACT_IDS" in after


def test_jd_not_proof_and_no_fabrication_preserved():
    payload = _brown_payload()
    before = _compiled_with_capsule(payload)
    after, _ = apply_executive_summary_targeting_cap(
        before,
        runtime_payload=payload,
        available_input_tokens=14848,
    )
    assert "NOT PROOF" in after or "not proof" in after.lower()
    assert "NO FABRICATION" in after.upper() or "no fabrication" in after.lower()
    assert "jd_used_as_proof=false" in after or "jd_used_as_proof must be false" in after


def test_duplicate_jd_line_removed_before_unique_themes():
    jd = (
        "Senior Vice President, IT Strategy\n"
        "Brown & Brown is seeking a Senior Vice President role.\n"
        "Brown & Brown is seeking a Senior Vice President role.\n"
        "- Lead enterprise architecture and AI innovation.\n"
    )
    capped = compress_targeting_jd_body(jd, 400)
    assert capped.count("Brown & Brown is seeking") <= 1


def test_targeting_region_tokens_drop_on_brown_scale():
    payload = _brown_payload()
    before = _compiled_with_capsule(payload)
    t0 = estimate_targeting_region_tokens(before)
    after, meta = apply_executive_summary_targeting_cap(
        before,
        runtime_payload=payload,
        available_input_tokens=14848,
    )
    t1 = meta["targeting_tokens_after_cap"]
    assert t1 < t0
    assert estimate_tokens_approximate(after) < estimate_tokens_approximate(before)
