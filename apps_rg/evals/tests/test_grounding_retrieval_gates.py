from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from apps_rg.evals.resume_graph.metrics.binding import exact_binding_accuracy
from apps_rg.evals.resume_graph.metrics.grounding import (
    evaluate_binding_gate,
    evaluate_claim_evidence,
    evaluate_grounding_gate,
    seal_claim_evidence_record,
)
from apps_rg.evals.resume_graph.metrics.retrieval import (
    evaluate_retrieval_gate,
    evaluate_retrieval_query,
    seal_retrieval_query,
)

EVALS_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = EVALS_ROOT / "fixtures" / "resume_graph"
GROUNDING_FIXTURE = FIXTURE_ROOT / "grounding_mutations.v1.json"
RETRIEVAL_FIXTURE = FIXTURE_ROOT / "retrieval_hard_negatives.v1.json"
CLAIM_SCHEMA = EVALS_ROOT / "schemas" / "claim_evidence_record.v1.schema.json"
RETRIEVAL_SCHEMA = EVALS_ROOT / "schemas" / "retrieval_universe.v1.schema.json"
GROUNDING_RUBRIC = EVALS_ROOT / "contracts" / "grounding_binding_rubric.v1.yaml"
RETRIEVAL_RUBRIC = EVALS_ROOT / "contracts" / "retrieval_coverage_rubric.v1.yaml"
EVALUATION_CONTRACT = EVALS_ROOT / "contracts" / "evaluation_contract.v2.yaml"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _set_path(value: dict[str, Any], path: list[str], replacement: Any) -> None:
    target = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement


def _grounding_record() -> dict[str, Any]:
    return seal_claim_evidence_record(deepcopy(_json(GROUNDING_FIXTURE)["base_record"]))


def _retrieval_query(split: str, suffix: str) -> dict[str, Any]:
    query = deepcopy(_json(RETRIEVAL_FIXTURE)["query_template"])
    query["query_id"] = f"{query['query_id']}-{suffix}"
    query["split"] = split
    candidate_ids = {
        candidate["candidate_id"]: f"{candidate['candidate_id']}-{suffix}"
        for candidate in query["candidates"]
    }
    query["candidate_universe"]["candidate_ids"] = [
        candidate_ids[candidate_id] for candidate_id in query["candidate_universe"]["candidate_ids"]
    ]
    for candidate in query["candidates"]:
        candidate["candidate_id"] = candidate_ids[candidate["candidate_id"]]
        if candidate["near_duplicate_of"] is not None:
            candidate["near_duplicate_of"] = candidate_ids[candidate["near_duplicate_of"]]
    return seal_retrieval_query(query)


def _promote_candidate(query: dict[str, Any], candidate_stem: str) -> dict[str, Any]:
    mutated = deepcopy(query)
    candidates = mutated["candidates"]
    selected = next(
        candidate for candidate in candidates if candidate["candidate_id"].startswith(candidate_stem)
    )
    reordered = [selected, *(candidate for candidate in candidates if candidate is not selected)]
    for rank, candidate in enumerate(reordered, 1):
        candidate["rank"] = rank
        candidate["score"] = round(1.0 - (rank / 100), 2)
    mutated["candidates"] = reordered
    return seal_retrieval_query(mutated)


def test_claim_evidence_schema_accepts_sealed_control_and_rejects_runtime_support_flag() -> None:
    schema = _json(CLAIM_SCHEMA)
    validator = Draft202012Validator(schema)
    record = _grounding_record()

    validator.validate(record)
    record["runtime_support_flag"] = True
    with pytest.raises(ValidationError):
        validator.validate(record)


def test_rubrics_freeze_fail_closed_denominators_and_future_run_authority() -> None:
    grounding = _yaml(GROUNDING_RUBRIC)
    retrieval = _yaml(RETRIEVAL_RUBRIC)

    assert grounding["runtime_authored_support_flags_are_proof"] is False
    assert grounding["missing_or_invalid_evidence_disposition"] == "UNKNOWN"
    assert grounding["gate_requirements"]["unsupported_material_claim_count"] == 0
    assert grounding["promotion_scope"] == "future_runs_only"
    assert retrieval["candidate_denominator"] == "full_finite_universe"
    assert retrieval["candidate_universe_authority"].startswith("frozen_human_labelled")
    assert retrieval["required_split_separation"] == ["CALIBRATION", "HOLDOUT"]
    assert set(retrieval["required_slices"]) == {
        "target_profile",
        "section",
        "graph_lane",
        "employer",
        "evidence_type",
        "metric_bearing",
        "evidence_density",
        "candidate_pool_size",
        "split",
        "hard_negative_class",
    }
    assert retrieval["promotion_scope"] == "future_runs_only"


def test_every_wave3_metric_maps_to_its_named_contract_gate() -> None:
    contract = _yaml(EVALUATION_CONTRACT)
    record = _grounding_record()
    calibration = _retrieval_query("CALIBRATION", "cal")
    holdout = _retrieval_query("HOLDOUT", "hold")
    results = {
        "G1": evaluate_retrieval_gate([calibration, holdout]),
        "G2": evaluate_binding_gate([record]),
        "G3": evaluate_grounding_gate([record]),
    }

    for gate_id, result in results.items():
        declared_metrics = {metric["name"] for metric in contract["gates"][gate_id]["metrics"]}
        assert set(result["metrics"]) <= declared_metrics


def test_known_good_material_claim_passes_grounding_and_binding() -> None:
    record = _grounding_record()

    claim_result = evaluate_claim_evidence(record)
    gate_result = evaluate_grounding_gate([record])

    assert claim_result["status"] == "PASS"
    assert claim_result["exact_evidence_locator"] == record["exact_evidence_locator"]
    assert claim_result["recomputed_support_disposition"] == "SUPPORTED"
    assert evaluate_binding_gate([record])["status"] == "PASS"
    assert gate_result["status"] == "PASS"
    assert gate_result["metrics"]["material_claim_support_rate"] == 1.0
    assert gate_result["metrics"]["unsupported_material_claim_count"] == 0
    assert gate_result["metrics"]["composite_claim_full_support_rate"] == 1.0


def test_known_good_paraphrase_preserves_authorized_entailment_and_passes() -> None:
    record = _grounding_record()
    record["claim_text"] = "Raised Acme team productivity 20 percent during 2024."

    result = evaluate_claim_evidence(seal_claim_evidence_record(record))

    assert result["status"] == "PASS"
    assert result["recomputed_support_disposition"] == "SUPPORTED"


@pytest.mark.parametrize("mutation_name", sorted(_json(GROUNDING_FIXTURE)["mutations"]))
def test_every_controlled_grounding_mutation_fails_closed(mutation_name: str) -> None:
    fixture = _json(GROUNDING_FIXTURE)
    mutation = fixture["mutations"][mutation_name]
    record = deepcopy(fixture["base_record"])
    _set_path(record, mutation["path"], mutation["value"])
    result = evaluate_claim_evidence(seal_claim_evidence_record(record))

    assert result["status"] == "FAIL"
    assert mutation["expected_code"] in result["failure_codes"]


def test_missing_exact_evidence_is_unknown_never_pass() -> None:
    record = _grounding_record()
    record["exact_evidence_locator"] = None
    record["locator_failure_reason"] = "source excerpt unavailable"
    result = evaluate_grounding_gate([seal_claim_evidence_record(record)])

    assert result["status"] == "UNKNOWN"
    assert result["failure_codes"] == []
    assert "EXACT_EVIDENCE_LOCATOR_UNAVAILABLE" in result["unknown_reasons"]
    assert result["claim_results"][0]["exact_evidence_locator"] is None
    assert result["claim_results"][0]["locator_failure_reason"] == "source excerpt unavailable"


def test_binding_and_grounding_gates_remain_independent() -> None:
    record = _grounding_record()
    record["entailment_grade"] = "NONE"
    record["support_disposition"] = "UNSUPPORTED"
    record = seal_claim_evidence_record(record)

    binding = evaluate_binding_gate([record])
    grounding = evaluate_grounding_gate([record])

    assert binding["gate_id"] == "G2"
    assert binding["status"] == "PASS"
    assert grounding["gate_id"] == "G3"
    assert grounding["status"] == "FAIL"
    assert "UNSUPPORTED_CLAIM" in grounding["failure_codes"]


def test_unknown_entailment_does_not_erase_exact_binding_measurement() -> None:
    record = _grounding_record()
    record["entailment_grade"] = "UNKNOWN"
    record["support_disposition"] = "UNKNOWN"
    record = seal_claim_evidence_record(record)

    assert evaluate_binding_gate([record])["status"] == "PASS"
    assert evaluate_grounding_gate([record])["status"] == "UNKNOWN"


def test_nonmaterial_claim_cannot_change_material_gate_denominator() -> None:
    material = _grounding_record()
    nonmaterial = _grounding_record()
    nonmaterial["claim_id"] = "claim-nonmaterial"
    nonmaterial["materiality"] = "NON_MATERIAL"
    nonmaterial["bindings"]["employer"] = {
        "status": "MISMATCH",
        "expected": "Acme",
        "observed": "OtherCo",
        "inflation": False,
    }
    nonmaterial = seal_claim_evidence_record(nonmaterial)

    grounding = evaluate_grounding_gate([material, nonmaterial])
    binding = evaluate_binding_gate([material, nonmaterial])

    assert grounding["status"] == "PASS"
    assert grounding["metrics"]["material_claim_support_rate"] == 1.0
    assert binding["status"] == "PASS"


def test_declared_support_cannot_override_a_binding_mismatch() -> None:
    record = _grounding_record()
    record["bindings"]["employer"] = {
        "status": "MISMATCH",
        "expected": "Acme",
        "observed": "OtherCo",
        "inflation": False,
    }
    record["support_disposition"] = "SUPPORTED"
    result = evaluate_claim_evidence(seal_claim_evidence_record(record))

    assert result["status"] == "FAIL"
    assert "EMPLOYER_BINDING_MISMATCH" in result["failure_codes"]
    assert "DECLARED_SUPPORT_DISPOSITION_MISMATCH" in result["failure_codes"]


def test_exact_binding_accuracy_uses_all_applicable_records() -> None:
    exact = _grounding_record()
    mismatch = deepcopy(exact)
    mismatch["bindings"]["role"] = {
        "status": "MISMATCH",
        "expected": "Director",
        "observed": "Analyst",
        "inflation": False,
    }

    assert exact_binding_accuracy([exact, mismatch], "role") == 0.5


def test_retrieval_schema_and_clean_full_universe_pass() -> None:
    calibration = _retrieval_query("CALIBRATION", "cal")
    holdout = _retrieval_query("HOLDOUT", "hold")
    Draft202012Validator(_json(RETRIEVAL_SCHEMA)).validate(calibration)

    query_result = evaluate_retrieval_query(calibration)
    gate_result = evaluate_retrieval_gate([calibration, holdout])

    assert query_result["status"] == "PASS"
    assert query_result["metrics"]["recall_at_3"] == 1.0
    assert query_result["metrics"]["mrr"] == 1.0
    assert query_result["metrics"]["hard_negative_rejection_rate"] == 1.0
    assert gate_result["status"] == "PASS"
    assert gate_result["metrics"]["pooled_recall_at_3"] == 1.0
    assert gate_result["split_summary"] == {
        "calibration": {"query_count": 1, "candidate_count": 11},
        "holdout": {"query_count": 1, "candidate_count": 11},
    }


@pytest.mark.parametrize(
    "candidate_stem",
    _json(RETRIEVAL_FIXTURE)["critical_hard_negative_candidate_ids"],
)
def test_every_critical_hard_negative_fails_when_promoted_into_top_k(candidate_stem: str) -> None:
    query = _promote_candidate(_retrieval_query("CALIBRATION", "cal"), candidate_stem)
    result = evaluate_retrieval_query(query)

    assert result["status"] == "FAIL"
    assert "CRITICAL_HARD_NEGATIVE_SELECTED" in result["failure_codes"]


def test_full_candidate_denominator_tampering_is_unknown() -> None:
    query = _retrieval_query("CALIBRATION", "cal")
    query["candidates"] = query["candidates"][: query["gate_k"]]
    result = evaluate_retrieval_query(query)

    assert result["status"] == "UNKNOWN"
    assert "CANDIDATE_COUNT_MISMATCH" in result["unknown_reasons"]
    assert "QUERY_DIGEST_INVALID" in result["unknown_reasons"]


def test_top_k_only_ranking_cannot_be_resealed_as_full_universe() -> None:
    query = _retrieval_query("CALIBRATION", "cal")
    query["candidates"] = query["candidates"][: query["gate_k"]]
    query["candidate_count"] = len(query["candidates"])
    result = evaluate_retrieval_query(seal_retrieval_query(query))

    assert result["status"] == "UNKNOWN"
    assert "CANDIDATE_UNIVERSE_MISMATCH" in result["unknown_reasons"]


def test_retrieval_gate_preserves_required_slices_and_worst_case_status() -> None:
    calibration = _promote_candidate(_retrieval_query("CALIBRATION", "cal"), "negative-wrong-employer")
    holdout = _retrieval_query("HOLDOUT", "hold")
    result = evaluate_retrieval_gate([calibration, holdout])

    assert result["status"] == "FAIL"
    assert set(result["slices"]) == {
        "target_profile",
        "section",
        "graph_lane",
        "employer",
        "evidence_type",
        "metric_bearing",
        "evidence_density",
        "candidate_pool_size",
        "split",
        "hard_negative_class",
    }
    assert result["slices"]["split"]["CALIBRATION"]["status"] == "FAIL"
    assert result["slices"]["hard_negative_class"]["WRONG_EMPLOYER"]["status"] == "FAIL"


def test_calibration_and_holdout_must_be_distinct_and_complete() -> None:
    calibration = _retrieval_query("CALIBRATION", "shared")
    incomplete = evaluate_retrieval_gate([calibration])
    holdout_with_leakage = deepcopy(calibration)
    holdout_with_leakage["split"] = "HOLDOUT"
    holdout_with_leakage["query_id"] = "query-productivity-holdout"
    holdout_with_leakage = seal_retrieval_query(holdout_with_leakage)
    leaked = evaluate_retrieval_gate([calibration, holdout_with_leakage])

    assert incomplete["status"] == "UNKNOWN"
    assert "CALIBRATION_HOLDOUT_SPLIT_INCOMPLETE" in incomplete["unknown_reasons"]
    assert leaked["status"] == "FAIL"
    assert "CALIBRATION_HOLDOUT_LEAKAGE" in leaked["failure_codes"]
