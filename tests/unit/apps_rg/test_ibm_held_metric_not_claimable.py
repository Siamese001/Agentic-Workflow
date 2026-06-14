"""Phase-2 graph-expansion fallback must not mark an unapproved/held raw ledger metric claimable.

Regression for the W2.2 bul_ibm_005 held-metric anchor false-block (plan
typed-edge-role-facet-guardrails-a6f3d2, operator decision 2026-06-14): the
``build_ibm_phase2_graph_plan_fact`` fallback used to set ``has_metric=True`` from ANY raw
ledger ``metric_values[0]`` (e.g. fact_revenue_ops_001's held "$10M new ARR"), with no
approved ``metric_outcome`` binding. That made ``x2_ibm_metric_anchor_bullet_ownership``
require anchoring a figure the hold-metric gate forbids in output. A raw metric is now
claimable ONLY when an approved metric_outcome is bound.
"""

from __future__ import annotations

import apps_rg.runtime.sections.ibm_bullets_graph_evidence as mod

_HOP = {"graph_hop_path": [{"edge_type": "e", "from": "a", "to": "b"}], "skill_id": "skill_x"}


def _build(ledger_row: dict, monkeypatch) -> dict:
    # Force the generic Phase-2 fallback (not the HIGH/eligible-MEDIUM slice path) and a
    # non-empty claim, so the test exercises the metric-gating branch deterministically.
    monkeypatch.setattr(
        mod, "_claim_text_for_phase2_graph_fact", lambda **_: "Led IBM-AWS alliance co-sell."
    )
    fact = mod.build_ibm_phase2_graph_plan_fact(
        fact_id="bul_ibm_005",
        ledger_row=ledger_row,
        hop_entry=_HOP,
        graph={},
        section_id="ibm_bullets",
    )
    assert fact is not None
    return fact


def test_held_metric_without_metric_outcome_is_not_claimable(monkeypatch) -> None:
    fact = _build(
        {
            "metric_values": ["$10M new ARR"],
            "confidence": "MEDIUM",
            "verification_status": "graph_phase2_track",
        },
        monkeypatch,
    )
    assert fact["has_metric"] is False
    assert fact["metric_raw"] == ""
    # Raw value retained for lineage, but not marked claimable.
    assert fact["metric_values"] == ["$10M new ARR"]
    assert fact["metric_outcome_ids"] == []


def test_approved_metric_outcome_binding_is_claimable(monkeypatch) -> None:
    fact = _build(
        {
            "metric_values": ["20% joint revenue growth"],
            "metric_outcome_ids": ["metric_ibm_20pct_joint_revenue_growth"],
            "confidence": "MEDIUM",
            "verification_status": "graph_phase2_track",
        },
        monkeypatch,
    )
    assert fact["has_metric"] is True
    assert fact["metric_raw"] == "20% joint revenue growth"
    assert fact["metric_outcome_ids"] == ["metric_ibm_20pct_joint_revenue_growth"]
