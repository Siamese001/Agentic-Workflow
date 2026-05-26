"""IBM bullets lane nuance: five bullets, pool selection, metric anchors."""

from __future__ import annotations

import json

from apps_rg.runtime.validators.ibm_bullets_x2 import (
    IBM_BULLET_IDS,
    run_ibm_bullets_x2_gates,
)

IBM_BULLETS_CRITICAL_GATES = frozenset(
    {
        "x2_ibm_bullet_count_5",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_text_claim_coverage_integrity",
        "x2_ibm_metric_anchor_bullet_ownership",
    }
)


def _five_bullets(*, strip_metrics: bool = False) -> tuple[list[dict], dict]:
    bullets = []
    ledger = []
    for bid in IBM_BULLET_IDS:
        text = f"Enterprise platform delivery for {bid} with measurable outcomes."
        if bid == "bul_ibm_001":
            text = "Delivered 99.9% uptime for regulated financial services platforms."
        if bid == "bul_ibm_005" and not strip_metrics:
            text = "Drove $15M incremental revenue through hyperscaler alliances."
        if bid == "bul_ibm_005" and strip_metrics:
            text = "Led hyperscaler alliances without revenue metrics."
        bullets.append({"bullet_id": bid, "bullet_text": text, "source_fact_ids": [bid]})
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
    return bullets, {"bullets": bullets, "claim_ledger": ledger}


def test_missing_ibm_metric_fails_anchor_gate() -> None:
    bullets, parsed = _five_bullets(strip_metrics=True)
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=[],
    )
    assert any(g.gate_id == "x2_ibm_metric_anchor_bullet_ownership" and not g.pass_ for g in gates)


def test_unify_runtime_term_fails_gate() -> None:
    bullets, parsed = _five_bullets()
    bullets[0]["bullet_text"] = "Built agentic runtime with GraphRAG orchestration for IBM clients."
    parsed["claim_ledger"][0]["claim_text"] = bullets[0]["bullet_text"]
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        raw_output=json.dumps(parsed),
        x1d_judges=[],
    )
    assert any(g.gate_id == "x2_no_unify_runtime_terms" and not g.pass_ for g in gates)
