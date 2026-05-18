"""Structural text_claim_coverage integrity for unify_bullets (deterministic proof only)."""

from __future__ import annotations

from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output
from apps_rg.runtime.validators.executive_summary_x2 import build_sentence_claim_coverage
from apps_rg.runtime.validators.unify_bullets_x2 import (
    TEXT_COVERAGE_INTEGRITY_GATE_ID,
    UNIFY_BULLET_IDS,
    build_unify_bullets_text_claim_coverage,
    check_unify_bullets_text_claim_coverage_integrity,
)


def _payload_bundle():
    from apps_rg.runtime.sections.unify_bullets_lane import (
        build_runtime_payload,
        build_selected_fact_plan,
        extract_unify_employment,
        load_base_resume,
    )

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_unify_employment(base)
    plan = build_selected_fact_plan(facts)
    rp = build_runtime_payload(
        base_json_path=path,
        base_hash=base_hash,
        unify_header=header,
        selected_fact_plan=plan,
        allowed_fact_ids=allowed,
        target_title="SVP",
        target_company="Corp",
        jd_text="AI governance synthetic role description.",
        briefing="regulated",
    )
    parsed = build_mock_output(rp)
    return parsed, allowed


def test_build_unify_bullets_coverage_one_row_per_bullet_with_matching_ledger_rows():
    parsed, allowed = _payload_bundle()
    bullets = list(parsed["bullets"])
    ledger = list(parsed["claim_ledger"])
    cov = build_unify_bullets_text_claim_coverage(bullets, ledger, allowed)
    assert cov["coverage_schema"] == "unify_bullets_structural_v1"
    assert cov["overall_pass"] is True
    rows = cov["sentences"]
    assert len(rows) == 6
    by_id = {b["bullet_id"]: b for b in bullets}
    for row in rows:
        bid = row["bullet_id"]
        assert bid in UNIFY_BULLET_IDS
        assert row["sentence_text"].startswith(f"- {bid}:")
        mc = row["material_claims"]
        assert len(mc) == 1
        assert mc[0]["support_status"] == "SUPPORTED"
        assert mc[0]["claim_text"] == by_id[bid]["bullet_text"]
        ledger_row = next(
            x
            for x in ledger
            if any(str(i).split("_metric_")[0] == bid for i in (x.get("source_fact_ids") or []))
        )
        assert mc[0]["source_fact_ids"] == ledger_row["source_fact_ids"]


def test_coverage_integrity_gate_detects_cross_claim_blob():
    parsed, allowed = _payload_bundle()
    bullets = list(parsed["bullets"])
    ledger = list(parsed["claim_ledger"])
    good = build_unify_bullets_text_claim_coverage(bullets, ledger, allowed)
    tampered = dict(good)
    tampered["sentences"] = list(good["sentences"])
    row0 = dict(tampered["sentences"][0])
    mc = list(row0["material_claims"])
    mc[0] = dict(mc[0])
    mc[0]["claim_text"] = bullets[-1]["bullet_text"]
    row0["material_claims"] = mc
    tampered["sentences"][0] = row0

    ok, reason = check_unify_bullets_text_claim_coverage_integrity(bullets, ledger, tampered, allowed)
    assert ok is False
    assert reason and "mismatch" in reason


def test_exec_summary_sentence_claim_coverage_claim_text_matches_each_claim_row():
    """Regression: inner loop must append each matching row's claim_text (no stale outer variable)."""
    ledger = [
        {"claim_text": "Alpha discovery.", "source_fact_ids": ["f1"]},
        {"claim_text": "Beta remediation outcome.", "source_fact_ids": ["f2"]},
    ]
    allowed = {"f1", "f2"}
    resume = "Alpha discovery."
    cov = build_sentence_claim_coverage(resume, ledger, allowed)
    texts = [m["claim_text"] for m in cov["sentences"][0]["material_claims"]]
    assert texts == ["Alpha discovery."]
    assert "Beta remediation outcome." not in texts


def test_integrity_gate_id_constant_stable():
    assert TEXT_COVERAGE_INTEGRITY_GATE_ID == "x2_text_claim_coverage_integrity"
