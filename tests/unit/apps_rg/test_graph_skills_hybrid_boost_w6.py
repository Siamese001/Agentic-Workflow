"""W6: hybrid boost reorder-only + NEG-3 fail-closed widen rejection."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.c0.hybrid_informed_fact_plan_reorder import (
    apply_hybrid_informed_fact_plan_reorder,
    reorder_selected_fact_plan_by_hybrid_scores,
)
from apps_rg.runtime.graph_skills_hybrid_boost import (
    apply_hybrid_boost_reorder_only,
    audit_section_hybrid_boost,
    build_hybrid_graph_boost_receipt,
    collect_rejected_hybrid_widen_attempts,
)
from apps_rg.runtime.validators.graph_skills_proof_common import (
    GraphSkillsProofError,
    assert_hybrid_fact_ids_in_resolver_pool,
)

REPO = Path(__file__).resolve().parents[3]


def _plan() -> dict:
    return {
        "section_id": "executive_summary",
        "selection_method": "augmented_skills_graph_c03_graphrag",
        "facts": [
            {"fact_id": "fact_alpha", "claim_text": "alpha"},
            {"fact_id": "fact_beta", "claim_text": "beta"},
            {"fact_id": "fact_gamma", "claim_text": "gamma"},
        ],
        "required_fact_ids": ["fact_alpha", "fact_beta", "fact_gamma"],
    }


def _hybrid_doc(*, include_outside: bool = True) -> dict:
    items = [
        {
            "source_id": "fact_gamma",
            "content": "gamma",
            "confidence_score": 9.0,
        },
        {
            "source_id": "fact_alpha",
            "content": "alpha",
            "confidence_score": 1.0,
        },
    ]
    if include_outside:
        items.append(
            {
                "source_id": "fact_outside_pool_w6",
                "content": "must not widen pool",
                "confidence_score": 100.0,
            }
        )
    return {"enrichment_items": items}


def test_neg3_hybrid_outside_resolver_pool() -> None:
    with pytest.raises(GraphSkillsProofError, match="outside resolver pool"):
        assert_hybrid_fact_ids_in_resolver_pool(
            section_id="executive_summary",
            hybrid_suggested_fact_ids=["fact_outside_pool_w6"],
            resolver_allowed_fact_ids=["fact_alpha", "fact_beta"],
        )


def test_collect_rejected_widen_attempts() -> None:
    allowed = {"fact_alpha", "fact_beta", "fact_gamma"}
    rejected = collect_rejected_hybrid_widen_attempts(
        _hybrid_doc()["enrichment_items"],
        resolver_allowed_fact_ids=allowed,
    )
    assert any(r["fact_id"] == "fact_outside_pool_w6" for r in rejected)
    assert all(r["reason_code"] == "outside_resolver_pool" for r in rejected)


def test_reorder_preserves_fact_id_set() -> None:
    plan = _plan()
    reordered = reorder_selected_fact_plan_by_hybrid_scores(
        plan,
        score_by_fact_id={"fact_gamma": 9.0, "fact_alpha": 1.0, "fact_beta": 2.0},
    )
    before = {f["fact_id"] for f in plan["facts"]}
    after = {f["fact_id"] for f in reordered["facts"]}
    assert before == after
    assert reordered["facts"][0]["fact_id"] == "fact_gamma"


def test_apply_hybrid_boost_reorder_only_no_widen() -> None:
    plan = _plan()
    reordered, summary = apply_hybrid_boost_reorder_only(
        plan, hybrid_doc=_hybrid_doc(), section_id="executive_summary"
    )
    assert summary["pool_widened"] is False
    assert summary["status"] == "PASS"
    assert summary["rejected_widen_attempt_count"] >= 1
    assert reordered["facts"][0]["fact_id"] == "fact_gamma"


def test_apply_hybrid_informed_does_not_add_facts() -> None:
    plan = _plan()
    out = apply_hybrid_informed_fact_plan_reorder(plan, hybrid_doc=_hybrid_doc())
    assert len(out["facts"]) == len(plan["facts"])


def test_audit_section_neg3_pass() -> None:
    row = audit_section_hybrid_boost(
        section_id="executive_summary",
        plan=_plan(),
        hybrid_doc=_hybrid_doc(),
        probe_outside_pool_ids=("fact_probe_w6",),
    )
    assert row["neg3_pass"] is True
    assert row["pool_widen_forbidden"] is True
    assert row["reorder_applied"] is True


@pytest.mark.slow
def test_build_hybrid_graph_boost_receipt() -> None:
    receipt = build_hybrid_graph_boost_receipt(repo_root=REPO)
    assert receipt["status"] == "PASS"
    assert receipt["neg3_all_lanes_pass"] is True
    assert receipt["reorder_only"] is True
    assert len(receipt["lanes"]) >= 1
    lane = receipt["lanes"][0]
    assert lane["section_id"] == "executive_summary"
    assert lane["rejected_widen_attempt_count"] >= 1
