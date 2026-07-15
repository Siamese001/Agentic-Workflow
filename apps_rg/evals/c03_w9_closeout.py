"""W9 blinded shadow-rollout closeout harness.

The harness records engineering readiness without manufacturing variants or
coach judgments.  Promotion remains impossible until six authorized pairs,
qualified reviews/adjudications, and official W6 PASS evidence are supplied.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest

SCHEMA_VERSION = "apps_rg.c03.w9_closeout.v1"
EXPECTED_PAIR_COUNT = 6
EXPECTED_REVIEWS_PER_PAIR = 2


def build_w9_closeout(
    *,
    pair_receipts: Sequence[Mapping[str, Any]] = (),
    coach_reviews: Sequence[Mapping[str, Any]] = (),
    adjudications: Sequence[Mapping[str, Any]] = (),
    official_w6_status: str = "UNKNOWN",
    generation_authorized: bool = False,
    whole_resume_release_pass: bool = False,
) -> dict[str, Any]:
    pair_ids = [str(row.get("pair_id") or "").strip() for row in pair_receipts]
    review_pairs = [str(row.get("pair_id") or "").strip() for row in coach_reviews]
    adjudicated_pairs = [
        str(row.get("pair_id") or row.get("item_id") or "").strip()
        for row in adjudications
    ]
    failures: list[str] = []
    if not generation_authorized:
        failures.append("authorized_variant_generation_missing")
    if len(pair_ids) != EXPECTED_PAIR_COUNT or len(set(pair_ids)) != EXPECTED_PAIR_COUNT:
        failures.append("six_unique_blinded_pairs_missing")
    if any(row.get("variant_identity_hidden") is not True for row in pair_receipts):
        failures.append("variant_identity_not_blinded")
    if len(review_pairs) != EXPECTED_PAIR_COUNT * EXPECTED_REVIEWS_PER_PAIR:
        failures.append("qualified_coach_review_quorum_missing")
    for pair_id in set(pair_ids):
        if review_pairs.count(pair_id) != EXPECTED_REVIEWS_PER_PAIR:
            failures.append(f"coach_review_quorum:{pair_id}")
    if set(adjudicated_pairs) != set(pair_ids) or len(adjudicated_pairs) != EXPECTED_PAIR_COUNT:
        failures.append("one_adjudication_per_pair_missing")
    if any(row.get("qualified_resume_coach") is not True for row in coach_reviews):
        failures.append("unqualified_coach_review")
    if any(row.get("human_quality_no_worse") is not True for row in adjudications):
        failures.append("human_quality_no_worse_nonpass")
    if any(row.get("target_relevance_not_worse") is not True for row in adjudications):
        failures.append("target_relevance_nonpass")
    if str(official_w6_status).upper() != "PASS":
        failures.append("official_w6_nonpass")
    if not whole_resume_release_pass:
        failures.append("whole_resume_release_gate_nonpass")

    failures = sorted(set(failures))
    release_pass = not failures
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "engineering_harness_complete": True,
        "generation_authorized": generation_authorized,
        "pair_count": len(pair_ids),
        "coach_review_count": len(coach_reviews),
        "adjudication_count": len(adjudications),
        "official_w6_status": str(official_w6_status).upper(),
        "whole_resume_release_pass": whole_resume_release_pass,
        "release_pass": release_pass,
        "promotion_eligible": release_pass,
        "unknown_is_pass": False,
        "failure_codes": failures,
    }
    body["record_digest"] = stable_digest(body)
    return body


__all__ = ["build_w9_closeout"]
