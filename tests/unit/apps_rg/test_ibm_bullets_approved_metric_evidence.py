"""Approved-promotable metric evidence for the ibm_bullets X1D judge (typed-edge guardrails).

Regression guard for the keystone W2.3 fix: a graph-approved, promotable, section-eligible
metric_outcome (the IBM-AWS alliance "20% joint revenue growth") must reach the X1D judge's
allowed_fact_packet as supporting evidence, even when section display-budget capping
(``graph_role_episode_selector`` ``metric_cap``) drops it from the per-bundle proof-pool
contribution. Without it Gemini-Pro graded the literal "20%" in the bullet as
``unsupported_metric`` (factual_support FAIL) and blocked ibm_bullets at X3.
"""
from __future__ import annotations

from apps_rg.runtime.sections.ibm_bullets_lane import build_ibm_bullets_allowed_fact_packet
from apps_rg.runtime.sections.ibm_role_episode_evidence import (
    FORBIDDEN_METRIC_SUBSTRINGS,
    approved_promotable_metric_evidence,
)


def test_approved_metric_evidence_surfaces_20pct() -> None:
    ev = approved_promotable_metric_evidence("ibm_bullets")
    assert ev, "expected approved metric_outcome evidence for ibm_bullets"
    by_id = {e["fact_id"]: e for e in ev}
    twenty = by_id.get("metric_ibm_20pct_joint_revenue_growth")
    assert twenty is not None, "the approved alliance 20% metric must be surfaced"
    assert "20%" in twenty["claim_text"], "evidence claim_text must carry the 20% figure"
    assert twenty["has_metric"] is True
    assert twenty["metric_outcome_ids"] == ["metric_ibm_20pct_joint_revenue_growth"]


def test_approved_metric_evidence_excludes_forbidden_and_off_section() -> None:
    ev = approved_promotable_metric_evidence("ibm_bullets")
    for e in ev:
        low = str(e.get("metric_raw") or "").lower()
        assert not any(f in low for f in FORBIDDEN_METRIC_SUBSTRINGS), (
            f"forbidden metric leaked into judge evidence: {e['fact_id']} -> {e['metric_raw']}"
        )
    # A section nobody is eligible for yields nothing (eligibility is enforced).
    assert approved_promotable_metric_evidence("__no_such_section__") == []


def test_packet_appends_approved_metric_evidence() -> None:
    ibm_facts = [{"fact_id": "bul_ibm_005", "claim_text": "alliance co-sell", "has_metric": False}]
    extra = approved_promotable_metric_evidence("ibm_bullets")
    packet = build_ibm_bullets_allowed_fact_packet(
        ibm_facts=ibm_facts,
        ibm_header={},
        proof_pool_ref="",
        proof_pool_digest="",
        approved_metric_evidence=extra,
    )
    fact_ids = {e.get("fact_id") for e in packet}
    assert "bul_ibm_005" in fact_ids
    assert "metric_ibm_20pct_joint_revenue_growth" in fact_ids, (
        "approved metric evidence must be appended to the judge packet"
    )
