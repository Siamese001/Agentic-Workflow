"""Absolute and pairwise evaluation for sealed resume-section reviews."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from apps_rg.evals.section_quality_benchmark.constants import (
    DIMENSIONS,
    REPORT_SCHEMA_VERSION,
    SECTION_IDS,
)
from apps_rg.evals.section_quality_benchmark.reporting import seal_report
from apps_rg.evals.section_quality_benchmark.validation import (
    load_rubrics,
    validate_input_bundle,
    validate_review_bundle,
)


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _worst_status(statuses: Sequence[str]) -> str:
    if "FAIL" in statuses:
        return "FAIL"
    if "UNKNOWN" in statuses:
        return "UNKNOWN"
    if "NOT_MEASURED" in statuses:
        return "NOT_MEASURED"
    return "PASS"


def _empty_lane(section_id: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "status": status,
        "case_count": 0,
        "absolute_case_count": 0,
        "pairwise_case_count": 0,
        "active_reviewer_class": "NONE",
        "metrics": {},
        "reviewer_summaries": {
            "human": {"review_count": 0, "dimension_means": {}, "candidate_preference_rate": None},
            "model_judge": {
                "review_count": 0,
                "dimension_means": {},
                "candidate_preference_rate": None,
            },
        },
        "failure_codes": [],
        "unknown_reasons": [reason] if status == "UNKNOWN" else [],
        "not_measured_reasons": [reason] if status == "NOT_MEASURED" else [],
        "case_results": [],
    }


def _resolve_preference(value: str, case: Mapping[str, Any]) -> str:
    if value in {"TIE", "UNKNOWN"}:
        return value
    blinding = case["blinding"]
    if value == blinding["candidate_variant"]:
        return "CANDIDATE"
    if value == blinding["baseline_variant"]:
        return "BASELINE"
    return "UNKNOWN"


def _review_disposition(
    review: Mapping[str, Any], rubric: Mapping[str, Any], case: Mapping[str, Any]
) -> dict[str, Any]:
    minimum = float(rubric["minimum_score"])
    critical = set(rubric["critical_dimensions"])
    failure_codes = [
        f"DIMENSION_BELOW_MINIMUM_{dimension.upper()}"
        for dimension, result in review["dimension_scores"].items()
        if float(result["score"]) < minimum
    ]
    unknown_reasons: list[str] = []
    resolved_preferences = None
    resolved_overall_preference = review["overall_preference"]
    if review["mode"] == "PAIRWISE":
        preferences = review["dimension_preferences"]
        resolved_preferences = {
            dimension: _resolve_preference(preference, case) for dimension, preference in preferences.items()
        }
        resolved_overall_preference = _resolve_preference(review["overall_preference"], case)
        if resolved_overall_preference == "BASELINE":
            failure_codes.append("PAIRWISE_OVERALL_BASELINE_PREFERRED")
        elif resolved_overall_preference == "UNKNOWN":
            unknown_reasons.append("PAIRWISE_OVERALL_PREFERENCE_UNKNOWN")
        baseline_dimensions = {
            dimension for dimension, preference in resolved_preferences.items() if preference == "BASELINE"
        }
        if baseline_dimensions:
            failure_codes.append("PAIRWISE_DIMENSION_WORSE")
        if baseline_dimensions & critical:
            failure_codes.append("PAIRWISE_CRITICAL_DIMENSION_WORSE")
        if any(preference == "UNKNOWN" for preference in resolved_preferences.values()):
            unknown_reasons.append("PAIRWISE_DIMENSION_PREFERENCE_UNKNOWN")
        if review["material_worse_dimensions"]:
            failure_codes.append("PAIRWISE_MATERIAL_WORSE_DIMENSION")
    if failure_codes:
        status = "FAIL"
        unknown_reasons = []
    elif unknown_reasons:
        status = "UNKNOWN"
    else:
        status = "PASS"
    return {
        "review_id": review["review_id"],
        "reviewer_class": review["reviewer_class"],
        "reviewer_identity_ref": review["reviewer_identity_ref"],
        "rubric_id": review["rubric_id"],
        "rubric_digest": review["rubric_digest"],
        "status": status,
        "dimension_scores": review["dimension_scores"],
        "dimension_preferences": review["dimension_preferences"],
        "overall_preference": review["overall_preference"],
        "resolved_dimension_preferences": resolved_preferences,
        "resolved_overall_preference": resolved_overall_preference,
        "material_worse_dimensions": review["material_worse_dimensions"],
        "failure_codes": sorted(set(failure_codes)),
        "unknown_reasons": sorted(set(unknown_reasons)),
    }


def _evaluate_case(
    case: Mapping[str, Any],
    reviews: Sequence[Mapping[str, Any]],
    rubric: Mapping[str, Any],
    active_reviewer_class: str,
) -> dict[str, Any]:
    all_review_results = [_review_disposition(review, rubric, case) for review in reviews]
    active_results = [
        result for result in all_review_results if result["reviewer_class"] == active_reviewer_class
    ]
    failure_codes: list[str] = []
    unknown_reasons: list[str] = []
    candidate_grounding = case["candidate"]["grounding_status"]
    if candidate_grounding == "FAIL":
        failure_codes.append("CANDIDATE_GROUNDING_FAILED")
    elif candidate_grounding == "UNKNOWN":
        unknown_reasons.append("CANDIDATE_GROUNDING_UNKNOWN")
    if case["mode"] == "PAIRWISE":
        baseline_grounding = case["baseline"]["grounding_status"]
        if baseline_grounding != "PASS":
            unknown_reasons.append("BASELINE_GROUNDING_NONPASS")
    if active_reviewer_class == "NONE" or not active_results:
        unknown_reasons.append("ACTIVE_REVIEW_COVERAGE_MISSING")
    failure_codes.extend(code for result in active_results for code in result["failure_codes"])
    unknown_reasons.extend(reason for result in active_results for reason in result["unknown_reasons"])
    if failure_codes:
        status = "FAIL"
        unknown_reasons = []
    elif unknown_reasons:
        status = "UNKNOWN"
    else:
        status = "PASS"
    return {
        "case_id": case["case_id"],
        "section_id": case["section_id"],
        "mode": case["mode"],
        "split": case["split"],
        "candidate_artifact_id": case["candidate"]["artifact_id"],
        "candidate_content_digest": case["candidate"]["content_digest"],
        "baseline_artifact_id": (
            case["baseline"]["artifact_id"] if isinstance(case["baseline"], Mapping) else None
        ),
        "baseline_content_digest": (
            case["baseline"]["content_digest"] if isinstance(case["baseline"], Mapping) else None
        ),
        "active_reviewer_class": active_reviewer_class,
        "status": status,
        "failure_codes": sorted(set(failure_codes)),
        "unknown_reasons": sorted(set(unknown_reasons)),
        "review_results": all_review_results,
    }


def _reviewer_summary(
    reviews: Sequence[Mapping[str, Any]], cases_by_id: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    dimension_means = {
        dimension: _mean([float(review["dimension_scores"][dimension]["score"]) for review in reviews])
        for dimension in DIMENSIONS
    }
    pairwise = [review for review in reviews if review["mode"] == "PAIRWISE"]
    preference_rate = (
        sum(
            _resolve_preference(review["overall_preference"], cases_by_id[review["case_id"]]) == "CANDIDATE"
            for review in pairwise
        )
        / len(pairwise)
        if pairwise
        else None
    )
    return {
        "review_count": len(reviews),
        "dimension_means": dimension_means if reviews else {},
        "candidate_preference_rate": preference_rate,
    }


def _active_reviewer_class(
    cases: Sequence[Mapping[str, Any]], reviews_by_case: Mapping[str, Sequence[Mapping[str, Any]]]
) -> str:
    if all(
        any(review["reviewer_class"] == "HUMAN" for review in reviews_by_case[case["case_id"]])
        for case in cases
    ):
        return "HUMAN"
    if all(
        any(review["reviewer_class"] == "MODEL_JUDGE" for review in reviews_by_case[case["case_id"]])
        for case in cases
    ):
        return "MODEL_JUDGE"
    return "NONE"


def _lane_result(
    section_id: str,
    cases: Sequence[Mapping[str, Any]],
    reviews_by_case: Mapping[str, Sequence[Mapping[str, Any]]],
    rubric: Mapping[str, Any],
) -> dict[str, Any]:
    if not cases:
        return _empty_lane(section_id, "NOT_MEASURED", f"lane not supplied: {section_id}")
    active_class = _active_reviewer_class(cases, reviews_by_case)
    case_results = [
        _evaluate_case(case, reviews_by_case[case["case_id"]], rubric, active_class) for case in cases
    ]
    active_reviews = [
        review
        for case in cases
        for review in reviews_by_case[case["case_id"]]
        if review["reviewer_class"] == active_class
    ]
    human_reviews = [
        review
        for case in cases
        for review in reviews_by_case[case["case_id"]]
        if review["reviewer_class"] == "HUMAN"
    ]
    model_reviews = [
        review
        for case in cases
        for review in reviews_by_case[case["case_id"]]
        if review["reviewer_class"] == "MODEL_JUDGE"
    ]
    metrics = {
        dimension: _mean([float(review["dimension_scores"][dimension]["score"]) for review in active_reviews])
        for dimension in DIMENSIONS
    }
    pairwise_active = [review for review in active_reviews if review["mode"] == "PAIRWISE"]
    cases_by_id = {case["case_id"]: case for case in cases}
    metrics["candidate_preference_rate"] = (
        sum(
            _resolve_preference(review["overall_preference"], cases_by_id[review["case_id"]]) == "CANDIDATE"
            for review in pairwise_active
        )
        / len(pairwise_active)
        if pairwise_active
        else None
    )
    metrics["no_worse_rate"] = (
        sum(
            _resolve_preference(review["overall_preference"], cases_by_id[review["case_id"]])
            in {"CANDIDATE", "TIE"}
            and not review["material_worse_dimensions"]
            and all(
                _resolve_preference(preference, cases_by_id[review["case_id"]]) in {"CANDIDATE", "TIE"}
                for preference in review["dimension_preferences"].values()
            )
            for review in pairwise_active
        )
        / len(pairwise_active)
        if pairwise_active
        else None
    )
    failure_codes = sorted({code for case_result in case_results for code in case_result["failure_codes"]})
    unknown_reasons = sorted(
        {reason for case_result in case_results for reason in case_result["unknown_reasons"]}
    )
    status = _worst_status([result["status"] for result in case_results])
    return {
        "section_id": section_id,
        "status": status,
        "case_count": len(cases),
        "absolute_case_count": sum(case["mode"] == "ABSOLUTE" for case in cases),
        "pairwise_case_count": sum(case["mode"] == "PAIRWISE" for case in cases),
        "active_reviewer_class": active_class,
        "metrics": metrics,
        "reviewer_summaries": {
            "human": _reviewer_summary(human_reviews, cases_by_id),
            "model_judge": _reviewer_summary(model_reviews, cases_by_id),
        },
        "failure_codes": failure_codes,
        "unknown_reasons": unknown_reasons,
        "not_measured_reasons": [],
        "case_results": case_results,
    }


def _invalid_report(
    input_bundle: Any,
    reasons: Sequence[str],
) -> dict[str, Any]:
    benchmark_id = (
        str(input_bundle.get("benchmark_id", "invalid-section-quality-benchmark"))
        if isinstance(input_bundle, Mapping)
        else "invalid-section-quality-benchmark"
    )
    cases = input_bundle.get("lane_cases", []) if isinstance(input_bundle, Mapping) else []
    supplied = {
        case.get("section_id")
        for case in cases
        if isinstance(case, Mapping) and case.get("section_id") in SECTION_IDS
    }
    lanes = {
        section_id: _empty_lane(
            section_id,
            "UNKNOWN" if section_id in supplied else "NOT_MEASURED",
            "; ".join(reasons) if section_id in supplied else f"lane not supplied: {section_id}",
        )
        for section_id in SECTION_IDS
    }
    return seal_report(
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "benchmark_id": benchmark_id,
            "status": "UNKNOWN",
            "score_groups": ["section_quality"],
            "complete_lane_count": 0,
            "lane_results": lanes,
            "failure_codes": [],
            "unknown_reasons": sorted(set(reasons)),
            "not_measured_reasons": [
                f"lane not supplied: {section_id}" for section_id in SECTION_IDS if section_id not in supplied
            ],
            "authority": {
                "classification": "UNMEASURED",
                "human_reviews_present": False,
                "model_judge_results_advisory": True,
                "model_judge_calibrated_against_humans": False,
                "release_authorizing": False,
                "promotion_scope": "future_runs_only",
                "current_run_mutated": False,
            },
            "report_digest": "",
        }
    )


def evaluate_section_benchmark(
    input_bundle: Any,
    review_bundle: Any,
) -> dict[str, Any]:
    """Evaluate sealed section artifacts and completed reviews without running a judge."""

    input_reasons = validate_input_bundle(input_bundle)
    if input_reasons:
        return _invalid_report(input_bundle, input_reasons)
    rubrics = load_rubrics()
    review_reasons = validate_review_bundle(review_bundle, input_bundle, rubrics=rubrics)
    if review_reasons:
        return _invalid_report(input_bundle, review_reasons)

    cases_by_lane: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for case in input_bundle["lane_cases"]:
        cases_by_lane[case["section_id"]].append(case)
    reviews_by_case: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for review in review_bundle["reviews"]:
        reviews_by_case[review["case_id"]].append(review)
    lanes = {
        section_id: _lane_result(
            section_id,
            cases_by_lane[section_id],
            reviews_by_case,
            rubrics[section_id],
        )
        for section_id in SECTION_IDS
    }
    statuses = [lane["status"] for lane in lanes.values()]
    status = _worst_status(statuses)
    human_present = any(review["reviewer_class"] == "HUMAN" for review in review_bundle["reviews"])
    model_present = any(review["reviewer_class"] == "MODEL_JUDGE" for review in review_bundle["reviews"])
    measured_active_classes = {
        lane["active_reviewer_class"] for lane in lanes.values() if lane["case_count"] > 0
    }
    human_measurement_complete = measured_active_classes == {"HUMAN"}
    failure_codes = sorted({code for lane in lanes.values() for code in lane["failure_codes"]})
    unknown_reasons = sorted({reason for lane in lanes.values() for reason in lane["unknown_reasons"]})
    not_measured_reasons = sorted(
        {reason for lane in lanes.values() for reason in lane["not_measured_reasons"]}
    )
    return seal_report(
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "benchmark_id": input_bundle["benchmark_id"],
            "status": status,
            "score_groups": ["section_quality"],
            "complete_lane_count": sum(lane["status"] in {"PASS", "FAIL"} for lane in lanes.values()),
            "lane_results": lanes,
            "failure_codes": failure_codes,
            "unknown_reasons": unknown_reasons,
            "not_measured_reasons": not_measured_reasons,
            "authority": {
                "classification": (
                    "HUMAN_REVIEW"
                    if human_measurement_complete
                    else "MODEL_JUDGE_ADVISORY"
                    if model_present
                    else "UNMEASURED"
                ),
                "human_reviews_present": human_present,
                "model_judge_results_advisory": True,
                "model_judge_calibrated_against_humans": False,
                "release_authorizing": False,
                "promotion_scope": "future_runs_only",
                "current_run_mutated": False,
            },
            "report_digest": "",
        }
    )


__all__ = ["evaluate_section_benchmark"]
