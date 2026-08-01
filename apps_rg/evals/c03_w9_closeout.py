"""W9 blinded shadow-rollout prerequisite and evaluation closeout harness.

The harness never manufactures variants or coach judgments.  It verifies the
existing W9 prerequisites and, on the active path, derives the whole-resume
gate from a sealed substantive evaluation receipt.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from apps_rg.evals.whole_resume.constants import METRIC_NAMES
from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest

SCHEMA_VERSION = "apps_rg.c03.w9_closeout.v1"
EXPECTED_PAIR_COUNT = 6
EXPECTED_REVIEWS_PER_PAIR = 2
WHOLE_RESUME_RECEIPT_SCHEMA = "apps_rg.whole_resume_evaluation_receipt.v1"
_REQUIRED_PASS_METRICS: Mapping[str, Any] = {
    "material_claim_grounding_rate": 1.0,
    "critical_cross_section_inconsistency_count": 0,
    "chronology_inconsistency_count": 0,
    "employer_title_inconsistency_count": 0,
    "duplicate_achievement_rate": 0.0,
    "summary_experience_repetition_rate": 0.0,
    "ats_structure_pass": True,
    "jd_parroting_risk_count": 0,
    "unnatural_keyword_insertion_count": 0,
    "unsupported_leadership_inflation_count": 0,
    "unsupported_scope_inflation_count": 0,
    "human_grounding_no_worse_rate": 1.0,
    "human_naturalness_no_worse_rate": 1.0,
    "human_relevance_no_worse_rate": 1.0,
    "material_defect_count": 0,
}


def _pair_set_digest(pair_receipts: Sequence[Mapping[str, Any]]) -> str:
    return stable_digest(
        [
            {
                "pair_id": str(row.get("pair_id") or ""),
                "pair_payload_digest": str(row.get("pair_payload_digest") or row.get("content_digest") or ""),
            }
            for row in sorted(pair_receipts, key=lambda value: str(value.get("pair_id") or ""))
        ]
    )


def _evaluation_receipt_failures(
    receipt: Mapping[str, Any],
    *,
    pair_receipts: Sequence[Mapping[str, Any]],
    official_w6_status: str,
) -> list[str]:
    failures: list[str] = []
    if receipt.get("schema_version") != WHOLE_RESUME_RECEIPT_SCHEMA:
        failures.append("whole_resume_evaluation_receipt_schema_invalid")
    expected_digest = stable_digest({key: value for key, value in receipt.items() if key != "record_digest"})
    if receipt.get("record_digest") != expected_digest:
        failures.append("whole_resume_evaluation_receipt_digest_invalid")
    if receipt.get("status") != "PASS" or receipt.get("whole_resume_release_pass") is not True:
        failures.append("whole_resume_evaluation_nonpass")
    metrics = receipt.get("metrics")
    if (
        not isinstance(metrics, Mapping)
        or set(metrics) != set(METRIC_NAMES)
        or any(value is None for value in metrics.values())
    ):
        failures.append("whole_resume_evaluation_metrics_invalid")
    elif any(metrics.get(name) != expected for name, expected in _REQUIRED_PASS_METRICS.items()):
        failures.append("whole_resume_evaluation_thresholds_nonpass")
    pair_results = receipt.get("pair_results")
    if (
        not isinstance(pair_results, Sequence)
        or isinstance(pair_results, (str, bytes))
        or len(pair_results) != 6
    ):
        failures.append("whole_resume_evaluation_pair_results_invalid")
    elif any(not _pair_result_passes(result) for result in pair_results):
        failures.append("whole_resume_evaluation_pair_result_nonpass")
    elif stable_digest(
        [
            {
                "pair_id": str(result.get("pair_id") or ""),
                "pair_payload_digest": str(result.get("pair_payload_digest") or ""),
            }
            for result in sorted(pair_results, key=lambda value: str(value.get("pair_id") or ""))
        ]
    ) != receipt.get("pair_set_digest"):
        failures.append("whole_resume_evaluation_pair_results_binding_mismatch")
    if receipt.get("failure_codes") or receipt.get("unknown_reasons"):
        failures.append("whole_resume_evaluation_reasons_nonempty")
    if (
        receipt.get("pair_count") != EXPECTED_PAIR_COUNT
        or receipt.get("human_review_count") != EXPECTED_PAIR_COUNT * EXPECTED_REVIEWS_PER_PAIR
        or receipt.get("adjudication_count") != EXPECTED_PAIR_COUNT
    ):
        failures.append("whole_resume_evaluation_quorum_invalid")
    pair_ids = sorted(str(row.get("pair_id") or "") for row in pair_receipts)
    if receipt.get("pair_ids") != pair_ids:
        failures.append("whole_resume_evaluation_pair_ids_mismatch")
    if receipt.get("pair_set_digest") != _pair_set_digest(pair_receipts):
        failures.append("whole_resume_evaluation_pair_set_mismatch")
    if receipt.get("official_w6_status") != str(official_w6_status).upper():
        failures.append("whole_resume_evaluation_w6_binding_mismatch")
    authority = receipt.get("authority")
    if not isinstance(authority, Mapping) or (
        authority.get("feeds_w9_closeout") is not True
        or authority.get("release_authorizing") is not False
        or authority.get("current_run_authority_unchanged") is not True
        or authority.get("human_review_satisfied") is not True
    ):
        failures.append("whole_resume_evaluation_authority_invalid")
    return failures


def _pair_result_passes(result: Any) -> bool:
    if not isinstance(result, Mapping):
        return False
    candidate = result.get("candidate_result")
    pairwise = result.get("pairwise_result")
    return (
        isinstance(candidate, Mapping)
        and candidate.get("status") == "PASS"
        and isinstance(pairwise, Mapping)
        and pairwise.get("status") == "PASS"
    )


def build_w9_closeout(
    *,
    pair_receipts: Sequence[Mapping[str, Any]] = (),
    coach_reviews: Sequence[Mapping[str, Any]] = (),
    adjudications: Sequence[Mapping[str, Any]] = (),
    official_w6_status: str = "UNKNOWN",
    generation_authorized: bool = False,
    whole_resume_evaluation_receipt: Mapping[str, Any] | None = None,
    # Compatibility only for callers predating the sealed Wave 5 receipt.
    whole_resume_release_pass: bool = False,
) -> dict[str, Any]:
    pair_ids = [str(row.get("pair_id") or "").strip() for row in pair_receipts]
    review_pairs = [str(row.get("pair_id") or "").strip() for row in coach_reviews]
    adjudicated_pairs = [str(row.get("pair_id") or row.get("item_id") or "").strip() for row in adjudications]
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
    if whole_resume_evaluation_receipt is None:
        if any(row.get("human_quality_no_worse") is not True for row in adjudications):
            failures.append("human_quality_no_worse_nonpass")
        if any(row.get("target_relevance_not_worse") is not True for row in adjudications):
            failures.append("target_relevance_nonpass")
    if str(official_w6_status).upper() != "PASS":
        failures.append("official_w6_nonpass")
    if whole_resume_evaluation_receipt is not None:
        receipt_failures = (
            _evaluation_receipt_failures(
                whole_resume_evaluation_receipt,
                pair_receipts=pair_receipts,
                official_w6_status=official_w6_status,
            )
            if isinstance(whole_resume_evaluation_receipt, Mapping)
            else ["whole_resume_evaluation_receipt_invalid"]
        )
        failures.extend(receipt_failures)
        whole_resume_release_pass = not receipt_failures
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
        "whole_resume_gate_source": (
            "SEALED_EVALUATION_RECEIPT"
            if whole_resume_evaluation_receipt is not None
            else "LEGACY_BOOLEAN_COMPATIBILITY"
        ),
        "whole_resume_evaluation_receipt_digest": (
            str(whole_resume_evaluation_receipt.get("record_digest") or "")
            if isinstance(whole_resume_evaluation_receipt, Mapping)
            else None
        ),
        "release_pass": release_pass,
        "promotion_eligible": release_pass,
        "unknown_is_pass": False,
        "failure_codes": failures,
    }
    body["record_digest"] = stable_digest(body)
    return body


__all__ = ["build_w9_closeout"]
