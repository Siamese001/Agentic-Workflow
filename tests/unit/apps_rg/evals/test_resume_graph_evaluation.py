from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

import pytest
import yaml

from apps_rg.evals.c03_human_eval.split_policy import (
    PROOF_SPLIT_POLICY_ID,
    proof_split_for_digest,
)

from apps_rg.evals.resume_graph_evaluation import (
    INSUFFICIENT,
    PASS,
    UNKNOWN,
    brier_score,
    build_sanitized_ci_receipt,
    canonical_digest,
    compute_row_content_digest,
    evaluate_file,
    evaluate_rows,
    expected_calibration_error,
    fit_isotonic_pav,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
    report_digest_is_valid,
)
from ops_scripts.calibration.apps_rg_resume_graph_w6 import main
from ops_scripts.ci.check_apps_rg_resume_graph_w6 import validate_artifact


def _profile(tmp_path: Path | None = None) -> dict:
    dataset_path = str((tmp_path / "missing.jsonl") if tmp_path else Path("missing.jsonl"))
    output_path = str((tmp_path / "receipt.json") if tmp_path else Path("receipt.json"))
    protected_output_path = str(
        (tmp_path / "protected-full-report.json")
        if tmp_path
        else Path("protected-full-report.json")
    )
    return {
        "schema_version": "apps_rg.resume_graph_evaluation_profile.v1",
        "profile_id": "apps_rg::resume_graph_evaluation::test",
        "policy_version": "test_candidate_v1",
        "app_id": "apps_rg",
        "status": "candidate_unpromoted",
        "dataset": {
            "dataset_id": "apps_rg_c03_resume_graph_proof",
            "dataset_version": "v1",
            "dataset_path": dataset_path,
            "row_schema_version": "apps_rg.resume_graph_evaluation_row.v1",
            "proof_split_policy_id": PROOF_SPLIT_POLICY_ID,
            "required_label_source": "human_semantic_review",
            "minimum_total_samples": 4,
            "minimum_calibration_samples": 2,
            "minimum_holdout_samples": 2,
            "minimum_metric_binding_samples": 1,
            "require_two_reviewers": True,
            "require_adjudication_receipt": True,
            "require_leakage_check_pass": True,
            "require_both_proof_labels_per_split": True,
            "required_target_profiles": ["profile_a"],
            "required_sections": ["headline"],
        },
        "retrieval": {
            "k_values": [1, 3, 5, 10],
            "gate_k": 10,
            "primary_k": 10,
            "frontier_k": 2,
            "maximum_selected_audit_extras": 1,
            "allocator_candidate_budget": 64,
            "relevance_positive_floor": 2.0,
            "relevance_grade_minimum": 0.0,
            "relevance_grade_maximum": 3.0,
            "ndcg_gain": "exponential",
            "recall_definition": "micro_pooled_top_k_relevant_hits_over_all_relevant_candidates_in_the_complete_bounded_finite_universe",
        },
        "calibration": {
            "method": "deterministic_isotonic_pav_v1",
            "ece_bins": 10,
            "threshold_precision_floor": 0.9,
            "minimum_candidate_threshold": 0.9,
            "minimum_predicted_positive_count": 1,
            "active_threshold": None,
            "activation_status": "UNPROMOTED",
            "future_run_only": True,
        },
        "release_targets": {
            "recall_at_k_minimum": 0.95,
            "ndcg_at_k_minimum": 0.9,
            "mrr_minimum": None,
            "authority_eligibility_accuracy_minimum": 1.0,
            "exact_path_accuracy_minimum": 1.0,
            "claim_entailment_accuracy_minimum": 0.5,
            "metric_binding_accuracy_minimum": 0.95,
            "ece_maximum": 0.05,
            "proof_confidence_candidate_precision_minimum": 0.9,
            "proof_confidence_candidate_floor_minimum": 0.9,
            "proof_confidence_candidate_support_minimum": 1,
            "brier_maximum": None,
        },
        "output": {
            "protected_artifact_path": protected_output_path,
            "artifact_path": output_path,
            "artifact_schema_version": "apps_rg.resume_graph_w6_evaluation.v1",
            "ci_receipt_schema_version": "apps_rg.resume_graph_w6_ci_receipt.v1",
        },
    }


def _row(sample_id: str, split: str, proof_label: bool) -> dict:
    chosen = "candidate_relevant"
    row = {
        "schema_version": "apps_rg.resume_graph_evaluation_row.v1",
        "sample_id": sample_id,
        "dataset_id": "apps_rg_c03_resume_graph_proof",
        "dataset_version": "v1",
        "split": split,
        "target_profile_id": "profile_a",
        "authority_eligible": "PASS",
        "section_id": "headline",
        "claim_unit_id": f"claim::{sample_id}",
        "ranked_candidate_ids": [chosen, "candidate_other"],
        "relevance_labels": {chosen: 3, "candidate_other": 0},
        "selected_candidate_id": chosen,
        "predicted_path_ids": ["root", f"skill::{sample_id}", f"fact::{sample_id}"],
        "gold_path_ids": ["root", f"skill::{sample_id}", f"fact::{sample_id}"],
        "path_accuracy_label": True,
        "claim_entailment_prediction": proof_label,
        "claim_entailment_label": proof_label,
        "claim_entailment_grade": 3 if proof_label else 1,
        "target_relevance_grade": 3,
        "representation_mode": "CANONICAL_VISIBLE",
        "metric_binding_prediction": True,
        "metric_binding_label": True,
        "metric_binding_disposition": "EXACT",
        "metric_applicable": True,
        # Raw proof strength is deliberately not a probability-like value.
        "proof_score_raw": 1.3 if proof_label else -0.2,
        "proof_label": proof_label,
        # Global uniqueness can force a selection below the local best option.
        "selection_margin": -0.25 if sample_id.endswith("negative") else 0.25,
        "label_source": "human_semantic_review",
        "reviewer_refs": [f"review::{sample_id}::a", f"review::{sample_id}::b"],
        "adjudication_ref": f"adjudication::{sample_id}",
        "leakage_check_ref": f"leakage::{sample_id}",
        "leakage_check_status": "PASS",
        "label_policy": "human-proof-v1",
        "created_at": "2026-07-13T12:00:00Z",
        "graph_digest": "a" * 64,
        "policy_digest": "b" * 64,
        "allocation_plan_digest": "c" * 64,
    }
    row["content_digest"] = compute_row_content_digest(row)
    return row


def _valid_rows() -> list[dict]:
    return [
        _row("calibration-negative", "calibration", False),
        _row("calibration-positive", "calibration", True),
        _row("holdout-negative", "holdout", False),
        _row("holdout-positive", "holdout", True),
    ]


def _canonical_export_row(row: dict, *, with_retrieval: bool = True) -> dict:
    proof_split_group_nonce = 0
    while True:
        proof_split_group = canonical_digest(
            {
                "binding": row["predicted_path_ids"],
                "nonce": proof_split_group_nonce,
            }
        )
        if proof_split_for_digest(proof_split_group, salt=0) == row["split"]:
            break
        proof_split_group_nonce += 1
    proof_identity = canonical_digest(
        {
            "claim_unit_id": row["claim_unit_id"],
            "path": row["predicted_path_ids"],
        }
    )
    proof_reviewer_refs = ("human-reviewer://proof-a", "human-reviewer://proof-b")
    retrieval_reviewer_refs = (
        "human-reviewer://retrieval-a",
        "human-reviewer://retrieval-b",
    )
    export = {
        "schema_version": "apps_rg.c03_human_eval.adjudicated_evaluation.v1",
        "dataset_id": row["dataset_id"],
        "dataset_version": row["dataset_version"],
        "sample_id": row["sample_id"],
        "split": row["split"],
        "proof_split": row["split"],
        "retrieval_split": row["split"],
        "proof_identity_digest": proof_identity,
        "proof_split_group_digest": proof_split_group,
        "proof_split_policy_id": PROOF_SPLIT_POLICY_ID,
        "proof_split_policy_salt": 0,
        "target_profile_id": row["target_profile_id"],
        "case_id": f"case::{row['sample_id']}",
        "target_jd_digest": canonical_digest(
            {"kind": "jd", "sample_id": row["sample_id"]}
        ),
        "target_brief_digest": canonical_digest(
            {"kind": "brief", "sample_id": row["sample_id"]}
        ),
        "section_id": row["section_id"],
        "claim_unit_id": row["claim_unit_id"],
        "representation_mode": row["representation_mode"],
        "content_digest": "d" * 64,
        "label_source": row["label_source"],
        "human_score": float(row["proof_label"]),
        "authority_eligible": row["authority_eligible"],
        "claim_entailment_grade": row["claim_entailment_grade"],
        "path_accuracy": row["path_accuracy_label"],
        "metric_binding": "EXACT",
        "metric_applicable": True,
        "target_relevance_grade": 3,
        "overall_proof_valid": row["proof_label"],
        "reviewer_refs": [
            {
                "review_id": "review-a",
                "reviewer_id_hash": hashlib.sha256(
                    proof_reviewer_refs[0].encode("utf-8")
                ).hexdigest(),
                "reviewer_identity_ref": proof_reviewer_refs[0],
                "review_digest": "1" * 64,
            },
            {
                "review_id": "review-b",
                "reviewer_id_hash": hashlib.sha256(
                    proof_reviewer_refs[1].encode("utf-8")
                ).hexdigest(),
                "reviewer_identity_ref": proof_reviewer_refs[1],
                "review_digest": "2" * 64,
            },
        ],
        "adjudication_ref": {
            "adjudication_id": f"adjudication::{row['sample_id']}",
            "record_digest": "3" * 64,
        },
        "allocation_plan_digest": row["allocation_plan_digest"],
        "selected_candidate_id": row["selected_candidate_id"],
        "gold_path_ids": row["predicted_path_ids"],
        "gold_path_semantics": "system_selected_binding_human_validated",
        "proof_score_raw": row["proof_score_raw"],
        "system_prediction": {
            "claim_entailment_prediction": True,
            "metric_binding_prediction": True,
        },
        "selection_margin": row["selection_margin"],
        "system_fields": {},
        "retrieval_candidates": (
            [
                {
                    "candidate_id": candidate_id,
                    "rank": rank,
                    "selected": candidate_id == row["selected_candidate_id"],
                    "relevance_grade": row["relevance_labels"][candidate_id],
                    "path_valid": True,
                    "metric_binding": "EXACT",
                    "metric_applicable": True,
                    "system_fields": {},
                }
                for rank, candidate_id in enumerate(row["ranked_candidate_ids"], 1)
            ]
            if with_retrieval
            else None
        ),
        "retrieval_query_id": (
            f"query::{row['sample_id']}" if with_retrieval else None
        ),
        "retrieval_query_content_digest": (
            canonical_digest({"kind": "query", "sample_id": row["sample_id"]})
            if with_retrieval
            else None
        ),
        "candidate_universe_size": 2 if with_retrieval else None,
        "frontier_k": 2 if with_retrieval else None,
        "frontier_exhausted": True if with_retrieval else None,
        "judged_top_count": 2 if with_retrieval else None,
        "judged_candidate_count": 2 if with_retrieval else None,
        "candidate_judging_scope": (
            "FULL_FINITE_UNIVERSE" if with_retrieval else None
        ),
        "selected_audit_extra": None,
        "retrieval_recall_scope": (
            "FULL_FINITE_UNIVERSE" if with_retrieval else None
        ),
        "candidate_frontier_metadata": (
            {
                "raw_eligible_candidate_count": 2,
                "allocator_candidate_budget": 64,
                "allocator_budget_truncated": False,
                "candidate_universe_size": 2,
                "frontier_k": 2,
                "frontier_exhausted": True,
                "judged_top_count": 2,
                "judged_candidate_count": 2,
                "candidate_judging_scope": "FULL_FINITE_UNIVERSE",
                "selected_audit_extra_included": False,
                "selected_audit_extra_rank": None,
            }
            if with_retrieval
            else None
        ),
        "retrieval_reviewer_refs": (
            [
                {
                    "review_id": "retrieval-a",
                    "reviewer_id_hash": hashlib.sha256(
                        retrieval_reviewer_refs[0].encode("utf-8")
                    ).hexdigest(),
                    "reviewer_identity_ref": retrieval_reviewer_refs[0],
                    "review_digest": "4" * 64,
                },
                {
                    "review_id": "retrieval-b",
                    "reviewer_id_hash": hashlib.sha256(
                        retrieval_reviewer_refs[1].encode("utf-8")
                    ).hexdigest(),
                    "reviewer_identity_ref": retrieval_reviewer_refs[1],
                    "review_digest": "5" * 64,
                },
            ]
            if with_retrieval
            else []
        ),
        "retrieval_adjudication_ref": (
            {"adjudication_id": "retrieval-final", "record_digest": "6" * 64}
            if with_retrieval
            else None
        ),
        "graph_digest": row["graph_digest"],
        "policy_digest": row["policy_digest"],
        "label_policy": "c03_claim_proof_v1@sha256:" + "7" * 64,
        "created_at": row["created_at"],
        "leakage_check_ref": "artifact://sealed/leakage.json#sha256:" + "8" * 64,
        "leakage_check_status": "PASS",
    }
    export["record_digest"] = canonical_digest(export)
    return export


def _contains_key(value: object, target: str) -> bool:
    if isinstance(value, dict):
        return target in value or any(_contains_key(item, target) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, target) for item in value)
    return False


def _write_sanitized_receipt(
    directory: Path,
    report: dict,
    *,
    name: str = "ci-receipt.json",
) -> tuple[Path, str, str]:
    protected = directory / (name + ".protected")
    protected.write_text(
        json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    protected_sha = hashlib.sha256(protected.read_bytes()).hexdigest()
    receipt = build_sanitized_ci_receipt(
        report,
        protected_full_report_sha256=protected_sha,
    )
    artifact = directory / name
    artifact.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact, hashlib.sha256(artifact.read_bytes()).hexdigest(), protected_sha


def test_retrieval_metrics_have_conventional_deterministic_values() -> None:
    ranking = ["weak", "best"]
    relevance = {"best": 3.0, "weak": 1.0}
    assert recall_at_k(ranking, relevance, 1) == pytest.approx(0.5)
    assert recall_at_k(ranking, relevance, 1, positive_floor=2.0) == 0.0
    assert recall_at_k(ranking, relevance, 2, positive_floor=2.0) == 1.0
    expected_ndcg = (1.0 + 7.0 / math.log2(3.0)) / (7.0 + 1.0 / math.log2(3.0))
    assert ndcg_at_k(ranking, relevance, 2) == pytest.approx(expected_ndcg)
    assert reciprocal_rank(ranking, relevance, positive_floor=2.0) == pytest.approx(0.5)
    pooled = {**relevance, "selected-extra": 3.0}
    assert recall_at_k(ranking, pooled, 10, positive_floor=2.0) == pytest.approx(0.5)
    assert reciprocal_rank(
        ["weak", "selected-extra"],
        pooled,
        positive_floor=2.0,
        ranks=[1, 57],
    ) == pytest.approx(1.0 / 57.0)
    assert ndcg_at_k(
        ["weak", "selected-extra"],
        {"weak": 0.0, "selected-extra": 3.0},
        60,
        ranks=[1, 57],
    ) == pytest.approx(1.0 / math.log2(58.0))


def test_isotonic_fit_ece_and_brier_are_deterministic() -> None:
    model = fit_isotonic_pav([0.1, 0.2, 0.3, 0.4], [False, True, False, True])
    assert model.x_values == (0.1, 0.2, 0.3, 0.4)
    assert model.y_values == pytest.approx((0.0, 0.5, 0.5, 1.0))
    assert list(model.predict([0.15, 0.25, 0.35])) == pytest.approx([0.25, 0.5, 0.75])
    assert expected_calibration_error([0.0, 1.0], [False, True]) == 0.0
    assert expected_calibration_error([0.25, 0.75], [False, True]) == pytest.approx(0.25)
    assert brier_score([0.25, 0.75], [False, True]) == pytest.approx(0.0625)


def test_absent_human_dataset_is_unknown_null_and_contains_no_calibrated_confidence(
    tmp_path: Path,
) -> None:
    report = evaluate_file(tmp_path / "does-not-exist.jsonl", _profile())
    assert report["status"] == UNKNOWN
    assert report["unknown_is_pass"] is False
    assert report["evaluation_gate_pass"] is False
    assert report["promotion_eligible"] is False
    assert report["current_run_mutated"] is False
    assert all(value is None for value in report["metrics"].values())
    assert report["calibration"]["model"] is None
    assert report["calibration"]["candidate_threshold"] is None
    assert report["per_sample_results"] == []
    assert not _contains_key(report, "proof_confidence_calibrated")
    assert report_digest_is_valid(report)
    assert report == evaluate_file(tmp_path / "does-not-exist.jsonl", _profile())


def test_valid_human_splits_fit_only_calibration_and_score_holdout() -> None:
    rows = _valid_rows()
    report = evaluate_rows(
        rows, _profile(), source_ref="fixture.jsonl", allow_internal_rows=True
    )
    assert report["status"] == PASS
    assert report["evaluation_gate_pass"] is True
    assert report["promotion_eligible"] is False
    assert report["metrics"]["recall_at_k"] == 1.0
    assert report["metrics"]["recall_at_1"] == 1.0
    assert report["metrics"]["recall_at_3"] == 1.0
    assert report["metrics"]["recall_at_5"] == 1.0
    assert report["metrics"]["recall_at_10"] == 1.0
    assert report["metrics"]["ndcg_at_k"] == 1.0
    assert report["metrics"]["ndcg_at_10"] == 1.0
    assert report["metrics"]["mrr"] == 1.0
    assert report["metrics"]["exact_path_accuracy"] == 1.0
    assert report["metrics"]["selection_margin_minimum"] == -0.25
    assert report["metrics"]["ece"] == 0.0
    assert report["metrics"]["brier"] == 0.0
    assert report["calibration"]["fit_sample_count"] == 2
    assert report["calibration"]["holdout_sample_count"] == 2
    assert (
        report["calibration"]["candidate_threshold"]["selection_split"]
        == "proof_split:calibration"
    )
    assert report["calibration"]["active_threshold"] is None
    assert report["future_release_candidate_summary"]["precision"] == 1.0
    assert report["future_release_candidate_summary"]["support_count"] == 1
    assert report["future_release_candidate_summary"]["minimum_calibrated_confidence"] == 1.0
    assert report["future_release_candidate_summary"]["activation_status"] == "UNPROMOTED"
    assert len(report["per_sample_results"]) == 2
    assert all(row["split"] == "holdout" for row in report["per_sample_results"])
    assert all("proof_confidence_calibrated" in row for row in report["per_sample_results"])
    assert report_digest_is_valid(report)


def test_invalid_human_receipts_are_insufficient_and_suppress_calibrated_output() -> None:
    rows = _valid_rows()
    rows[0]["reviewer_refs"] = ["only-one-reviewer"]
    rows[0]["adjudication_ref"] = ""
    rows[0]["leakage_check_status"] = "FAIL"
    rows[0]["content_digest"] = compute_row_content_digest(rows[0])
    report = evaluate_rows(rows, _profile(), allow_internal_rows=True)
    assert report["status"] == INSUFFICIENT
    assert report["evaluation_gate_pass"] is False
    assert all(value is None for value in report["metrics"].values())
    assert not _contains_key(report, "proof_confidence_calibrated")
    assert any("reviewer_refs" in reason for reason in report["reasons"])
    assert any("adjudication_ref" in reason for reason in report["reasons"])
    assert any("leakage_check_status" in reason for reason in report["reasons"])


def test_row_order_does_not_change_report_or_digest() -> None:
    rows = _valid_rows()
    forward = evaluate_rows(
        rows, _profile(), source_ref="fixture.jsonl", allow_internal_rows=True
    )
    reverse = evaluate_rows(
        list(reversed(rows)),
        _profile(),
        source_ref="fixture.jsonl",
        allow_internal_rows=True,
    )
    assert forward == reverse


def test_holdout_labels_never_influence_fitted_model_or_candidate_threshold() -> None:
    baseline_rows = _valid_rows()
    changed_rows = copy.deepcopy(baseline_rows)
    for row in changed_rows:
        if row["split"] == "holdout":
            row["proof_label"] = not row["proof_label"]
            row["claim_entailment_label"] = row["proof_label"]
            row["claim_entailment_grade"] = 3 if row["proof_label"] else 1
            row["content_digest"] = compute_row_content_digest(row)
    baseline = evaluate_rows(baseline_rows, _profile(), allow_internal_rows=True)
    changed = evaluate_rows(changed_rows, _profile(), allow_internal_rows=True)
    assert baseline["calibration"]["model"] == changed["calibration"]["model"]
    assert (
        baseline["calibration"]["candidate_threshold"]
        == changed["calibration"]["candidate_threshold"]
    )
    assert baseline["metrics"]["brier"] != changed["metrics"]["brier"]


def test_target_relevance_is_reported_but_cannot_change_proof_or_release_gate() -> None:
    baseline_rows = [_canonical_export_row(row) for row in _valid_rows()]
    changed_rows = copy.deepcopy(baseline_rows)
    for row in changed_rows:
        if row["proof_split"] == "holdout":
            row["target_relevance_grade"] = 0
            row["record_digest"] = canonical_digest(
                {key: value for key, value in row.items() if key != "record_digest"}
            )
    baseline = evaluate_rows(baseline_rows, _profile())
    changed = evaluate_rows(changed_rows, _profile())
    assert baseline["status"] == changed["status"] == PASS
    assert baseline["gate_results"] == changed["gate_results"]
    assert baseline["calibration"] == changed["calibration"]
    assert baseline["metrics"]["target_relevance_mean_grade"] == 3.0
    assert changed["metrics"]["target_relevance_mean_grade"] == 0.0
    assert changed["target_relevance_summary"]["authoritative"] is False


def test_authority_failure_cannot_pass_via_inconsistent_overall_proof_label() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    for row in export_rows:
        row["authority_eligible"] = "FAIL"
        row["record_digest"] = canonical_digest(
            {key: value for key, value in row.items() if key != "record_digest"}
        )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert report["evaluation_gate_pass"] is False
    assert any(
        "proof_label:DISAGREES_WITH_FROZEN_PROOF_RUBRIC" in reason
        for reason in report["reasons"]
    )
    assert all(value is None for value in report["metrics"].values())


def test_authority_failure_is_a_hard_release_gate_even_with_consistent_negative_proof() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    target = next(
        row
        for row in export_rows
        if row["proof_split"] == "holdout" and row["overall_proof_valid"] is False
    )
    target["authority_eligible"] = "FAIL"
    target["record_digest"] = canonical_digest(
        {key: value for key, value in target.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] != PASS
    assert report["metrics"]["authority_eligibility_accuracy"] == 0.5
    assert (
        report["gate_results"]["authority_eligibility_accuracy_minimum"]["status"]
        == "FAIL"
    )


@pytest.mark.parametrize(
    ("metric_applicable", "metric_binding"),
    [(True, "NOT_APPLICABLE"), (False, "EXACT")],
)
def test_claim_metric_applicability_must_match_human_disposition(
    metric_applicable: bool,
    metric_binding: str,
) -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    target = export_rows[0]
    target["metric_applicable"] = metric_applicable
    target["metric_binding"] = metric_binding
    target["record_digest"] = canonical_digest(
        {key: value for key, value in target.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert any("metric_applicable" in reason for reason in report["reasons"])


@pytest.mark.parametrize(
    ("field", "value"),
    [("path_valid", False), ("metric_binding", "INEXACT")],
)
def test_retrieval_ineligible_candidate_cannot_be_forged_as_relevant(
    field: str,
    value: object,
) -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    candidate = export_rows[0]["retrieval_candidates"][0]
    candidate[field] = value
    candidate["relevance_grade"] = 3
    export_rows[0]["record_digest"] = canonical_digest(
        {
            key: item
            for key, item in export_rows[0].items()
            if key != "record_digest"
        }
    )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert any(
        "INELIGIBLE_CANDIDATE_MUST_HAVE_ZERO_RELEVANCE" in reason
        for reason in report["reasons"]
    )


@pytest.mark.parametrize(
    ("group_field", "reason"),
    [
        ("case_id", "RETRIEVAL_CASE_CROSSES_CALIBRATION_AND_HOLDOUT"),
        ("target_jd_digest", "TARGET_JD_CROSSES_CALIBRATION_AND_HOLDOUT"),
        ("target_brief_digest", "TARGET_BRIEF_CROSSES_CALIBRATION_AND_HOLDOUT"),
    ],
)
def test_retrieval_group_may_not_cross_calibration_and_holdout(
    group_field: str,
    reason: str,
) -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    shared_value = "shared-case" if group_field == "case_id" else "f" * 64
    for row in export_rows:
        row[group_field] = shared_value
        row["record_digest"] = canonical_digest(
            {key: value for key, value in row.items() if key != "record_digest"}
        )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert reason in report["reasons"]


def test_pooled_recall_is_micro_averaged_over_relevant_candidates() -> None:
    profile = _profile()
    profile["retrieval"].update(
        {"k_values": [1], "gate_k": 1, "primary_k": 1, "frontier_k": 3}
    )
    profile["release_targets"]["recall_at_k_minimum"] = 0.0
    profile["release_targets"]["ndcg_at_k_minimum"] = 0.0
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    for row in export_rows:
        row["retrieval_candidates"].append(
            {
                "candidate_id": "candidate-third",
                "rank": 3,
                "selected": False,
                "relevance_grade": 0,
                "path_valid": True,
                "metric_binding": "EXACT",
                "metric_applicable": True,
                "system_fields": {},
            }
        )
        row["candidate_universe_size"] = 3
        row["frontier_k"] = 3
        row["judged_top_count"] = 3
        row["judged_candidate_count"] = 3
        row["candidate_frontier_metadata"].update(
            {
                "raw_eligible_candidate_count": 3,
                "candidate_universe_size": 3,
                "frontier_k": 3,
                "judged_top_count": 3,
                "judged_candidate_count": 3,
            }
        )
        if row["proof_split"] == "holdout" and row["overall_proof_valid"] is True:
            row["retrieval_candidates"][1]["relevance_grade"] = 3
        row["record_digest"] = canonical_digest(
            {key: value for key, value in row.items() if key != "record_digest"}
        )
    report = evaluate_rows(export_rows, profile)
    assert report["metrics"]["recall_at_1"] == pytest.approx(0.75)
    assert report["metrics"]["pooled_recall_at_1"] == pytest.approx(2.0 / 3.0)
    assert report["metrics"]["recall_at_k"] == pytest.approx(2.0 / 3.0)


def test_canonical_packet_export_is_normalized_and_optional_retrieval_is_applicable_only() -> None:
    native_rows = _valid_rows()
    export_rows = [
        _canonical_export_row(row, with_retrieval=not row["sample_id"].endswith("negative"))
        for row in native_rows
    ]
    report = evaluate_rows(export_rows, _profile(), source_ref="sealed/export.jsonl")
    assert report["status"] == PASS
    assert report["dataset"]["sample_count"] == 4
    assert report["coverage"]["retrieval_total_count"] == 2
    assert report["coverage"]["retrieval_calibration_count"] == 1
    assert report["coverage"]["retrieval_holdout_count"] == 1
    assert report["metrics"]["recall_at_k"] == 1.0
    assert len(report["per_sample_results"]) == 2


def test_evaluator_rejects_profile_proof_split_policy_drift() -> None:
    profile = _profile()
    profile["dataset"]["proof_split_policy_id"] = (
        "c03-proof-identity-stratified-sha256-v1"
    )
    report = evaluate_rows(
        [_canonical_export_row(row) for row in _valid_rows()],
        profile,
    )
    assert report["status"] == INSUFFICIENT
    assert "PROFILE_PROOF_SPLIT_POLICY_ID_MISMATCH" in report["reasons"]


def test_proof_and_retrieval_holdouts_are_evaluated_on_their_own_split_domains() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    for row in export_rows:
        row["retrieval_split"] = (
            "holdout" if row["proof_split"] == "calibration" else "calibration"
        )
        row["record_digest"] = canonical_digest(
            {key: value for key, value in row.items() if key != "record_digest"}
        )
    report = evaluate_rows(export_rows, _profile(), source_ref="sealed/export.jsonl")
    assert report["status"] == PASS
    proof_holdout_ids = {row["sample_id"] for row in report["per_sample_results"]}
    retrieval_holdout_ids = {
        row["sample_id"] for row in report["retrieval_sample_results"]
    }
    assert proof_holdout_ids == {
        row["sample_id"] for row in export_rows if row["proof_split"] == "holdout"
    }
    assert retrieval_holdout_ids == {
        row["sample_id"] for row in export_rows if row["retrieval_split"] == "holdout"
    }
    assert proof_holdout_ids.isdisjoint(retrieval_holdout_ids)


def test_proof_identity_may_not_cross_calibration_and_holdout() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    export_rows[2]["proof_identity_digest"] = export_rows[0]["proof_identity_digest"]
    export_rows[2]["record_digest"] = canonical_digest(
        {key: value for key, value in export_rows[2].items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert "PROOF_IDENTITY_CROSSES_CALIBRATION_AND_HOLDOUT" in report["reasons"]
    assert all(value is None for value in report["metrics"].values())


def test_paraphrased_claims_with_the_same_binding_group_may_not_cross_splits() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    assert export_rows[0]["proof_identity_digest"] != export_rows[2][
        "proof_identity_digest"
    ]
    export_rows[2]["proof_split_group_digest"] = export_rows[0][
        "proof_split_group_digest"
    ]
    export_rows[2]["record_digest"] = canonical_digest(
        {key: value for key, value in export_rows[2].items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert (
        "PROOF_SPLIT_GROUP_CROSSES_CALIBRATION_AND_HOLDOUT"
        in report["reasons"]
    )


def test_sealed_export_rejects_mixed_salt_and_nondeterministic_proof_split() -> None:
    mixed_salt_rows = [_canonical_export_row(row) for row in _valid_rows()]
    mixed_salt_rows[0]["proof_split_policy_salt"] = 1
    mixed_salt_rows[0]["record_digest"] = canonical_digest(
        {key: value for key, value in mixed_salt_rows[0].items() if key != "record_digest"}
    )
    mixed = evaluate_rows(mixed_salt_rows, _profile())
    assert "MISSING_OR_MIXED_PROOF_SPLIT_POLICY_SALT" in mixed["reasons"]

    nondeterministic_rows = [_canonical_export_row(row) for row in _valid_rows()]
    row = nondeterministic_rows[0]
    row["proof_split"] = "holdout" if row["proof_split"] == "calibration" else "calibration"
    row["split"] = row["proof_split"]
    row["record_digest"] = canonical_digest(
        {key: value for key, value in row.items() if key != "record_digest"}
    )
    nondeterministic = evaluate_rows(nondeterministic_rows, _profile())
    assert "NONDETERMINISTIC_PROOF_SPLIT_ASSIGNMENT" in nondeterministic["reasons"]


def test_duplicate_proof_identities_have_equal_calibration_weight() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    duplicate = copy.deepcopy(export_rows[0])
    duplicate["sample_id"] = "duplicate-calibration-negative"
    duplicate["representation_mode"] = "DERIVED_ALTERNATIVE"
    duplicate["selected_candidate_id"] = "derived:narrative:container"
    duplicate["retrieval_candidates"] = None
    duplicate["retrieval_query_id"] = None
    duplicate["retrieval_query_content_digest"] = None
    duplicate["candidate_universe_size"] = None
    duplicate["frontier_k"] = None
    duplicate["frontier_exhausted"] = None
    duplicate["judged_top_count"] = None
    duplicate["judged_candidate_count"] = None
    duplicate["candidate_judging_scope"] = None
    duplicate["selected_audit_extra"] = None
    duplicate["retrieval_recall_scope"] = None
    duplicate["candidate_frontier_metadata"] = None
    duplicate["retrieval_reviewer_refs"] = []
    duplicate["retrieval_adjudication_ref"] = None
    duplicate["record_digest"] = canonical_digest(
        {key: value for key, value in duplicate.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows + [duplicate], _profile())
    assert report["status"] == PASS
    assert report["calibration"]["fit_row_count"] == 3
    assert report["calibration"]["fit_sample_count"] == 2
    assert report["coverage"]["proof_calibration_identity_count"] == 2


def test_derived_duplicates_cannot_inflate_applicable_metric_support() -> None:
    profile = _profile()
    profile["dataset"]["minimum_metric_binding_samples"] = 3
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    duplicate = copy.deepcopy(export_rows[-1])
    duplicate["sample_id"] = "derived-holdout-metric-duplicate"
    duplicate["representation_mode"] = "DERIVED_ALTERNATIVE"
    duplicate["retrieval_candidates"] = None
    for field in (
        "retrieval_query_id",
        "retrieval_query_content_digest",
        "candidate_universe_size",
        "frontier_k",
        "frontier_exhausted",
        "judged_top_count",
        "judged_candidate_count",
        "candidate_judging_scope",
        "selected_audit_extra",
        "retrieval_recall_scope",
        "candidate_frontier_metadata",
        "retrieval_adjudication_ref",
    ):
        duplicate[field] = None
    duplicate["retrieval_reviewer_refs"] = []
    duplicate["record_digest"] = canonical_digest(
        {key: value for key, value in duplicate.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows + [duplicate], profile)
    assert report["status"] == INSUFFICIENT
    assert "METRIC_BINDING_HOLDOUT_COUNT_BELOW_MINIMUM:2<3" in report["reasons"]


def test_canonical_visible_representation_wins_when_derived_duplicate_sorts_first() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    canonical = next(
        row
        for row in export_rows
        if row["proof_split"] == "holdout" and row["overall_proof_valid"] is True
    )
    derived = copy.deepcopy(canonical)
    derived["sample_id"] = "000-derived-sorts-first"
    derived["representation_mode"] = "DERIVED_ALTERNATIVE"
    derived["selected_candidate_id"] = "derived:narrative:container"
    derived["retrieval_candidates"] = None
    derived["retrieval_query_id"] = None
    derived["retrieval_query_content_digest"] = None
    derived["candidate_frontier_metadata"] = None
    derived["candidate_universe_size"] = None
    derived["frontier_k"] = None
    derived["frontier_exhausted"] = None
    derived["judged_top_count"] = None
    derived["judged_candidate_count"] = None
    derived["candidate_judging_scope"] = None
    derived["selected_audit_extra"] = None
    derived["retrieval_recall_scope"] = None
    derived["retrieval_reviewer_refs"] = []
    derived["retrieval_adjudication_ref"] = None
    derived["record_digest"] = canonical_digest(
        {key: value for key, value in derived.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows + [derived], _profile())
    assert report["status"] == PASS
    assert report["calibration"]["holdout_sample_count"] == 2
    assert report["calibration"]["holdout_row_count"] == 3
    assert report["future_release_candidate_summary"]["support_count"] == 1


def test_inconsistent_duplicate_proof_identity_is_insufficient() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    duplicate = copy.deepcopy(export_rows[0])
    duplicate["sample_id"] = "inconsistent-duplicate"
    duplicate["proof_score_raw"] = 99.0
    duplicate["record_digest"] = canonical_digest(
        {key: value for key, value in duplicate.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows + [duplicate], _profile())
    assert report["status"] == INSUFFICIENT
    assert (
        "DUPLICATE_PROOF_IDENTITY_HAS_INCONSISTENT_SCORE_LABEL_OR_BINDING"
        in report["reasons"]
    )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        (
            "authority_eligible",
            "FAIL",
            "DUPLICATE_PROOF_IDENTITY_HAS_INCONSISTENT_SCORE_LABEL_OR_BINDING",
        ),
        (
            "target_relevance_grade",
            0,
            "DUPLICATE_PROOF_CONTEXT_HAS_INCONSISTENT_TARGET_OR_PREDICTION_FIELDS",
        ),
    ],
)
def test_duplicate_proof_identity_cannot_contradict_any_human_dimension(
    field: str,
    value: object,
    reason: str,
) -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    duplicate = copy.deepcopy(export_rows[1])
    duplicate["sample_id"] = f"contradictory-{field}"
    duplicate[field] = value
    duplicate["record_digest"] = canonical_digest(
        {key: item for key, item in duplicate.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows + [duplicate], _profile())
    assert report["status"] == INSUFFICIENT
    assert reason in report["reasons"]


def test_relevant_candidate_below_k_remains_in_full_universe_recall_denominator() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    target = next(
        row
        for row in export_rows
        if row["proof_split"] == "holdout" and row["overall_proof_valid"] is True
    )
    for candidate in target["retrieval_candidates"]:
        candidate["selected"] = False
        candidate["relevance_grade"] = 0
    target["selected_candidate_id"] = "selected-outside-top-k"
    target["candidate_universe_size"] = 57
    target["frontier_exhausted"] = False
    target["judged_candidate_count"] = 57
    target["candidate_judging_scope"] = "FULL_FINITE_UNIVERSE"
    target["selected_audit_extra"] = {
        "candidate_id": "selected-outside-top-k",
        "rank": 57,
    }
    target["retrieval_recall_scope"] = "FULL_FINITE_UNIVERSE"
    target["candidate_frontier_metadata"].update(
        {
            "raw_eligible_candidate_count": 57,
            "candidate_universe_size": 57,
            "frontier_exhausted": False,
            "judged_candidate_count": 57,
            "candidate_judging_scope": "FULL_FINITE_UNIVERSE",
            "selected_audit_extra_included": True,
            "selected_audit_extra_rank": 57,
        }
    )
    target["retrieval_candidates"].extend(
        [
            {
                "candidate_id": (
                    "selected-outside-top-k" if rank == 57 else f"candidate-{rank}"
                ),
                "rank": rank,
                "selected": rank == 57,
                "relevance_grade": 3 if rank == 57 else 0,
                "path_valid": True,
                "metric_binding": "EXACT",
                "metric_applicable": True,
                "system_fields": {},
            }
            for rank in range(3, 58)
        ]
    )
    target["record_digest"] = canonical_digest(
        {key: value for key, value in target.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows, _profile())
    retrieval_result = next(
        row
        for row in report["retrieval_sample_results"]
        if row["sample_id"] == target["sample_id"]
    )
    assert retrieval_result["recall_at_k"] == 0.0
    assert retrieval_result["reciprocal_rank"] == pytest.approx(1.0 / 57.0)


def test_exhausted_eight_candidate_universe_requires_no_padding() -> None:
    profile = _profile()
    profile["retrieval"]["frontier_k"] = 10
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    for row in export_rows:
        selected = row["selected_candidate_id"]
        row["retrieval_candidates"] = [
            {
                "candidate_id": selected if rank == 1 else f"candidate-{rank}",
                "rank": rank,
                "selected": rank == 1,
                "relevance_grade": 3 if rank == 1 else 0,
                "path_valid": True,
                "metric_binding": "EXACT",
                "metric_applicable": True,
                "system_fields": {},
            }
            for rank in range(1, 9)
        ]
        row["candidate_universe_size"] = 8
        row["frontier_k"] = 10
        row["frontier_exhausted"] = True
        row["judged_top_count"] = 8
        row["judged_candidate_count"] = 8
        row["selected_audit_extra"] = None
        row["retrieval_recall_scope"] = "FULL_FINITE_UNIVERSE"
        row["candidate_frontier_metadata"].update(
            {
                "raw_eligible_candidate_count": 8,
                "candidate_universe_size": 8,
                "frontier_k": 10,
                "frontier_exhausted": True,
                "judged_top_count": 8,
                "judged_candidate_count": 8,
            }
        )
        row["record_digest"] = canonical_digest(
            {key: value for key, value in row.items() if key != "record_digest"}
        )
    report = evaluate_rows(export_rows, profile)
    assert report["status"] == PASS
    assert report["metrics"]["pooled_recall_at_10"] == 1.0

    export_rows[0]["retrieval_candidates"].pop()
    export_rows[0]["record_digest"] = canonical_digest(
        {key: value for key, value in export_rows[0].items() if key != "record_digest"}
    )
    missing_rank = evaluate_rows(export_rows, profile)
    assert missing_rank["status"] == INSUFFICIENT
    assert any("MISSING_REQUIRED_RANK:8" in reason for reason in missing_rank["reasons"])


def test_production_file_rejects_handcrafted_internal_rows(tmp_path: Path) -> None:
    dataset = tmp_path / "handcrafted.jsonl"
    dataset.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in _valid_rows()),
        encoding="utf-8",
    )
    report = evaluate_file(dataset, _profile())
    assert report["status"] == INSUFFICIENT
    assert all(value is None for value in report["metrics"].values())
    assert not _contains_key(report, "proof_confidence_calibrated")
    assert any(
        "OFFICIAL_EVIDENCE_CHAIN_REQUIRED" in reason for reason in report["reasons"]
    )


def test_self_consistent_sealed_jsonl_cannot_self_authorize_official_pass(
    tmp_path: Path,
) -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    dataset = tmp_path / "self-consistent-forgery.jsonl"
    dataset.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in export_rows),
        encoding="utf-8",
    )
    report = evaluate_file(dataset, _profile())
    assert report["status"] == INSUFFICIENT
    assert report["official_evidence_chain_validated"] is False
    assert any(
        "OFFICIAL_EVIDENCE_CHAIN_REQUIRED" in reason for reason in report["reasons"]
    )


def test_official_evaluator_rejects_dataset_symlink_before_reading(
    tmp_path: Path,
) -> None:
    actual = tmp_path / "actual-dataset.jsonl"
    actual.write_text(
        "".join(
            json.dumps(row, sort_keys=True) + "\n"
            for row in [_canonical_export_row(row) for row in _valid_rows()]
        ),
        encoding="utf-8",
    )
    actual.chmod(0o600)
    alias = tmp_path / "dataset-alias.jsonl"
    alias.symlink_to(actual)
    report = evaluate_file(alias, _profile())
    assert report["status"] == INSUFFICIENT
    assert "DATASET_PRIVACY_INVALID:must not be a symlink" in report["reasons"]


def _dummy_official_inputs(tmp_path: Path) -> dict[str, Path]:
    controlled = tmp_path / "controlled"
    controlled.mkdir(mode=0o700)
    dataset = controlled / "dataset.jsonl"
    dataset.write_text("{}\n", encoding="utf-8")
    receipt = controlled / "export-receipt.json"
    receipt.write_text("{}\n", encoding="utf-8")
    authority = controlled / "authority-receipt.json"
    authority.write_text("{}\n", encoding="utf-8")
    for path in (dataset, receipt, authority):
        path.chmod(0o600)
    packet = controlled / "packet"
    labels = controlled / "labels"
    packet.mkdir(mode=0o700)
    labels.mkdir(mode=0o700)
    return {
        "dataset": dataset,
        "export_receipt": receipt,
        "authority_receipt": authority,
        "packet": packet,
        "labels": labels,
    }


def _evaluate_dummy_official_inputs(inputs: dict[str, Path]) -> dict:
    return evaluate_file(
        inputs["dataset"],
        _profile(),
        export_receipt_path=inputs["export_receipt"],
        trusted_export_receipt_sha256=hashlib.sha256(
            inputs["export_receipt"].read_bytes()
        ).hexdigest(),
        trusted_prelabel_packet_manifest_sha256="a" * 64,
        human_review_authority_receipt_path=inputs["authority_receipt"],
        trusted_human_review_authority_receipt_sha256=hashlib.sha256(
            inputs["authority_receipt"].read_bytes()
        ).hexdigest(),
        packet_dir=inputs["packet"],
        labels_dir=inputs["labels"],
    )


@pytest.mark.parametrize(
    ("controlled_input", "reason_prefix"),
    [
        ("dataset", "DATASET_CONTROL_BOUNDARY_INVALID"),
        ("export_receipt", "TRUSTED_EXPORT_RECEIPT_CONTROL_BOUNDARY_INVALID"),
        (
            "authority_receipt",
            "HUMAN_REVIEW_AUTHORITY_RECEIPT_CONTROL_BOUNDARY_INVALID",
        ),
        ("packet", "PACKET_ROOT_CONTROL_BOUNDARY_INVALID"),
        ("labels", "LABELS_ROOT_CONTROL_BOUNDARY_INVALID"),
    ],
)
def test_official_evaluator_rejects_controlled_inputs_inside_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    controlled_input: str,
    reason_prefix: str,
) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir(mode=0o700)
    monkeypatch.setattr(
        "apps_rg.evals.resume_graph_evaluation.repo_root_from_module",
        lambda: checkout,
    )
    inputs = _dummy_official_inputs(tmp_path)
    destination = checkout / inputs[controlled_input].name
    inputs[controlled_input].rename(destination)
    inputs[controlled_input] = destination
    report = _evaluate_dummy_official_inputs(inputs)
    assert report["status"] == INSUFFICIENT
    assert any(reason.startswith(reason_prefix) for reason in report["reasons"])


@pytest.mark.parametrize(
    ("controlled_input", "reason_prefix"),
    [
        ("dataset", "DATASET_CONTROL_BOUNDARY_INVALID"),
        ("export_receipt", "TRUSTED_EXPORT_RECEIPT_CONTROL_BOUNDARY_INVALID"),
        (
            "authority_receipt",
            "HUMAN_REVIEW_AUTHORITY_RECEIPT_CONTROL_BOUNDARY_INVALID",
        ),
        ("packet", "PACKET_ROOT_CONTROL_BOUNDARY_INVALID"),
        ("labels", "LABELS_ROOT_CONTROL_BOUNDARY_INVALID"),
    ],
)
def test_official_evaluator_rejects_controlled_input_ancestor_symlinks(
    tmp_path: Path,
    controlled_input: str,
    reason_prefix: str,
) -> None:
    inputs = _dummy_official_inputs(tmp_path)
    controlled = tmp_path / "controlled"
    alias = tmp_path / "controlled-alias"
    alias.symlink_to(controlled, target_is_directory=True)
    inputs[controlled_input] = alias / inputs[controlled_input].relative_to(controlled)
    report = _evaluate_dummy_official_inputs(inputs)
    assert report["status"] == INSUFFICIENT
    assert any(reason.startswith(reason_prefix) for reason in report["reasons"])


@pytest.mark.parametrize(
    ("controlled_input", "reason_prefix"),
    [
        ("dataset", "DATASET_UNREADABLE"),
        ("export_receipt", "TRUSTED_EXPORT_RECEIPT_CONTROL_BOUNDARY_INVALID"),
        (
            "authority_receipt",
            "HUMAN_REVIEW_AUTHORITY_RECEIPT_CONTROL_BOUNDARY_INVALID",
        ),
        ("packet", "PACKET_ROOT_MEMBER_CONTROL_BOUNDARY_INVALID"),
        ("labels", "LABELS_ROOT_MEMBER_CONTROL_BOUNDARY_INVALID"),
    ],
)
def test_official_evaluator_rejects_hardlinked_controlled_input_inodes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    controlled_input: str,
    reason_prefix: str,
) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir(mode=0o700)
    monkeypatch.setattr(
        "apps_rg.evals.resume_graph_evaluation.repo_root_from_module",
        lambda: checkout,
    )
    inputs = _dummy_official_inputs(tmp_path)
    target = inputs[controlled_input]
    if target.is_dir():
        target = target / "controlled-member.json"
        target.write_text("{}\n", encoding="utf-8")
        target.chmod(0o600)
    __import__("os").link(target, checkout / f"{controlled_input}-hardlink")
    report = _evaluate_dummy_official_inputs(inputs)
    assert report["status"] == INSUFFICIENT
    assert any(reason.startswith(reason_prefix) for reason in report["reasons"])


@pytest.mark.parametrize(
    ("aliased_input", "reason_fragment"),
    [
        ("export_receipt", "TRUSTED_EXPORT_RECEIPT_CONTROL_BOUNDARY_INVALID"),
        (
            "authority_receipt",
            "HUMAN_REVIEW_AUTHORITY_RECEIPT_CONTROL_BOUNDARY_INVALID",
        ),
        ("packet", "PACKET_ROOT_CONTROL_BOUNDARY_INVALID"),
        ("labels", "LABELS_ROOT_CONTROL_BOUNDARY_INVALID"),
    ],
)
def test_official_evaluator_rejects_controlled_root_symlink_before_resolve(
    tmp_path: Path,
    aliased_input: str,
    reason_fragment: str,
) -> None:
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        "".join(
            json.dumps(row, sort_keys=True) + "\n"
            for row in [_canonical_export_row(row) for row in _valid_rows()]
        ),
        encoding="utf-8",
    )
    dataset.chmod(0o600)
    receipt = tmp_path / "export-receipt.json"
    receipt.write_text("{}\n", encoding="utf-8")
    receipt.chmod(0o600)
    authority_receipt = tmp_path / "authority-receipt.json"
    authority_receipt.write_text("{}\n", encoding="utf-8")
    authority_receipt.chmod(0o600)
    packet = tmp_path / "packet"
    labels = tmp_path / "labels"
    packet.mkdir(mode=0o700)
    labels.mkdir(mode=0o700)

    inputs = {
        "export_receipt": receipt,
        "authority_receipt": authority_receipt,
        "packet": packet,
        "labels": labels,
    }
    target = inputs[aliased_input]
    alias = tmp_path / f"{aliased_input}-alias"
    alias.symlink_to(target, target_is_directory=target.is_dir())
    inputs[aliased_input] = alias
    report = evaluate_file(
        dataset,
        _profile(),
        export_receipt_path=inputs["export_receipt"],
        trusted_export_receipt_sha256=hashlib.sha256(
            receipt.read_bytes()
        ).hexdigest(),
        trusted_prelabel_packet_manifest_sha256="a" * 64,
        human_review_authority_receipt_path=inputs["authority_receipt"],
        trusted_human_review_authority_receipt_sha256=hashlib.sha256(
            authority_receipt.read_bytes()
        ).hexdigest(),
        packet_dir=inputs["packet"],
        labels_dir=inputs["labels"],
    )
    assert report["status"] == INSUFFICIENT
    assert any(reason_fragment in reason for reason in report["reasons"])


def test_malformed_sealed_export_emits_insufficient_receipt_instead_of_raising(
    tmp_path: Path,
) -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    export_rows[0]["retrieval_candidates"][0]["rank"] = "not-an-integer"
    export_rows[0]["record_digest"] = canonical_digest(
        {key: value for key, value in export_rows[0].items() if key != "record_digest"}
    )
    dataset = tmp_path / "malformed-sealed.jsonl"
    dataset.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in export_rows),
        encoding="utf-8",
    )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert all(value is None for value in report["metrics"].values())
    assert not _contains_key(report, "proof_confidence_calibrated")
    assert any("INVALID_RANK" in reason for reason in report["reasons"])


@pytest.mark.parametrize(
    ("ref_field", "identity_field", "reason_fragment"),
    [
        ("reviewer_refs", "reviewer_id_hash", "INVALID_HUMAN_REVIEW_RECEIPTS"),
        ("retrieval_reviewer_refs", "review_digest", "INVALID_RECEIPTS"),
    ],
)
def test_sealed_export_rejects_non_distinct_human_review_receipts(
    ref_field: str,
    identity_field: str,
    reason_fragment: str,
) -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    tampered = export_rows[0]
    tampered[ref_field][1][identity_field] = tampered[ref_field][0][identity_field]
    tampered["record_digest"] = canonical_digest(
        {key: value for key, value in tampered.items() if key != "record_digest"}
    )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert any(reason_fragment in reason for reason in report["reasons"])
    assert all(value is None for value in report["metrics"].values())


def test_evaluator_rejects_proof_retrieval_reviewer_cohort_overlap() -> None:
    export_rows = [_canonical_export_row(row) for row in _valid_rows()]
    for row in export_rows:
        proof_reviewer = row["reviewer_refs"][0]
        row["retrieval_reviewer_refs"][0]["reviewer_id_hash"] = proof_reviewer[
            "reviewer_id_hash"
        ]
        row["retrieval_reviewer_refs"][0]["reviewer_identity_ref"] = proof_reviewer[
            "reviewer_identity_ref"
        ]
        row["record_digest"] = canonical_digest(
            {key: value for key, value in row.items() if key != "record_digest"}
        )
    report = evaluate_rows(export_rows, _profile())
    assert report["status"] == INSUFFICIENT
    assert "PROOF_RETRIEVAL_REVIEWER_HASH_COHORTS_OVERLAP" in report["reasons"]
    assert (
        "PROOF_RETRIEVAL_REVIEWER_IDENTITY_REF_COHORTS_OVERLAP"
        in report["reasons"]
    )


def test_cli_materializes_prelabel_unknown_receipt_and_returns_nonpass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    profile = _profile(tmp_path)
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=True), encoding="utf-8")
    output_path = Path(profile["output"]["artifact_path"])
    protected_path = Path(profile["output"]["protected_artifact_path"])

    assert main(["--profile", str(profile_path)]) == 2
    receipt = json.loads(output_path.read_text(encoding="utf-8"))
    assert receipt["status"] == UNKNOWN
    assert receipt["evaluation_gate_pass"] is False
    assert receipt["promotion_eligible"] is False
    assert all(value is None for value in receipt["metrics"].values())
    assert not _contains_key(receipt, "proof_confidence_calibrated")
    assert receipt["record_digest"] == canonical_digest(
        {key: value for key, value in receipt.items() if key != "record_digest"}
    )
    protected = json.loads(protected_path.read_text(encoding="utf-8"))
    assert report_digest_is_valid(protected)
    assert validate_artifact(output_path) == ["W6 evaluation disposition is nonpass: UNKNOWN"]
    assert json.loads(capsys.readouterr().out)["status"] == UNKNOWN


def test_cli_protected_report_is_owner_only_under_permissive_umask(
    tmp_path: Path,
) -> None:
    profile = _profile(tmp_path)
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=True), encoding="utf-8")
    previous_umask = __import__("os").umask(0o022)
    try:
        assert main(["--profile", str(profile_path)]) == 2
    finally:
        __import__("os").umask(previous_umask)
    protected = Path(profile["output"]["protected_artifact_path"])
    assert protected.stat().st_mode & 0o777 == 0o600
    assert protected.parent.stat().st_mode & 0o777 == 0o700


def test_ci_checker_rejects_pass_from_noncanonical_or_activated_policy(
    tmp_path: Path,
) -> None:
    report = evaluate_rows(_valid_rows(), _profile(), allow_internal_rows=True)
    assert report["status"] == PASS
    artifact, receipt_sha, protected_sha = _write_sanitized_receipt(
        tmp_path, report, name="noncanonical-pass.json"
    )
    assert any(
        "does not bind the canonical W6 evaluation profile" in error
        for error in validate_artifact(
            artifact,
            trusted_report_sha256=receipt_sha,
            trusted_full_report_sha256=protected_sha,
        )
    )

    report["policy_activation_status"] = "PROMOTED"
    report["promotion_eligible"] = True
    report["future_run_only"] = False
    report["calibration"]["active_threshold"] = 0.9
    report["deterministic_digest"] = canonical_digest(
        {key: value for key, value in report.items() if key != "deterministic_digest"}
    )
    artifact, receipt_sha, protected_sha = _write_sanitized_receipt(
        tmp_path, report, name="activated-pass.json"
    )
    errors = validate_artifact(
        artifact,
        trusted_report_sha256=receipt_sha,
        trusted_full_report_sha256=protected_sha,
    )
    assert "W6 may evaluate only an UNPROMOTED future-run policy" in errors
    assert "W6 evaluation cannot make a policy promotion eligible" in errors
    assert "W6 calibration must remain future-run-only" in errors
    assert "W6 evaluation cannot contain an active threshold" in errors


def test_ci_checker_rejects_canonical_profile_proof_split_policy_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = evaluate_rows(_valid_rows(), _profile(), allow_internal_rows=True)
    artifact, receipt_sha, protected_sha = _write_sanitized_receipt(
        tmp_path, report, name="profile-policy-drift.json"
    )
    canonical_profile = yaml.safe_load(
        (
            Path(__file__).resolve().parents[4]
            / "apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml"
        ).read_text(encoding="utf-8")
    )
    canonical_profile["dataset"]["proof_split_policy_id"] = (
        "c03-proof-identity-stratified-sha256-v1"
    )
    drifted_profile = tmp_path / "drifted-profile.yaml"
    drifted_profile.write_text(
        yaml.safe_dump(canonical_profile, sort_keys=True), encoding="utf-8"
    )
    monkeypatch.setattr(
        "ops_scripts.ci.check_apps_rg_resume_graph_w6.CANONICAL_PROFILE",
        drifted_profile,
    )
    errors = validate_artifact(
        artifact,
        trusted_report_sha256=receipt_sha,
        trusted_full_report_sha256=protected_sha,
    )
    assert (
        "canonical W6 proof split policy differs from the shared evaluator contract"
        in errors
    )


def test_sanitized_ci_receipt_omits_controlled_evaluation_details(tmp_path: Path) -> None:
    report = evaluate_rows(_valid_rows(), _profile(), allow_internal_rows=True)
    artifact, _, _ = _write_sanitized_receipt(tmp_path, report)
    receipt = json.loads(artifact.read_text(encoding="utf-8"))
    for key in (
        "per_sample_results",
        "retrieval_sample_results",
        "coverage",
        "model",
        "candidate_threshold",
        "proof_score_raw",
        "proof_confidence_calibrated",
        "source_ref",
        "reasons",
    ):
        assert not _contains_key(receipt, key)


def test_forged_sanitized_pass_cannot_self_authorize_with_known_full_digest(
    tmp_path: Path,
) -> None:
    report = evaluate_rows(_valid_rows(), _profile(), allow_internal_rows=True)
    canonical_profile = yaml.safe_load(
        (
            Path(__file__).resolve().parents[4]
            / "apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml"
        ).read_text(encoding="utf-8")
    )
    report["profile_digest"] = canonical_digest(canonical_profile)
    report["evaluation_mode"] = "OFFICIAL"
    report["official_evidence_chain_validated"] = True
    report["evidence_chain"] = {
        "export_receipt_sha256": "1" * 64,
        "prelabel_packet_manifest_sha256": "5" * 64,
        "human_review_authority_receipt_sha256": "6" * 64,
        "packet_manifest_sha256": "2" * 64,
        "packet_manifest_digest": "3" * 64,
        "completed_validation_digest": "4" * 64,
    }
    report["deterministic_digest"] = canonical_digest(
        {key: value for key, value in report.items() if key != "deterministic_digest"}
    )
    artifact, _, protected_sha = _write_sanitized_receipt(
        tmp_path, report, name="forged-pass.json"
    )
    errors = validate_artifact(
        artifact,
        trusted_full_report_sha256=protected_sha,
    )
    assert any(
        "trusted sanitized-receipt SHA-256" in error for error in errors
    )


def test_pinned_pass_cannot_omit_canonical_metrics_or_release_gates(
    tmp_path: Path,
) -> None:
    report = evaluate_rows(_valid_rows(), _profile(), allow_internal_rows=True)
    canonical_profile = yaml.safe_load(
        (
            Path(__file__).resolve().parents[4]
            / "apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml"
        ).read_text(encoding="utf-8")
    )
    report["profile_digest"] = canonical_digest(canonical_profile)
    report["evaluation_id"] = canonical_profile["profile_id"]
    report["policy_version"] = canonical_profile["policy_version"]
    report["evaluation_mode"] = "OFFICIAL"
    report["official_evidence_chain_validated"] = True
    report["evidence_chain"] = {
        "export_receipt_sha256": "1" * 64,
        "prelabel_packet_manifest_sha256": "5" * 64,
        "human_review_authority_receipt_sha256": "6" * 64,
        "packet_manifest_sha256": "2" * 64,
        "packet_manifest_digest": "3" * 64,
        "completed_validation_digest": "4" * 64,
    }
    report["deterministic_digest"] = canonical_digest(
        {key: value for key, value in report.items() if key != "deterministic_digest"}
    )
    artifact, _, protected_sha = _write_sanitized_receipt(
        tmp_path, report, name="truncated-pass.json"
    )
    receipt = json.loads(artifact.read_text(encoding="utf-8"))
    receipt["metrics"] = {"authority_eligibility_accuracy": 1.0}
    receipt["gate_results"] = {
        "authority_eligibility_accuracy_minimum": {
            "metric": "authority_eligibility_accuracy",
            "direction": "minimum",
            "threshold": 1.0,
            "value": 1.0,
            "status": PASS,
        }
    }
    receipt["record_digest"] = canonical_digest(
        {key: value for key, value in receipt.items() if key != "record_digest"}
    )
    artifact.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    receipt_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    errors = validate_artifact(
        artifact,
        trusted_report_sha256=receipt_sha,
        trusted_full_report_sha256=protected_sha,
    )
    assert any("metrics key inventory mismatch" in error for error in errors)
    assert any("gate_results key inventory mismatch" in error for error in errors)


def test_cli_rejects_aliasing_protected_and_sanitized_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile = _profile(tmp_path)
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=True), encoding="utf-8")
    alias = tmp_path / "same-output.json"
    assert main(
        [
            "--profile",
            str(profile_path),
            "--out",
            str(alias),
            "--ci-receipt-out",
            str(alias),
        ]
    ) == 2
    assert not alias.exists()
    assert "distinct paths" in json.loads(capsys.readouterr().out)["error"]


def test_cli_rejects_output_aliasing_dataset_or_controlled_roots(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile = _profile(tmp_path)
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text("", encoding="utf-8")
    profile["dataset"]["dataset_path"] = str(dataset)
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=True), encoding="utf-8")
    assert main(
        ["--profile", str(profile_path), "--out", str(dataset)]
    ) == 2
    assert "must not alias" in json.loads(capsys.readouterr().out)["error"]

    labels = tmp_path / "labels"
    labels.mkdir(mode=0o700)
    nested_output = labels / "protected.json"
    assert main(
        [
            "--profile",
            str(profile_path),
            "--labels-dir",
            str(labels),
            "--out",
            str(nested_output),
        ]
    ) == 2
    assert "outside packet and label roots" in json.loads(
        capsys.readouterr().out
    )["error"]

    controlled_file = labels / "claim_reviews.jsonl"
    controlled_file.write_text("{}\n", encoding="utf-8")
    controlled_file.chmod(0o600)
    hardlink_output = tmp_path / "hardlink-protected.json"
    __import__("os").link(controlled_file, hardlink_output)
    assert main(
        [
            "--profile",
            str(profile_path),
            "--labels-dir",
            str(labels),
            "--out",
            str(hardlink_output),
        ]
    ) == 2
    assert "must not alias any controlled evidence file" in json.loads(
        capsys.readouterr().out
    )["error"]


def test_cli_rehashes_controlled_inputs_after_evaluation_before_writing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = _profile(tmp_path)
    dataset = Path(profile["dataset"]["dataset_path"])
    dataset.write_text("{}\n", encoding="utf-8")
    dataset.chmod(0o600)
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=True), encoding="utf-8")

    def mutate_input_during_evaluation(
        dataset_path: Path, evaluation_profile: dict, **_: object
    ) -> dict:
        dataset_path.write_text('{"mutated":true}\n', encoding="utf-8")
        return evaluate_rows(
            _valid_rows(), evaluation_profile, allow_internal_rows=True
        )

    monkeypatch.setattr(
        "ops_scripts.calibration.apps_rg_resume_graph_w6.evaluate_file",
        mutate_input_during_evaluation,
    )
    assert main(["--profile", str(profile_path)]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert "changed during evaluation before output" in payload["error"]
    assert not Path(profile["output"]["protected_artifact_path"]).exists()
    assert not Path(profile["output"]["artifact_path"]).exists()


def test_tampering_with_a_human_row_is_detected_by_content_digest() -> None:
    rows = copy.deepcopy(_valid_rows())
    rows[-1]["proof_label"] = False
    report = evaluate_rows(rows, _profile(), allow_internal_rows=True)
    assert report["status"] == INSUFFICIENT
    assert any("content_digest:MISMATCH" in reason for reason in report["reasons"])
