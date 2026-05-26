"""Unify bullets mechanism-stack cap and metric anchor ownership."""

from __future__ import annotations

from apps_rg.runtime.validators.unify_bullets_x2 import (
    UNIFY_BULLET_IDS,
    _mechanism_dense_bullet_ids,
    _unify_metric_anchors_on_assigned_bullets,
    run_unify_bullets_x2_gates,
)


def _six_bullets_with_one_dense_stack() -> list[dict]:
    bullets = []
    for bid in UNIFY_BULLET_IDS:
        text = f"Outcome bullet for {bid} with delivery and governance impact."
        if bid == "bul_unify_001":
            text = (
                "Designed governed agentic AI platform combining deterministic routing, multi-agent "
                "orchestration, GraphRAG retrieval, sandboxed execution, and policy gating."
            )
        if bid == "bul_unify_004":
            text = "Reduced lab-to-production cycle time from six months to three weeks while preserving auditability."
        if bid == "bul_unify_006":
            text = "Generated $22M in IP-led revenue, expanded gross margins by 20%, and scaled team from 8 to 28 specialists."
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "source_fact_ids": [bid],
            }
        )
    return bullets


def test_at_most_one_mechanism_dense_bullet_detects_two_stacks():
    bullets = _six_bullets_with_one_dense_stack()
    bullets[1]["bullet_text"] = (
        "Built dependency graphs with deterministic routing, multi-agent orchestration, GraphRAG, "
        "sandboxed execution, and policy gating."
    )
    dense = _mechanism_dense_bullet_ids(bullets)
    assert len(dense) >= 2


def test_metric_anchor_requires_tokens_on_assigned_bullets():
    bullets = _six_bullets_with_one_dense_stack()
    ok, fails = _unify_metric_anchors_on_assigned_bullets(bullets)
    assert ok is True
    assert not fails


def test_x2_emits_mechanism_and_metric_anchor_gates():
    bullets = _six_bullets_with_one_dense_stack()
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output={"bullets": bullets, "claim_ledger": ledger},
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
    )
    gate_ids = {g.gate_id for g in gates}
    assert "x2_unify_at_most_one_mechanism_dense_bullet" in gate_ids
    assert "x2_unify_metric_anchor_bullet_ownership" in gate_ids
    assert "x2_unify_protected_bullet_metrics_preserved" in gate_ids
