from __future__ import annotations

from apps_rg.evals.c03_w9_closeout import build_w9_closeout


def test_w9_harness_is_complete_but_empty_evidence_cannot_promote() -> None:
    receipt = build_w9_closeout()
    assert receipt["engineering_harness_complete"] is True
    assert receipt["official_w6_status"] == "UNKNOWN"
    assert receipt["release_pass"] is False
    assert receipt["promotion_eligible"] is False
    assert "authorized_variant_generation_missing" in receipt["failure_codes"]
    assert "six_unique_blinded_pairs_missing" in receipt["failure_codes"]


def test_w9_requires_two_qualified_reviews_and_adjudication_per_pair() -> None:
    pairs = [
        {"pair_id": f"pair-{index}", "variant_identity_hidden": True}
        for index in range(6)
    ]
    reviews = [
        {"pair_id": f"pair-{index}", "qualified_resume_coach": True}
        for index in range(6)
        for _ in range(2)
    ]
    adjudications = [
        {
            "pair_id": f"pair-{index}",
            "human_quality_no_worse": True,
            "target_relevance_not_worse": True,
        }
        for index in range(6)
    ]
    receipt = build_w9_closeout(
        pair_receipts=pairs,
        coach_reviews=reviews,
        adjudications=adjudications,
        official_w6_status="PASS",
        generation_authorized=True,
        whole_resume_release_pass=True,
    )
    assert receipt["release_pass"] is True
    assert receipt["promotion_eligible"] is True
