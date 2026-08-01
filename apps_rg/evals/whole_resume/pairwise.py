"""Human W9 pairwise scoring over sealed blinded reviews."""

from __future__ import annotations

from typing import Any, Mapping

from .constants import W9_DIMENSIONS


def _variant_labels(labels: Mapping[str, Any], variant: str) -> Mapping[str, Any]:
    key = "resume_a" if variant == "A" else "resume_b"
    value = labels.get(key)
    return value if isinstance(value, Mapping) else {}


def _agreement_rate(reviews: list[Mapping[str, Any]]) -> float | None:
    if len(reviews) != 2:
        return None
    left = reviews[0].get("labels")
    right = reviews[1].get("labels")
    if not isinstance(left, Mapping) or not isinstance(right, Mapping):
        return None
    comparisons = [left.get("preference") == right.get("preference")]
    for variant in ("resume_a", "resume_b"):
        left_dimensions = left.get(variant)
        right_dimensions = right.get(variant)
        if not isinstance(left_dimensions, Mapping) or not isinstance(right_dimensions, Mapping):
            return None
        comparisons.extend(
            left_dimensions.get(dimension) == right_dimensions.get(dimension) for dimension in W9_DIMENSIONS
        )
    return round(sum(comparisons) / len(comparisons), 6)


def evaluate_pairwise(pair: Mapping[str, Any], candidate_result: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve a blinded adjudication and calculate named no-worse criteria."""

    candidate_variant = str(pair.get("candidate_variant") or "")
    baseline_variant = "B" if candidate_variant == "A" else "A"
    adjudication = pair.get("adjudication")
    final_labels = adjudication.get("final_labels") if isinstance(adjudication, Mapping) else None
    if not isinstance(final_labels, Mapping):
        return {
            "status": "UNKNOWN",
            "failure_codes": [],
            "unknown_reasons": ["sealed adjudication labels are unavailable"],
        }
    candidate_scores = _variant_labels(final_labels, candidate_variant)
    baseline_scores = _variant_labels(final_labels, baseline_variant)
    if set(candidate_scores) != set(W9_DIMENSIONS) or set(baseline_scores) != set(W9_DIMENSIONS):
        return {
            "status": "UNKNOWN",
            "failure_codes": [],
            "unknown_reasons": ["adjudication dimensions are incomplete"],
        }
    dimension_deltas = {
        dimension: int(candidate_scores[dimension]) - int(baseline_scores[dimension])
        for dimension in W9_DIMENSIONS
    }
    raw_preference = str(final_labels.get("preference") or "")
    resolved_preference = (
        "CANDIDATE"
        if raw_preference == candidate_variant
        else "BASELINE"
        if raw_preference == baseline_variant
        else "TIE"
        if raw_preference == "TIE"
        else "UNKNOWN"
    )
    grounding_no_worse = dimension_deltas["authenticity_factuality"] >= 0
    naturalness_no_worse = dimension_deltas["claim_naturalness"] >= 0
    relevance_no_worse = dimension_deltas["target_relevance"] >= 0
    all_dimensions_no_worse = all(value >= 0 for value in dimension_deltas.values())
    narrative_coherence = int(candidate_scores["executive_readability"])

    failures = list(candidate_result.get("failure_codes") or [])
    if not grounding_no_worse:
        failures.append("HUMAN_GROUNDING_REGRESSION")
    if not naturalness_no_worse:
        failures.append("HUMAN_NATURALNESS_REGRESSION")
    if not relevance_no_worse:
        failures.append("HUMAN_RELEVANCE_REGRESSION")
    if candidate_result.get("status") == "UNKNOWN":
        return {
            "status": "UNKNOWN",
            "failure_codes": sorted(set(failures)),
            "unknown_reasons": list(candidate_result.get("unknown_reasons") or []),
        }
    status = "FAIL" if failures else "PASS"
    reviews = [row for row in pair.get("reviews") or [] if isinstance(row, Mapping)]
    return {
        "status": status,
        "candidate_variant": candidate_variant,
        "raw_preference": raw_preference,
        "resolved_preference": resolved_preference,
        "dimension_deltas": dimension_deltas,
        "grounding_no_worse": grounding_no_worse,
        "naturalness_no_worse": naturalness_no_worse,
        "relevance_no_worse": relevance_no_worse,
        "all_dimensions_no_worse": all_dimensions_no_worse,
        "narrative_coherence": narrative_coherence,
        "reviewer_agreement_rate": _agreement_rate(reviews),
        "material_defect_count": len(set(failures)),
        "failure_codes": sorted(set(failures)),
        "unknown_reasons": [],
    }


__all__ = ["evaluate_pairwise"]
