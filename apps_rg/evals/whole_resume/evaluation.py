"""Pure offline evaluator for whole-resume and W9 quality."""

from __future__ import annotations

from statistics import fmean
from typing import Any, Mapping

from .constants import EXPECTED_PAIR_COUNT, METRIC_NAMES, RECEIPT_SCHEMA_VERSION
from .deterministic_checks import evaluate_resume_artifact
from .pairwise import evaluate_pairwise
from .reporting import seal_receipt
from .validation import pair_set_digest, validate_input_bundle

_COUNT_METRICS = {
    "critical_cross_section_inconsistency_count",
    "chronology_inconsistency_count",
    "employer_title_inconsistency_count",
    "jd_parroting_risk_count",
    "unnatural_keyword_insertion_count",
    "unsupported_leadership_inflation_count",
    "unsupported_scope_inflation_count",
}


def _empty_metrics() -> dict[str, Any]:
    return dict.fromkeys(METRIC_NAMES)


def _aggregate_deterministic(results: list[Mapping[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    names = set(METRIC_NAMES) - {
        "narrative_coherence",
        "human_grounding_no_worse_rate",
        "human_naturalness_no_worse_rate",
        "human_relevance_no_worse_rate",
        "candidate_preference_rate",
        "material_defect_count",
        "reviewer_agreement_rate",
    }
    for name in sorted(names):
        values = [
            result.get("metrics", {}).get(name)
            for result in results
            if result.get("metrics", {}).get(name) is not None
        ]
        if not values:
            metrics[name] = None
        elif name in _COUNT_METRICS:
            metrics[name] = sum(int(value) for value in values)
        elif all(isinstance(value, bool) for value in values):
            metrics[name] = all(values)
        else:
            metrics[name] = round(fmean(float(value) for value in values), 6)
    return metrics


def _rate(values: list[bool]) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def _unknown_receipt(bundle: Any, reasons: list[str]) -> dict[str, Any]:
    value = bundle if isinstance(bundle, Mapping) else {}
    raw_pairs = value.get("pairs")
    pairs = [pair for pair in raw_pairs if isinstance(pair, Mapping)] if isinstance(raw_pairs, list) else []
    return seal_receipt(
        {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "evaluation_id": str(value.get("evaluation_id") or "UNKNOWN"),
            "input_bundle_digest": str(value.get("bundle_digest") or ""),
            "pair_ids": sorted(str(pair.get("pair_id") or "") for pair in pairs),
            "pair_set_digest": pair_set_digest(pairs),
            "pair_count": len(pairs),
            "human_review_count": sum(
                len(reviews) for pair in pairs if isinstance((reviews := pair.get("reviews")), list)
            ),
            "adjudication_count": sum(1 for pair in pairs if isinstance(pair.get("adjudication"), Mapping)),
            "official_w6_status": str(value.get("official_w6_status") or "UNKNOWN"),
            "status": "UNKNOWN",
            "whole_resume_release_pass": False,
            "metrics": _empty_metrics(),
            "pair_results": [],
            "authority": {
                "classification": "CONDITIONALLY_RELEASE_AUTHORITATIVE",
                "human_review_required": True,
                "human_review_satisfied": False,
                "release_authorizing": False,
                "feeds_w9_closeout": True,
                "promotion_scope": "future_runs_only",
                "current_run_authority_unchanged": True,
            },
            "failure_codes": [],
            "unknown_reasons": reasons,
        }
    )


def evaluate_whole_resume(bundle: Any) -> dict[str, Any]:
    """Evaluate a sealed six-pair W9 bundle without invoking the runtime or a judge."""

    validation_errors = validate_input_bundle(bundle)
    if validation_errors:
        return _unknown_receipt(bundle, validation_errors)
    assert isinstance(bundle, Mapping)
    pairs = [pair for pair in bundle["pairs"] if isinstance(pair, Mapping)]
    pair_results: list[dict[str, Any]] = []
    candidate_results: list[dict[str, Any]] = []
    pairwise_results: list[dict[str, Any]] = []
    for pair in sorted(pairs, key=lambda row: str(row["pair_id"])):
        candidate_key = "resume_a" if pair["candidate_variant"] == "A" else "resume_b"
        baseline_key = "resume_b" if candidate_key == "resume_a" else "resume_a"
        candidate = evaluate_resume_artifact(pair[candidate_key], pair["target_context"])
        baseline = evaluate_resume_artifact(pair[baseline_key], pair["target_context"])
        pairwise = evaluate_pairwise(pair, candidate)
        candidate_results.append(candidate)
        pairwise_results.append(pairwise)
        pair_results.append(
            {
                "pair_id": str(pair["pair_id"]),
                "pair_payload_digest": str(pair["pair_payload_digest"]),
                "target_profile_id": str(pair["target_profile_id"]),
                "candidate_result": candidate,
                "baseline_result": baseline,
                "pairwise_result": pairwise,
            }
        )

    metrics = _empty_metrics()
    metrics.update(_aggregate_deterministic(candidate_results))
    grounding_no_worse = [
        result.get("grounding_no_worse") is True
        for result in pairwise_results
        if "grounding_no_worse" in result
    ]
    naturalness_no_worse = [
        result.get("naturalness_no_worse") is True
        for result in pairwise_results
        if "naturalness_no_worse" in result
    ]
    relevance_no_worse = [
        result.get("relevance_no_worse") is True
        for result in pairwise_results
        if "relevance_no_worse" in result
    ]
    preferences = [
        result.get("resolved_preference") == "CANDIDATE"
        for result in pairwise_results
        if result.get("resolved_preference") in {"CANDIDATE", "BASELINE", "TIE"}
    ]
    agreement_values = [
        float(result["reviewer_agreement_rate"])
        for result in pairwise_results
        if result.get("reviewer_agreement_rate") is not None
    ]
    narrative_values = [
        float(result["narrative_coherence"])
        for result in pairwise_results
        if result.get("narrative_coherence") is not None
    ]
    metrics.update(
        {
            "narrative_coherence": (round(fmean(narrative_values), 6) if narrative_values else None),
            "human_grounding_no_worse_rate": _rate(grounding_no_worse),
            "human_naturalness_no_worse_rate": _rate(naturalness_no_worse),
            "human_relevance_no_worse_rate": _rate(relevance_no_worse),
            "candidate_preference_rate": _rate(preferences),
            "material_defect_count": sum(
                int(result.get("material_defect_count") or 0) for result in pairwise_results
            ),
            "reviewer_agreement_rate": (round(fmean(agreement_values), 6) if agreement_values else None),
        }
    )

    failures: list[str] = []
    unknown_reasons: list[str] = []
    if len(pairs) != EXPECTED_PAIR_COUNT:
        failures.append("SIX_AUTHORIZED_W9_PAIRS_REQUIRED")
    if bundle["generation_authorized"] is not True:
        failures.append("AUTHORIZED_VARIANT_GENERATION_MISSING")
    w6_status = str(bundle["official_w6_status"])
    if w6_status == "FAIL":
        failures.append("OFFICIAL_W6_NONPASS")
    elif w6_status != "PASS":
        unknown_reasons.append("official W6 status is not PASS")
    evidence = bundle["human_review_evidence"]
    human_review_satisfied = (
        evidence.get("status") == "PASS"
        and evidence.get("official_pass") is True
        and evidence.get("require_w9") is True
    )
    if not human_review_satisfied:
        unknown_reasons.append("official completed W9 human-review evidence is unavailable")
    for result in pairwise_results:
        failures.extend(result.get("failure_codes") or [])
        unknown_reasons.extend(result.get("unknown_reasons") or [])
    failures = sorted(set(failures))
    unknown_reasons = sorted(set(unknown_reasons))
    status = "UNKNOWN" if unknown_reasons else ("FAIL" if failures else "PASS")
    return seal_receipt(
        {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "evaluation_id": str(bundle["evaluation_id"]),
            "input_bundle_digest": str(bundle["bundle_digest"]),
            "human_review_evidence_digest": str(evidence["record_digest"]),
            "pair_ids": sorted(str(pair["pair_id"]) for pair in pairs),
            "pair_set_digest": pair_set_digest(pairs),
            "pair_count": len(pairs),
            "human_review_count": sum(len(pair["reviews"]) for pair in pairs),
            "adjudication_count": len(pairs),
            "official_w6_status": w6_status,
            "status": status,
            "whole_resume_release_pass": status == "PASS",
            "metrics": metrics,
            "pair_results": pair_results,
            "authority": {
                "classification": "CONDITIONALLY_RELEASE_AUTHORITATIVE",
                "human_review_required": True,
                "human_review_satisfied": human_review_satisfied,
                "release_authorizing": False,
                "feeds_w9_closeout": True,
                "promotion_scope": "future_runs_only",
                "current_run_authority_unchanged": True,
            },
            "failure_codes": failures,
            "unknown_reasons": unknown_reasons,
        }
    )


__all__ = ["evaluate_whole_resume"]
