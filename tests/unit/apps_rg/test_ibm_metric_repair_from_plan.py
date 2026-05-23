a""IBM bullet metric anchor repair from graph plan (not base-resume hydration)."""

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
            "claim_text": "Delivered 99.9% platform availability across enterprise workloads.",
            "metric_raw": "99.9%",
        },
        {
            "fact_id": "bul_ibm_002",
            "claim_text": "Reduced cycle time 30% via agentic orchestration.",
            "metric_raw": "30%",
        },
        {
            "fact_id": "bul_ibm_003",
            "claim_text": "Cut integration cost 25% with governed runtime fabric.",
            "metric_raw": "25%",
        },
        {
            "fact_id": "bul_ibm_004",
            "claim_text": "Improved throughput 50% on retrieval-heavy pipelines.",
            "metric_raw": "50%",
        },
        {
            "fact_id": "bul_ibm_005",
            "claim_text": "Drove $15M in platform-led revenue expansion.",
            "metric_raw": "$15M",
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
    assert "$15M" in combined and "99.9%" in combined and "30%" in combined
    assert _metric_granularity_ok(repaired, parsed.get("claim_ledger") or [])
