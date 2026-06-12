"""IBM bullet metric anchor repair from graph plan (not base-resume hydration)."""

from __future__ import annotations

from apps_rg.runtime.sections.ibm_bullets_lane import inject_ibm_locked_metric_anchors
from apps_rg.runtime.validators.ibm_bullets_x2 import (
    IBM_BULLET_IDS,
    _ibm_metric_anchors_on_assigned_bullets,
    _metric_granularity_ok,
)


def _plan_facts() -> list[dict]:
    return [
        {
            "fact_id": "bul_ibm_001",
            "claim_text": "Led on-prem to AWS modernization waves for regulated client workloads.",
            "metric_raw": "",
        },
        {
            "fact_id": "bul_ibm_002",
            "claim_text": "Compressed HPC stress-test cycles from weeks to hours for risk scenarios.",
            "metric_raw": "weeks to hours",
        },
        {
            "fact_id": "bul_ibm_003",
            "claim_text": "Converted buyer discovery into target architecture and delivery handoff packages.",
            "metric_raw": "",
        },
        {
            "fact_id": "bul_ibm_004",
            "claim_text": "Built budget and delivery-status BI views for executive portfolio decisions.",
            "metric_raw": "",
        },
        {
            "fact_id": "bul_ibm_005",
            "claim_text": "Led IBM-AWS alliance co-sell frameworks that expanded joint revenue.",
            "metric_raw": "20% joint revenue growth",
        },
    ]


def test_inject_ibm_locked_metric_anchors_restores_x2_metric_gates() -> None:
    bullets = [
        {"bullet_id": bid, "bullet_text": "Generic rewrite without locked metrics.", "source_fact_ids": [bid]}
        for bid in IBM_BULLET_IDS
    ]
    parsed: dict = {"bullets": bullets, "claim_ledger": []}
    allowed = {bid for bid in IBM_BULLET_IDS} | {
        f"{bid}_metric_abc12345" for bid in IBM_BULLET_IDS
    }

    anchor_ok_before, _ = _ibm_metric_anchors_on_assigned_bullets(bullets)
    assert anchor_ok_before is False

    inject_ibm_locked_metric_anchors(
        parsed,
        plan_facts=_plan_facts(),
        allowed_fact_ids=allowed,
    )

    repaired = list(parsed["bullets"])
    anchor_ok_after, fails = _ibm_metric_anchors_on_assigned_bullets(repaired)
    assert anchor_ok_after is True, fails
    combined = " ".join(str(b.get("bullet_text") or "") for b in repaired)
    assert "weeks to hours" in combined and "20%" in combined
    assert "$15M" not in combined and "99.9%" not in combined and "30%" not in combined
    assert _metric_granularity_ok(repaired, parsed.get("claim_ledger") or [])
