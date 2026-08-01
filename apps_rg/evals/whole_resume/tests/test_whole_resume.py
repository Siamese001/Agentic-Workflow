from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from apps_rg.evals.c03_w9_closeout import build_w9_closeout
from apps_rg.evals.resume_graph.reporting import canonical_digest
from apps_rg.evals.whole_resume.constants import METRIC_NAMES, RUBRIC_ID, W9_DIMENSIONS
from apps_rg.evals.whole_resume.evaluation import evaluate_whole_resume
from apps_rg.evals.whole_resume.reporting import receipt_digest_is_valid
from apps_rg.evals.whole_resume.validation import (
    pair_payload_digest,
    rubric_file_digest,
    w9_review_bundle_digest,
)

PACKAGE = Path(__file__).resolve().parents[1]
EVALS_ROOT = PACKAGE.parent
INPUT_SCHEMA = PACKAGE / "schemas" / "whole_resume_input.v1.schema.json"
RECEIPT_SCHEMA = PACKAGE / "schemas" / "whole_resume_receipt.v1.schema.json"
RUBRIC = PACKAGE / "rubrics" / "whole_resume.v1.yaml"
CONTROLS = PACKAGE / "fixtures" / "benchmark_controls.v1.json"
CONTRACT = EVALS_ROOT / "contracts" / "evaluation_contract.v2.yaml"


def _seal(value: Mapping[str, Any], field: str = "record_digest") -> dict[str, Any]:
    sealed = dict(value)
    sealed[field] = canonical_digest({key: item for key, item in sealed.items() if key != field})
    return sealed


def _labels(*, preference: str = "TIE") -> dict[str, Any]:
    dimensions = dict.fromkeys(W9_DIMENSIONS, 4)
    return {
        "resume_a": dict(dimensions),
        "resume_b": dict(dimensions),
        "preference": preference,
    }


def _artifact(artifact_id: str) -> dict[str, Any]:
    sections = [
        {
            "section_id": "headline",
            "text": "Product strategy and platform transformation leader.",
            "claims": [
                {
                    "claim_id": f"{artifact_id}-headline",
                    "section_id": "headline",
                    "text": "Product strategy and platform transformation leader.",
                    "material": True,
                    "grounding_status": "PASS",
                    "evidence_refs": ["graph://skill/product-strategy"],
                    "employment_id": None,
                    "employer_id": None,
                    "title_id": None,
                    "achievement_id": None,
                    "jd_concept_ids": ["concept-product-strategy"],
                    "fact_bindings": [],
                }
            ],
        },
        {
            "section_id": "executive_summary",
            "text": "Product strategist improving digital platforms through grounded operating models.",
            "claims": [
                {
                    "claim_id": f"{artifact_id}-summary",
                    "section_id": "executive_summary",
                    "text": "Product strategist improving digital platforms through grounded operating models.",
                    "material": True,
                    "grounding_status": "PASS",
                    "evidence_refs": ["graph://skill/platform-strategy"],
                    "employment_id": None,
                    "employer_id": None,
                    "title_id": None,
                    "achievement_id": None,
                    "jd_concept_ids": ["concept-product-strategy"],
                    "fact_bindings": [],
                }
            ],
        },
        {
            "section_id": "competencies",
            "text": "Product strategy, platform modernization, and stakeholder alignment.",
            "claims": [],
        },
        {
            "section_id": "unify_bullets",
            "text": "Modernized a digital platform using governed evidence and measurable delivery practices.",
            "claims": [
                {
                    "claim_id": f"{artifact_id}-experience",
                    "section_id": "unify_bullets",
                    "text": "Modernized a digital platform using governed evidence and measurable delivery practices.",
                    "material": True,
                    "grounding_status": "PASS",
                    "evidence_refs": ["graph://achievement/platform-modernization"],
                    "employment_id": "employment-unify",
                    "employer_id": "employer-unify",
                    "title_id": "title-product",
                    "achievement_id": "achievement-modernization",
                    "jd_concept_ids": ["concept-platform-modernization"],
                    "fact_bindings": [
                        {
                            "key": "employment-unify/employer",
                            "value": "Unify",
                            "critical": True,
                        }
                    ],
                }
            ],
        },
    ]
    return {
        "artifact_id": artifact_id,
        "content": "\n".join(section["text"] for section in sections),
        "sections": sections,
        "employment": [
            {
                "employment_id": "employment-unify",
                "employer_id": "employer-unify",
                "title_id": "title-product",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
            }
        ],
    }


def _pair(index: int) -> dict[str, Any]:
    candidate_variant = "A" if index % 2 == 0 else "B"
    pair: dict[str, Any] = {
        "pair_id": f"pair-{index}",
        "target_profile_id": f"profile-{index}",
        "variant_identity_hidden": True,
        "candidate_variant": candidate_variant,
        "target_context": {
            "jd_text": "Seeking product strategy expertise for platform modernization and customer outcomes.",
            "jd_concepts": [
                {"concept_id": "concept-product-strategy", "text": "product strategy"},
                {
                    "concept_id": "concept-platform-modernization",
                    "text": "platform modernization",
                },
            ],
            "relevant_achievement_ids": ["achievement-modernization"],
        },
        "resume_a": _artifact(f"pair-{index}-resume-a"),
        "resume_b": _artifact(f"pair-{index}-resume-b"),
        "rubric_id": RUBRIC_ID,
        "rubric_digest": rubric_file_digest(),
    }
    pair["pair_payload_digest"] = pair_payload_digest(pair)
    reviews: list[dict[str, Any]] = []
    for reviewer in (1, 2):
        reviews.append(
            _seal(
                {
                    "review_id": f"review-pair-{index}-{reviewer}",
                    "reviewer_identity_ref": f"human-reviewer://w9-{reviewer}",
                    "qualification_ref": "resume-coach://executive-resume-review",
                    "independent_review": True,
                    "blinded_payload_digest": pair["pair_payload_digest"],
                    "rubric_digest": pair["rubric_digest"],
                    "labels": _labels(),
                }
            )
        )
    pair["reviews"] = reviews
    pair["adjudication"] = _seal(
        {
            "adjudication_id": f"adjudication-pair-{index}",
            "status": "CONSENSUS_ACCEPTED",
            "review_refs": [review["review_id"] for review in reviews],
            "review_digests": [review["record_digest"] for review in reviews],
            "final_labels": _labels(),
        }
    )
    return pair


def _bundle() -> dict[str, Any]:
    pairs = [_pair(index) for index in range(6)]
    evidence = _seal(
        {
            "status": "PASS",
            "official_pass": True,
            "require_w9": True,
            "completed_validation_digest": "a" * 64,
            "authority_receipt_digest": "b" * 64,
            "w9_review_bundle_digest": w9_review_bundle_digest(pairs),
        }
    )
    return _seal(
        {
            "schema_version": "apps_rg.whole_resume_input.v1",
            "evaluation_id": "whole-resume-control-v1",
            "official_w6_status": "PASS",
            "generation_authorized": True,
            "human_review_evidence": evidence,
            "pairs": pairs,
        },
        "bundle_digest",
    )


def _candidate(pair: dict[str, Any]) -> dict[str, Any]:
    return pair["resume_a" if pair["candidate_variant"] == "A" else "resume_b"]


def _rebind(bundle: dict[str, Any]) -> None:
    for pair in bundle["pairs"]:
        pair["pair_payload_digest"] = pair_payload_digest(pair)
        for review in pair["reviews"]:
            review["blinded_payload_digest"] = pair["pair_payload_digest"]
            review["rubric_digest"] = pair["rubric_digest"]
            review["record_digest"] = canonical_digest(
                {key: value for key, value in review.items() if key != "record_digest"}
            )
        pair["adjudication"]["review_refs"] = [review["review_id"] for review in pair["reviews"]]
        pair["adjudication"]["review_digests"] = [review["record_digest"] for review in pair["reviews"]]
        pair["adjudication"]["record_digest"] = canonical_digest(
            {key: value for key, value in pair["adjudication"].items() if key != "record_digest"}
        )
    bundle["human_review_evidence"]["w9_review_bundle_digest"] = w9_review_bundle_digest(bundle["pairs"])
    bundle["human_review_evidence"]["record_digest"] = canonical_digest(
        {key: value for key, value in bundle["human_review_evidence"].items() if key != "record_digest"}
    )
    bundle["bundle_digest"] = canonical_digest(
        {key: value for key, value in bundle.items() if key != "bundle_digest"}
    )


def test_schemas_rubric_and_contract_cover_every_emitted_metric() -> None:
    input_schema = json.loads(INPUT_SCHEMA.read_text(encoding="utf-8"))
    receipt_schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator.check_schema(receipt_schema)
    Draft202012Validator(input_schema, format_checker=FormatChecker()).validate(_bundle())
    receipt = evaluate_whole_resume(_bundle())
    Draft202012Validator(receipt_schema).validate(receipt)

    rubric = yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))
    assert rubric["pair_contract"]["authorized_pair_count"] == 6
    assert rubric["authority"]["receipt_release_authorizing_by_itself"] is False
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    contract_metrics = {row["name"] for row in contract["gates"]["G4"]["metrics"]}
    assert set(METRIC_NAMES) <= contract_metrics

    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    assert controls["authorized_pair_count"] == 6
    assert controls["authority"] == {
        "production_labels": False,
        "calibration_evidence": False,
        "release_authority": False,
        "current_run_mutation": False,
    }


def test_complete_six_pair_bundle_passes_without_blended_score() -> None:
    receipt = evaluate_whole_resume(_bundle())

    assert receipt["status"] == "PASS"
    assert receipt["whole_resume_release_pass"] is True
    assert receipt["pair_count"] == 6
    assert receipt["human_review_count"] == 12
    assert receipt["adjudication_count"] == 6
    assert receipt["metrics"]["material_claim_grounding_rate"] == 1.0
    assert receipt["metrics"]["human_grounding_no_worse_rate"] == 1.0
    assert receipt["metrics"]["human_naturalness_no_worse_rate"] == 1.0
    assert receipt["metrics"]["human_relevance_no_worse_rate"] == 1.0
    assert receipt["metrics"]["material_defect_count"] == 0
    assert "overall_score" not in receipt
    assert receipt["authority"]["release_authorizing"] is False
    assert receipt_digest_is_valid(receipt)
    assert receipt == evaluate_whole_resume(_bundle())


def test_input_tampering_is_unknown_instead_of_crashing() -> None:
    bundle = _bundle()
    _candidate(bundle["pairs"][0])["sections"][0]["text"] = "Tampered headline"
    receipt = evaluate_whole_resume(bundle)

    assert receipt["status"] == "UNKNOWN"
    assert receipt["whole_resume_release_pass"] is False
    assert any("digest mismatch" in reason for reason in receipt["unknown_reasons"])


@pytest.mark.parametrize("pair_count", (0, 5, 7))
def test_exactly_six_pairs_are_required(pair_count: int) -> None:
    bundle = _bundle()
    if pair_count < 6:
        bundle["pairs"] = bundle["pairs"][:pair_count]
    else:
        extra = _pair(6)
        bundle["pairs"].append(extra)
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)

    assert receipt["status"] == "FAIL"
    assert "SIX_AUTHORIZED_W9_PAIRS_REQUIRED" in receipt["failure_codes"]


def test_w6_and_official_human_review_evidence_fail_closed() -> None:
    bundle = _bundle()
    bundle["official_w6_status"] = "UNKNOWN"
    _rebind(bundle)
    assert evaluate_whole_resume(bundle)["status"] == "UNKNOWN"

    bundle = _bundle()
    bundle["official_w6_status"] = "FAIL"
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)
    assert receipt["status"] == "FAIL"
    assert "OFFICIAL_W6_NONPASS" in receipt["failure_codes"]

    bundle = _bundle()
    bundle["human_review_evidence"]["status"] = "PASS_TEST_ONLY"
    bundle["human_review_evidence"]["official_pass"] = False
    _rebind(bundle)
    assert evaluate_whole_resume(bundle)["status"] == "UNKNOWN"


def test_material_grounding_and_critical_consistency_fail() -> None:
    bundle = _bundle()
    candidate = _candidate(bundle["pairs"][0])
    candidate["sections"][0]["claims"][0]["grounding_status"] = "FAIL"
    candidate["sections"][1]["claims"][0]["fact_bindings"] = [
        {"key": "employment-unify/employer", "value": "Different", "critical": True}
    ]
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)

    assert receipt["status"] == "FAIL"
    assert "MATERIAL_CLAIM_GROUNDING_NONPASS" in receipt["failure_codes"]
    assert "CRITICAL_CROSS_SECTION_INCONSISTENCY" in receipt["failure_codes"]
    assert receipt["metrics"]["material_claim_grounding_rate"] < 1.0


def test_inflation_terms_use_token_boundaries() -> None:
    bundle = _bundle()
    candidate = _candidate(bundle["pairs"][0])
    claim = candidate["sections"][0]["claims"][0]
    claim["text"] = "Enabled product strategy and platform transformation."
    claim["grounding_status"] = "FAIL"
    candidate["sections"][0]["text"] = claim["text"]
    candidate["content"] = "\n".join(row["text"] for row in candidate["sections"])
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)

    assert receipt["status"] == "FAIL"
    assert receipt["metrics"]["unsupported_leadership_inflation_count"] == 0


def test_chronology_employer_and_ats_defects_fail() -> None:
    bundle = _bundle()
    candidate = _candidate(bundle["pairs"][0])
    candidate["employment"][0]["start_date"] = "2024-01-01"
    candidate["employment"][0]["end_date"] = "2023-01-01"
    candidate["sections"][3]["claims"][0]["employer_id"] = "wrong-employer"
    candidate["content"] += " | table"
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)

    assert receipt["status"] == "FAIL"
    assert "CHRONOLOGY_INCONSISTENCY" in receipt["failure_codes"]
    assert "EMPLOYER_TITLE_INCONSISTENCY" in receipt["failure_codes"]
    assert "ATS_STRUCTURE_NONPASS" in receipt["failure_codes"]


def test_duplicate_and_summary_experience_repetition_fail() -> None:
    bundle = _bundle()
    candidate = _candidate(bundle["pairs"][0])
    summary_claim = candidate["sections"][1]["claims"][0]
    experience_claim = candidate["sections"][3]["claims"][0]
    summary_claim["achievement_id"] = experience_claim["achievement_id"]
    summary_claim["text"] = experience_claim["text"]
    candidate["sections"][1]["text"] = experience_claim["text"]
    candidate["content"] = "\n".join(row["text"] for row in candidate["sections"])
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)

    assert receipt["status"] == "FAIL"
    assert "DUPLICATE_ACHIEVEMENT" in receipt["failure_codes"]
    assert "SUMMARY_EXPERIENCE_REPETITION" in receipt["failure_codes"]


@pytest.mark.parametrize(
    ("dimension", "failure_code"),
    (
        ("authenticity_factuality", "HUMAN_GROUNDING_REGRESSION"),
        ("claim_naturalness", "HUMAN_NATURALNESS_REGRESSION"),
        ("target_relevance", "HUMAN_RELEVANCE_REGRESSION"),
    ),
)
def test_human_no_worse_decisions_are_calculated(dimension: str, failure_code: str) -> None:
    bundle = _bundle()
    pair = bundle["pairs"][0]
    candidate_key = "resume_a" if pair["candidate_variant"] == "A" else "resume_b"
    baseline_key = "resume_b" if candidate_key == "resume_a" else "resume_a"
    for review in pair["reviews"]:
        review["labels"][candidate_key][dimension] = 3
        review["labels"][baseline_key][dimension] = 4
    pair["adjudication"]["final_labels"][candidate_key][dimension] = 3
    pair["adjudication"]["final_labels"][baseline_key][dimension] = 4
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)

    assert receipt["status"] == "FAIL"
    assert failure_code in receipt["failure_codes"]


def test_candidate_preference_and_reviewer_agreement_are_separate_metrics() -> None:
    bundle = _bundle()
    pair = bundle["pairs"][0]
    candidate_variant = pair["candidate_variant"]
    for review in pair["reviews"]:
        review["labels"]["preference"] = candidate_variant
    pair["adjudication"]["final_labels"]["preference"] = candidate_variant
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)

    pair_result = receipt["pair_results"][0]["pairwise_result"]
    assert pair_result["raw_preference"] == candidate_variant
    assert pair_result["resolved_preference"] == "CANDIDATE"
    assert receipt["metrics"]["candidate_preference_rate"] == pytest.approx(1 / 6, abs=1e-6)
    assert receipt["metrics"]["reviewer_agreement_rate"] == 1.0


def test_disagreement_requires_a_qualified_human_adjudicator() -> None:
    bundle = _bundle()
    pair = bundle["pairs"][0]
    pair["reviews"][0]["labels"]["preference"] = "A"
    pair["reviews"][1]["labels"]["preference"] = "B"
    pair["adjudication"]["status"] = "ADJUDICATED"
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)
    assert receipt["status"] == "UNKNOWN"
    assert any("qualified human adjudicator" in reason for reason in receipt["unknown_reasons"])

    pair["adjudication"].update(
        {
            "adjudicator_identity_ref": "human-reviewer://w9-adjudicator",
            "qualification_ref": "resume-coach://executive-resume-review",
            "human_attestation": True,
        }
    )
    _rebind(bundle)
    receipt = evaluate_whole_resume(bundle)
    assert receipt["status"] == "PASS"
    assert receipt["metrics"]["reviewer_agreement_rate"] < 1.0


def test_closeout_consumes_and_binds_the_sealed_receipt() -> None:
    bundle = _bundle()
    evaluation_receipt = evaluate_whole_resume(bundle)
    pair_receipts = [
        {
            "pair_id": pair["pair_id"],
            "pair_payload_digest": pair["pair_payload_digest"],
            "variant_identity_hidden": True,
        }
        for pair in bundle["pairs"]
    ]
    reviews = [
        {"pair_id": pair["pair_id"], "qualified_resume_coach": True}
        for pair in bundle["pairs"]
        for _ in range(2)
    ]
    adjudications = [{"pair_id": pair["pair_id"]} for pair in bundle["pairs"]]
    closeout = build_w9_closeout(
        pair_receipts=pair_receipts,
        coach_reviews=reviews,
        adjudications=adjudications,
        official_w6_status="PASS",
        generation_authorized=True,
        whole_resume_evaluation_receipt=evaluation_receipt,
    )

    assert closeout["release_pass"] is True
    assert closeout["promotion_eligible"] is True
    assert closeout["whole_resume_gate_source"] == "SEALED_EVALUATION_RECEIPT"
    assert closeout["whole_resume_evaluation_receipt_digest"] == evaluation_receipt["record_digest"]

    tampered = deepcopy(evaluation_receipt)
    tampered["metrics"]["material_defect_count"] = 1
    closeout = build_w9_closeout(
        pair_receipts=pair_receipts,
        coach_reviews=reviews,
        adjudications=adjudications,
        official_w6_status="PASS",
        generation_authorized=True,
        whole_resume_evaluation_receipt=tampered,
    )
    assert closeout["release_pass"] is False
    assert "whole_resume_evaluation_receipt_digest_invalid" in closeout["failure_codes"]

    incomplete = deepcopy(evaluation_receipt)
    incomplete["metrics"].pop("jd_concept_coverage")
    incomplete["record_digest"] = canonical_digest(
        {key: value for key, value in incomplete.items() if key != "record_digest"}
    )
    closeout = build_w9_closeout(
        pair_receipts=pair_receipts,
        coach_reviews=reviews,
        adjudications=adjudications,
        official_w6_status="PASS",
        generation_authorized=True,
        whole_resume_evaluation_receipt=incomplete,
    )
    assert closeout["release_pass"] is False
    assert "whole_resume_evaluation_metrics_invalid" in closeout["failure_codes"]

    misbound = deepcopy(evaluation_receipt)
    misbound["pair_results"][0]["pair_payload_digest"] = "f" * 64
    misbound["record_digest"] = canonical_digest(
        {key: value for key, value in misbound.items() if key != "record_digest"}
    )
    closeout = build_w9_closeout(
        pair_receipts=pair_receipts,
        coach_reviews=reviews,
        adjudications=adjudications,
        official_w6_status="PASS",
        generation_authorized=True,
        whole_resume_evaluation_receipt=misbound,
    )
    assert closeout["release_pass"] is False
    assert "whole_resume_evaluation_pair_results_binding_mismatch" in closeout["failure_codes"]


def test_closeout_rejects_a_malformed_receipt_without_crashing() -> None:
    closeout = build_w9_closeout(whole_resume_evaluation_receipt=[])  # type: ignore[arg-type]
    assert closeout["release_pass"] is False
    assert "whole_resume_evaluation_receipt_invalid" in closeout["failure_codes"]


def test_cli_writes_a_deterministic_receipt(tmp_path: Path) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "receipt.json"
    input_path.write_text(json.dumps(_bundle(), sort_keys=True), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg.evals.whole_resume",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--compact",
        ],
        check=False,
        capture_output=True,
        cwd=EVALS_ROOT.parents[1],
        shell=False,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["status"] == "PASS"
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written == evaluate_whole_resume(_bundle())
    assert receipt_digest_is_valid(written)


@pytest.mark.parametrize(
    "malformed",
    (
        None,
        [],
        {"schema_version": 7},
        {"pairs": [None]},
        {"pairs": [{"reviews": 7, "adjudication": []}]},
    ),
)
def test_malformed_inputs_return_unknown(malformed: Any) -> None:
    receipt = evaluate_whole_resume(malformed)
    assert receipt["status"] == "UNKNOWN"
    assert receipt["whole_resume_release_pass"] is False
