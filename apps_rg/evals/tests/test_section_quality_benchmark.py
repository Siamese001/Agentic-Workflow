from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence

import pytest
import yaml
from jsonschema import Draft202012Validator

from apps_rg.evals.section_quality_benchmark.__main__ import main as benchmark_main
from apps_rg.evals.section_quality_benchmark.constants import (
    DIMENSIONS,
    INPUT_SCHEMA_VERSION,
    REVIEW_SCHEMA_VERSION,
    SECTION_IDS,
)
from apps_rg.evals.section_quality_benchmark.evaluation import evaluate_section_benchmark
from apps_rg.evals.section_quality_benchmark.reporting import report_digest_is_valid
from apps_rg.evals.section_quality_benchmark.validation import (
    load_rubrics,
    seal_input_bundle,
    seal_review_bundle,
)

EVALS_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = EVALS_ROOT / "section_quality_benchmark"
FIXTURE_PATH = BENCHMARK_ROOT / "fixtures" / "benchmark_controls.v1.json"
INPUT_SCHEMA_PATH = BENCHMARK_ROOT / "schemas" / "section_input.v1.schema.json"
REVIEW_SCHEMA_PATH = BENCHMARK_ROOT / "schemas" / "section_review.v1.schema.json"
REPORT_SCHEMA_PATH = BENCHMARK_ROOT / "schemas" / "section_report.v1.schema.json"
CONTRACT_PATH = EVALS_ROOT / "contracts" / "evaluation_contract.v2.yaml"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fixture() -> dict[str, Any]:
    return _json(FIXTURE_PATH)


def _input_bundle(*, excluded_sections: Sequence[str] = ()) -> dict[str, Any]:
    fixture = _fixture()
    cases = []
    for template in fixture["cases"]:
        if template["section_id"] in excluded_sections:
            continue
        candidate_id = f"artifact-{template['case_id']}-candidate"
        baseline_content = template["baseline_content"]
        cases.append(
            {
                "case_id": template["case_id"],
                "section_id": template["section_id"],
                "mode": template["mode"],
                "split": template["split"],
                "target_profile": fixture["target_profile"],
                "target_job_digest": fixture["target_job_digest"],
                "prompt_digest": fixture["prompt_digest"],
                "section_contract_ref": f"contract://{template['section_id']}/v1",
                "candidate": {
                    "artifact_id": candidate_id,
                    "content": template["candidate_content"],
                    "content_digest": "",
                    "grounding_status": "PASS",
                    "evidence_refs": [f"evidence://{template['case_id']}/candidate"],
                },
                "baseline": (
                    {
                        "artifact_id": f"artifact-{template['case_id']}-baseline",
                        "content": baseline_content,
                        "content_digest": "",
                        "grounding_status": "PASS",
                        "evidence_refs": [f"evidence://{template['case_id']}/baseline"],
                    }
                    if baseline_content is not None
                    else None
                ),
                "blinding": (
                    {
                        "candidate_variant": "VARIANT_A",
                        "baseline_variant": "VARIANT_B",
                        "variant_identity_hidden": True,
                        "blinding_digest": "",
                    }
                    if baseline_content is not None
                    else None
                ),
            }
        )
    return seal_input_bundle(
        {
            "schema_version": INPUT_SCHEMA_VERSION,
            "benchmark_id": fixture["benchmark_id"],
            "lane_cases": cases,
            "bundle_digest": "",
        }
    )


def _review_bundle(
    input_bundle: dict[str, Any],
    *,
    reviewer_classes: Sequence[str] = ("HUMAN", "MODEL_JUDGE"),
) -> dict[str, Any]:
    fixture = _fixture()
    reviews = []
    for case in input_bundle["lane_cases"]:
        for reviewer_class in reviewer_classes:
            dimension_scores = {
                dimension: {
                    "score": fixture["default_score"],
                    "reason": f"Controlled {dimension} assessment for {case['case_id']}.",
                    "evidence_refs": [case["candidate"]["artifact_id"]],
                }
                for dimension in DIMENSIONS
            }
            pairwise = case["mode"] == "PAIRWISE"
            reviews.append(
                {
                    "review_id": f"review-{case['case_id']}-{reviewer_class.lower()}",
                    "case_id": case["case_id"],
                    "section_id": case["section_id"],
                    "mode": case["mode"],
                    "candidate_content_digest": case["candidate"]["content_digest"],
                    "baseline_content_digest": (case["baseline"]["content_digest"] if pairwise else None),
                    "reviewer_class": reviewer_class,
                    "reviewer_identity_ref": f"reviewer://{reviewer_class.lower()}/control",
                    "rubric_id": "",
                    "rubric_digest": "",
                    "dimension_scores": dimension_scores,
                    "dimension_preferences": (
                        dict.fromkeys(DIMENSIONS, fixture["default_preference"]) if pairwise else None
                    ),
                    "overall_preference": fixture["default_preference"] if pairwise else "NOT_APPLICABLE",
                    "material_worse_dimensions": [],
                    "review_digest": "",
                }
            )
    return seal_review_bundle(
        {
            "schema_version": REVIEW_SCHEMA_VERSION,
            "benchmark_id": input_bundle["benchmark_id"],
            "input_bundle_digest": "",
            "reviews": reviews,
            "bundle_digest": "",
        },
        input_bundle,
    )


def _review_for(review_bundle: dict[str, Any], case_id: str, reviewer_class: str) -> dict[str, Any]:
    return next(
        review
        for review in review_bundle["reviews"]
        if review["case_id"] == case_id and review["reviewer_class"] == reviewer_class
    )


def test_versioned_schemas_accept_sealed_clean_control_and_report() -> None:
    input_bundle = _input_bundle()
    review_bundle = _review_bundle(input_bundle)
    report = evaluate_section_benchmark(input_bundle, review_bundle)

    for path, value in (
        (INPUT_SCHEMA_PATH, input_bundle),
        (REVIEW_SCHEMA_PATH, review_bundle),
        (REPORT_SCHEMA_PATH, report),
    ):
        schema = _json(path)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)


def test_rubrics_cover_all_five_lanes_and_cannot_authorize_release() -> None:
    rubrics = load_rubrics()

    assert tuple(rubrics) == SECTION_IDS
    assert all(tuple(rubric["required_dimensions"]) == DIMENSIONS for rubric in rubrics.values())
    assert all(rubric["authority"]["release_authorizing"] is False for rubric in rubrics.values())
    assert all(rubric["authority"]["promotion_scope"] == "future_runs_only" for rubric in rubrics.values())
    assert all(rubric["pairwise"]["variant_identity_hidden_required"] is True for rubric in rubrics.values())


def test_complete_five_lane_control_passes_without_release_authority() -> None:
    input_bundle = _input_bundle()
    report = evaluate_section_benchmark(input_bundle, _review_bundle(input_bundle))

    assert report["status"] == "PASS"
    assert report["complete_lane_count"] == 5
    assert {lane["status"] for lane in report["lane_results"].values()} == {"PASS"}
    assert report["authority"] == {
        "classification": "HUMAN_REVIEW",
        "human_reviews_present": True,
        "model_judge_results_advisory": True,
        "model_judge_calibrated_against_humans": False,
        "release_authorizing": False,
        "promotion_scope": "future_runs_only",
        "current_run_mutated": False,
    }
    assert report_digest_is_valid(report)
    first_review = report["lane_results"]["headline"]["case_results"][0]["review_results"][0]
    assert first_review["dimension_scores"]["evidence_fidelity"]["reason"]
    assert first_review["dimension_scores"]["evidence_fidelity"]["evidence_refs"]


def test_missing_lane_is_not_measured_and_partial_benchmark_cannot_pass() -> None:
    input_bundle = _input_bundle(excluded_sections=("ibm_bullets",))
    report = evaluate_section_benchmark(input_bundle, _review_bundle(input_bundle))

    assert report["status"] == "NOT_MEASURED"
    assert report["complete_lane_count"] == 4
    assert report["lane_results"]["ibm_bullets"]["status"] == "NOT_MEASURED"


def test_model_only_measurement_is_explicitly_advisory() -> None:
    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle, reviewer_classes=("MODEL_JUDGE",))
    report = evaluate_section_benchmark(input_bundle, reviews)

    assert report["status"] == "PASS"
    assert report["authority"]["classification"] == "MODEL_JUDGE_ADVISORY"
    assert report["authority"]["human_reviews_present"] is False
    assert report["authority"]["release_authorizing"] is False


def test_human_results_are_not_blended_with_model_judge_results() -> None:
    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle)
    model = _review_for(reviews, "headline-absolute", "MODEL_JUDGE")
    model["dimension_scores"]["naturalness"]["score"] = 1
    reviews = seal_review_bundle(reviews, input_bundle)
    report = evaluate_section_benchmark(input_bundle, reviews)
    headline = report["lane_results"]["headline"]

    assert headline["active_reviewer_class"] == "HUMAN"
    assert headline["status"] == "PASS"
    assert headline["metrics"]["naturalness"] == 4.0
    assert headline["reviewer_summaries"]["model_judge"]["dimension_means"]["naturalness"] == 1.0


@pytest.mark.parametrize("mutation_name", ("low_evidence_fidelity", "unsupported_language"))
def test_low_human_dimension_fails_named_dimension_without_blended_score(
    mutation_name: str,
) -> None:
    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle)
    mutation = _fixture()["mutations"][mutation_name]
    human = _review_for(reviews, "headline-absolute", "HUMAN")
    human["dimension_scores"][mutation["dimension"]]["score"] = mutation["score"]
    reviews = seal_review_bundle(reviews, input_bundle)
    report = evaluate_section_benchmark(input_bundle, reviews)

    assert report["status"] == "FAIL"
    assert mutation["expected_code"] in report["lane_results"]["headline"]["failure_codes"]
    assert "overall_score" not in report


def test_grounding_failure_cannot_be_overridden_by_quality_scores() -> None:
    input_bundle = _input_bundle()
    headline = next(case for case in input_bundle["lane_cases"] if case["section_id"] == "headline")
    headline["candidate"]["grounding_status"] = "FAIL"
    input_bundle = seal_input_bundle(input_bundle)
    reviews = _review_bundle(input_bundle)
    report = evaluate_section_benchmark(input_bundle, reviews)

    assert report["status"] == "FAIL"
    assert "CANDIDATE_GROUNDING_FAILED" in report["lane_results"]["headline"]["failure_codes"]


def test_unknown_grounding_is_unknown_never_pass() -> None:
    input_bundle = _input_bundle()
    headline = next(case for case in input_bundle["lane_cases"] if case["section_id"] == "headline")
    headline["candidate"]["grounding_status"] = "UNKNOWN"
    input_bundle = seal_input_bundle(input_bundle)
    report = evaluate_section_benchmark(input_bundle, _review_bundle(input_bundle))

    assert report["status"] == "UNKNOWN"
    assert report["lane_results"]["headline"]["status"] == "UNKNOWN"


def test_pairwise_critical_regression_fails_no_worse_requirement() -> None:
    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle)
    mutation = _fixture()["mutations"]["pairwise_critical_worse"]
    review = _review_for(reviews, "executive-summary-pairwise", "HUMAN")
    pairwise_case = next(
        case for case in input_bundle["lane_cases"] if case["case_id"] == "executive-summary-pairwise"
    )
    review["dimension_preferences"][mutation["dimension"]] = pairwise_case["blinding"]["baseline_variant"]
    review["material_worse_dimensions"] = [mutation["dimension"]]
    reviews = seal_review_bundle(reviews, input_bundle)
    report = evaluate_section_benchmark(input_bundle, reviews)

    assert report["status"] == "FAIL"
    assert mutation["expected_code"] in report["lane_results"]["executive_summary"]["failure_codes"]


def test_pairwise_candidate_preference_is_reported_separately() -> None:
    input_bundle = _input_bundle()
    pairwise_case = next(
        case for case in input_bundle["lane_cases"] if case["case_id"] == "executive-summary-pairwise"
    )
    pairwise_case["blinding"]["candidate_variant"] = "VARIANT_B"
    pairwise_case["blinding"]["baseline_variant"] = "VARIANT_A"
    input_bundle = seal_input_bundle(input_bundle)
    reviews = _review_bundle(input_bundle)
    review = _review_for(reviews, "executive-summary-pairwise", "HUMAN")
    candidate_variant = pairwise_case["blinding"]["candidate_variant"]
    review["overall_preference"] = candidate_variant
    review["dimension_preferences"] = dict.fromkeys(DIMENSIONS, candidate_variant)
    reviews = seal_review_bundle(reviews, input_bundle)
    report = evaluate_section_benchmark(input_bundle, reviews)
    summary = report["lane_results"]["executive_summary"]

    assert summary["status"] == "PASS"
    assert summary["metrics"]["candidate_preference_rate"] == 1.0
    assert summary["metrics"]["no_worse_rate"] == 1.0
    review_result = next(
        result
        for result in summary["case_results"][1]["review_results"]
        if result["reviewer_class"] == "HUMAN"
    )
    assert review_result["overall_preference"] == candidate_variant
    assert review_result["resolved_overall_preference"] == "CANDIDATE"


def test_pairwise_identity_must_remain_blinded() -> None:
    input_bundle = _input_bundle()
    pairwise_case = next(
        case for case in input_bundle["lane_cases"] if case["case_id"] == "executive-summary-pairwise"
    )
    pairwise_case["blinding"]["variant_identity_hidden"] = False
    input_bundle = seal_input_bundle(input_bundle)
    report = evaluate_section_benchmark(input_bundle, _review_bundle(_input_bundle()))

    assert report["status"] == "UNKNOWN"
    assert "PAIRWISE_VARIANT_IDENTITY_NOT_HIDDEN" in report["unknown_reasons"]


def test_missing_dimension_and_tampered_artifact_fail_closed_as_unknown() -> None:
    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle)
    review = _review_for(reviews, "headline-absolute", "HUMAN")
    review["dimension_scores"].pop("specificity")
    reviews = seal_review_bundle(reviews, input_bundle)
    missing_dimension = evaluate_section_benchmark(input_bundle, reviews)

    assert missing_dimension["status"] == "UNKNOWN"
    assert "DIMENSION_SCORE_SET_INCOMPLETE" in missing_dimension["unknown_reasons"]

    input_bundle = _input_bundle()
    input_bundle["lane_cases"][0]["candidate"]["content"] = "tampered after sealing"
    tampered = evaluate_section_benchmark(input_bundle, _review_bundle(_input_bundle()))
    assert tampered["status"] == "UNKNOWN"
    assert "CANDIDATE_CONTENT_DIGEST_INVALID" in tampered["unknown_reasons"]


def test_malformed_json_types_return_unknown_instead_of_raising() -> None:
    input_bundle = _input_bundle()
    input_bundle["lane_cases"][0]["mode"] = {"invalid": True}
    input_bundle = seal_input_bundle(input_bundle)
    malformed_input = evaluate_section_benchmark(input_bundle, _review_bundle(_input_bundle()))

    assert malformed_input["status"] == "UNKNOWN"
    assert "CASE_MODE_INVALID" in malformed_input["unknown_reasons"]

    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle)
    pairwise = _review_for(reviews, "executive-summary-pairwise", "HUMAN")
    pairwise["dimension_preferences"]["naturalness"] = {"invalid": True}
    reviews = seal_review_bundle(reviews, input_bundle)
    malformed_review = evaluate_section_benchmark(input_bundle, reviews)

    assert malformed_review["status"] == "UNKNOWN"
    assert "PAIRWISE_PREFERENCE_SET_INVALID" in malformed_review["unknown_reasons"]


def test_review_bundle_is_bound_to_exact_input_artifacts() -> None:
    original = _input_bundle()
    reviews = _review_bundle(original)
    changed = deepcopy(original)
    changed["lane_cases"][0]["candidate"]["grounding_status"] = "UNKNOWN"
    changed = seal_input_bundle(changed)
    report = evaluate_section_benchmark(changed, reviews)

    assert report["status"] == "UNKNOWN"
    assert "REVIEW_INPUT_BUNDLE_DIGEST_MISMATCH" in report["unknown_reasons"]


def test_absent_case_review_coverage_is_unknown() -> None:
    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle)
    reviews["reviews"] = [review for review in reviews["reviews"] if review["case_id"] != "headline-absolute"]
    reviews = seal_review_bundle(reviews, input_bundle)
    report = evaluate_section_benchmark(input_bundle, reviews)

    assert report["status"] == "UNKNOWN"
    assert report["lane_results"]["headline"]["active_reviewer_class"] == "NONE"


def test_every_emitted_g4_metric_maps_to_contract() -> None:
    input_bundle = _input_bundle()
    report = evaluate_section_benchmark(input_bundle, _review_bundle(input_bundle))
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    declared = {metric["name"] for metric in contract["gates"]["G4"]["metrics"]}
    emitted = {metric for lane in report["lane_results"].values() for metric in lane["metrics"]}

    assert emitted <= declared


def test_cli_round_trip_is_deterministic(tmp_path: Path, capsys: Any) -> None:
    input_bundle = _input_bundle()
    reviews = _review_bundle(input_bundle)
    input_path = tmp_path / "input.json"
    reviews_path = tmp_path / "reviews.json"
    output_path = tmp_path / "report.json"
    input_path.write_text(json.dumps(input_bundle), encoding="utf-8")
    reviews_path.write_text(json.dumps(reviews), encoding="utf-8")

    exit_code = benchmark_main(
        [
            "--input",
            str(input_path),
            "--reviews",
            str(reviews_path),
            "--output",
            str(output_path),
            "--compact",
        ]
    )
    stdout_report = json.loads(capsys.readouterr().out)
    file_report = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert stdout_report == file_report
    assert file_report == evaluate_section_benchmark(input_bundle, reviews)
