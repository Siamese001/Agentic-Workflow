"""X2 gates must fail when RetiredProvider accidentally emits retired rewrite-intensity fields."""

from __future__ import annotations

from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS, run_ibm_bullets_x2_gates
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates


def _unify_po_with_intensity() -> dict:
    bullets = [
        {"bullet_id": bid, "bullet_text": f"t {bid}", "rewrite_intensity": "HEAVY", "source_fact_ids": [bid]}
        for bid in UNIFY_BULLET_IDS
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    return {
        "bullets": bullets,
        "selected_fact_plan": {},
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "rewrite_distribution": {"HEAVY": 6, "total": 6},
        "self_check": {},
    }


def test_unify_x2_fails_on_rewrite_intensity_model_fields() -> None:
    po = _unify_po_with_intensity()
    gates = run_unify_bullets_x2_gates(
        bullets=po["bullets"],
        parsed_output=po,
        claim_ledger=po["claim_ledger"],
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_no_rewrite_intensity_model")
    assert gate.pass_ is False


def test_ibm_x2_fails_on_rewrite_intensity_model_fields() -> None:
    bullets = [
        {"bullet_id": bid, "bullet_text": f"t {bid}", "rewrite_intensity": "MODERATE", "source_fact_ids": [bid]}
        for bid in IBM_BULLET_IDS
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    po = {
        "bullets": bullets,
        "selected_fact_plan": {},
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_ibm_no_rewrite_intensity_model")
    assert gate.pass_ is False
