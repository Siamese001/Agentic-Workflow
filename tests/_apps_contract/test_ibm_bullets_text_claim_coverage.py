"""Structural text_claim_coverage integrity for ibm_bullets (deterministic proof only)."""

from __future__ import annotations

from apps_rg.runtime.sections.ibm_bullets_lane import build_mock_output
from apps_rg.runtime.validators.ibm_bullets_x2 import (
    IBM_BULLET_IDS,
    TEXT_COVERAGE_INTEGRITY_GATE_ID,
    build_ibm_bullets_text_claim_coverage,
    check_ibm_bullets_text_claim_coverage_integrity,
)


def _payload_bundle():
    from apps_rg.runtime.sections.ibm_bullets_lane import (
        build_runtime_payload,
        build_selected_fact_plan,
        extract_ibm_employment,
        load_base_resume,
    )

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_ibm_employment(base)
    plan = build_selected_fact_plan(facts)
    rp = build_runtime_payload(
        base_json_path=path,
        base_hash=base_hash,
        ibm_header=header,
        selected_fact_plan=plan,
        allowed_fact_ids=allowed,
        target_title="SVP",
        target_company="Corp",
        jd_text="regulated financial services synthetic role description.",
        briefing="cloud modernization",
    )
    parsed = build_mock_output(rp)
    return parsed, allowed


def test_build_ibm_bullets_coverage_one_row_per_bullet():
    parsed, allowed = _payload_bundle()
    bullets = list(parsed["bullets"])
    ledger = list(parsed["claim_ledger"])
    cov = build_ibm_bullets_text_claim_coverage(bullets, ledger, allowed)
    assert cov["coverage_schema"] == "ibm_bullets_structural_v1"
    assert cov["overall_pass"] is True
    assert len(cov["sentences"]) == 5
    for bid in IBM_BULLET_IDS:
        assert any(r["bullet_id"] == bid for r in cov["sentences"])


def test_ibm_coverage_integrity_gate_detects_tamper():
    parsed, allowed = _payload_bundle()
    bullets = list(parsed["bullets"])
    ledger = list(parsed["claim_ledger"])
    good = build_ibm_bullets_text_claim_coverage(bullets, ledger, allowed)
    tampered = dict(good)
    tampered["sentences"] = list(good["sentences"])
    row0 = dict(tampered["sentences"][0])
    mc = list(row0["material_claims"])
    mc[0] = dict(mc[0])
    mc[0]["claim_text"] = bullets[-1]["bullet_text"]
    row0["material_claims"] = mc
    tampered["sentences"][0] = row0

    ok, reason = check_ibm_bullets_text_claim_coverage_integrity(bullets, ledger, tampered, allowed)
    assert ok is False
    assert reason and "mismatch" in reason


def test_integrity_gate_id_matches_unify_contract():
    assert TEXT_COVERAGE_INTEGRITY_GATE_ID == "x2_text_claim_coverage_integrity"
