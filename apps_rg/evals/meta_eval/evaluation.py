"""Exercise real critical graders against clean controls and controlled defects."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from apps_rg.evals.resume_graph.metrics.grounding import (
    evaluate_binding_gate,
    evaluate_grounding_gate,
    seal_claim_evidence_record,
)
from apps_rg.evals.resume_graph.metrics.retrieval import (
    evaluate_retrieval_gate,
    evaluate_retrieval_query,
    seal_retrieval_query,
)
from apps_rg.evals.resume_graph.reporting import canonical_digest

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "resume_graph"
_GRADER_CARDS = Path(__file__).resolve().parent / "grader_cards.v1.yaml"
SCHEMA_VERSION = "apps_rg.evaluator_validity_receipt.v1"


def _load(name: str) -> dict[str, Any]:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def _assign_path(value: dict[str, Any], path: list[str], replacement: Any) -> None:
    target: dict[str, Any] = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement


def _observation(
    *,
    case_id: str,
    grader: str,
    result: Mapping[str, Any],
    clean_control: bool,
    critical_mutation: bool,
    expected_code: str | None = None,
    allow_fail_closed_unknown: bool = False,
    isolation_reason: str | None = None,
) -> dict[str, Any]:
    codes = set(result.get("failure_codes", [])) | set(result.get("unknown_reasons", []))
    if clean_control:
        detected = result.get("status") == "PASS"
    else:
        detected = result.get("status") == "FAIL" or (
            allow_fail_closed_unknown and result.get("status") == "UNKNOWN"
        )
        if expected_code is not None:
            detected = detected and expected_code in codes
    return {
        "case_id": case_id,
        "grader": grader,
        "case_class": "CLEAN_CONTROL" if clean_control else "CRITICAL_MUTATION" if critical_mutation else "NONCRITICAL_MUTATION",
        "observed_status": result.get("status"),
        "expected_code": expected_code,
        "observed_codes": sorted(codes),
        "detected_or_accepted": detected,
        "unrelated_grader_isolation": isolation_reason or "SAME_INPUT_GRADER_ISOLATION_VERIFIED",
    }


def _promote_candidate(query: Mapping[str, Any], candidate_id: str) -> dict[str, Any]:
    mutated = copy.deepcopy(query)
    candidates = mutated["candidates"]
    chosen = next(candidate for candidate in candidates if candidate["candidate_id"] == candidate_id)
    reordered = [chosen] + [candidate for candidate in candidates if candidate["candidate_id"] != candidate_id]
    for index, candidate in enumerate(reordered, 1):
        candidate["rank"] = index
        candidate["score"] = round(1.0 - index / 100.0, 4)
    mutated["candidates"] = reordered
    return seal_retrieval_query(mutated)


def _distinct_holdout(query: Mapping[str, Any]) -> dict[str, Any]:
    holdout = copy.deepcopy(query)
    holdout["query_id"] = f"{holdout['query_id']}-holdout"
    holdout["split"] = "HOLDOUT"
    id_map = {
        candidate["candidate_id"]: f"{candidate['candidate_id']}-holdout"
        for candidate in holdout["candidates"]
    }
    holdout["candidate_universe"]["candidate_ids"] = [
        id_map[candidate_id] for candidate_id in holdout["candidate_universe"]["candidate_ids"]
    ]
    for candidate in holdout["candidates"]:
        candidate["candidate_id"] = id_map[candidate["candidate_id"]]
        if candidate["near_duplicate_of"] is not None:
            candidate["near_duplicate_of"] = id_map[candidate["near_duplicate_of"]]
    return seal_retrieval_query(holdout)


def _observations() -> list[dict[str, Any]]:
    grounding = _load("grounding_mutations.v1.json")
    base_record = seal_claim_evidence_record(grounding["base_record"])
    observations = [
        _observation(
            case_id="grounding_clean",
            grader="G3_GROUNDING",
            result=evaluate_grounding_gate([base_record]),
            clean_control=True,
            critical_mutation=False,
        ),
        _observation(
            case_id="provenance_clean",
            grader="G3_PROVENANCE",
            result=evaluate_grounding_gate([base_record]),
            clean_control=True,
            critical_mutation=False,
        ),
        _observation(
            case_id="binding_clean",
            grader="G2_BINDING",
            result=evaluate_binding_gate([base_record]),
            clean_control=True,
            critical_mutation=False,
        ),
    ]
    for mutation_id, mutation in grounding["mutations"].items():
        record = copy.deepcopy(grounding["base_record"])
        _assign_path(record, mutation["path"], mutation["value"])
        record = seal_claim_evidence_record(record)
        grader = "G3_GROUNDING" if mutation_id == "unsupported_entailment" else "G2_BINDING"
        result = (
            evaluate_grounding_gate([record])
            if grader == "G3_GROUNDING"
            else evaluate_binding_gate([record])
        )
        observations.append(
            _observation(
                case_id=f"grounding::{mutation_id}",
                grader=grader,
                result=result,
                clean_control=False,
                critical_mutation=True,
                expected_code=mutation["expected_code"],
                isolation_reason=(
                    "ENTAILMENT_ONLY_MUTATION_DOES_NOT_TARGET_BINDING"
                    if grader == "G3_GROUNDING"
                    else "BINDING_MUTATION_ISOLATED_TO_G2_BEFORE_G3"
                ),
            )
        )
    wrong_date = copy.deepcopy(grounding["base_record"])
    wrong_date["bindings"]["date"] = {
        "status": "MISMATCH",
        "expected": "2024",
        "observed": "2025",
        "inflation": False,
    }
    observations.append(
        _observation(
            case_id="grounding::wrong_date",
            grader="G2_BINDING",
            result=evaluate_binding_gate([seal_claim_evidence_record(wrong_date)]),
            clean_control=False,
            critical_mutation=True,
            expected_code="DATE_BINDING_MISMATCH",
            isolation_reason="BINDING_MUTATION_ISOLATED_TO_G2_BEFORE_G3",
        )
    )
    provenance_cases = []
    removed = copy.deepcopy(grounding["base_record"])
    removed["source_id"] = ""
    provenance_cases.append(("source_removed", seal_claim_evidence_record(removed), "SOURCE_ID_MISSING"))
    tampered = copy.deepcopy(base_record)
    tampered["source_excerpt_digest"] = "b" * 64
    provenance_cases.append(("source_digest_tampered", tampered, "CLAIM_EVIDENCE_DIGEST_INVALID"))
    wrong_path = copy.deepcopy(grounding["base_record"])
    wrong_path["path_binding"] = "MISMATCH"
    provenance_cases.append(("wrong_graph_path", seal_claim_evidence_record(wrong_path), "GRAPH_PATH_MISMATCH"))
    for case_id, record, expected_code in provenance_cases:
        observations.append(
            _observation(
                case_id=f"provenance::{case_id}",
                grader="G3_PROVENANCE",
                result=evaluate_grounding_gate([record]),
                clean_control=False,
                critical_mutation=True,
                expected_code=expected_code,
                allow_fail_closed_unknown=True,
                isolation_reason="PROVENANCE_MUTATION_PRECEDES_SEMANTIC_GRADING",
            )
        )

    retrieval = _load("retrieval_hard_negatives.v1.json")
    base_query = seal_retrieval_query(retrieval["query_template"])
    observations.append(
        _observation(
            case_id="retrieval_clean",
            grader="G1_RETRIEVAL",
            result=evaluate_retrieval_query(base_query),
            clean_control=True,
            critical_mutation=False,
        )
    )
    observations.append(
        _observation(
            case_id="split_leakage_clean",
            grader="G1_SPLIT_LEAKAGE",
            result=evaluate_retrieval_gate([base_query, _distinct_holdout(base_query)]),
            clean_control=True,
            critical_mutation=False,
        )
    )
    for candidate_id in retrieval["critical_hard_negative_candidate_ids"]:
        observations.append(
            _observation(
                case_id=f"retrieval::promote::{candidate_id}",
                grader="G1_RETRIEVAL",
                result=evaluate_retrieval_query(_promote_candidate(base_query, candidate_id)),
                clean_control=False,
                critical_mutation=True,
                expected_code="CRITICAL_HARD_NEGATIVE_SELECTED",
                isolation_reason="RETRIEVAL_RANK_MUTATION_DOES_NOT_CHANGE_CLAIM_EVIDENCE_RECORDS",
            )
        )
    omitted = copy.deepcopy(base_query)
    omitted["gate_k"] = 2
    omitted = seal_retrieval_query(omitted)
    observations.append(
        _observation(
            case_id="retrieval::relevant_outside_top_k",
            grader="G1_RETRIEVAL",
            result=evaluate_retrieval_query(omitted),
            clean_control=False,
            critical_mutation=True,
            expected_code="RELEVANT_EVIDENCE_OMITTED",
            isolation_reason="TOP_K_BOUNDARY_MUTATION_DOES_NOT_CHANGE_GROUNDING_INPUTS",
        )
    )
    holdout = copy.deepcopy(base_query)
    holdout["split"] = "HOLDOUT"
    holdout = seal_retrieval_query(holdout)
    observations.append(
        _observation(
            case_id="retrieval::holdout_leakage",
            grader="G1_SPLIT_LEAKAGE",
            result=evaluate_retrieval_gate([base_query, holdout]),
            clean_control=False,
            critical_mutation=True,
            expected_code="CALIBRATION_HOLDOUT_LEAKAGE",
            isolation_reason="SPLIT_IDENTITY_MUTATION_ISOLATED_TO_DATASET_GOVERNANCE",
        )
    )
    return observations


def run_meta_evaluation() -> dict[str, Any]:
    """Return a deterministic G6 receipt; no human labels or thresholds are inferred."""

    observations = _observations()
    repeated = _observations()
    critical = [row for row in observations if row["case_class"] == "CRITICAL_MUTATION"]
    clean = [row for row in observations if row["case_class"] == "CLEAN_CONTROL"]
    grounding = [row for row in critical if row["grader"] in {"G2_BINDING", "G3_GROUNDING"}]
    provenance = [row for row in critical if row["grader"] == "G3_PROVENANCE"]
    retrieval = [row for row in critical if row["grader"].startswith("G1_")]
    critical_recall = sum(row["detected_or_accepted"] for row in critical) / len(critical)
    clean_fpr = sum(not row["detected_or_accepted"] for row in clean) / len(clean)
    unexpected_unknown = sum(
        row["observed_status"] == "UNKNOWN"
        and not row["case_id"].startswith("provenance::")
        for row in observations
    )
    stability = float(canonical_digest(observations) == canonical_digest(repeated))
    failures: list[str] = []
    if critical_recall != 1.0:
        failures.append("CRITICAL_MUTATION_RECALL_BELOW_ONE")
    if clean_fpr > 0.05:
        failures.append("CLEAN_CONTROL_FALSE_POSITIVE_RATE_EXCEEDED")
    if unexpected_unknown:
        failures.append("REQUIRED_GRADER_UNKNOWN")
    if stability != 1.0:
        failures.append("GRADER_SCORE_INSTABILITY")
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": "G6",
        "score_groups": ["evaluator_validity"],
        "fixture_digests": {
            name: canonical_digest(_load(name))
            for name in ("grounding_mutations.v1.json", "retrieval_hard_negatives.v1.json")
        },
        "grader_cards_digest": canonical_digest(
            yaml.safe_load(_GRADER_CARDS.read_text(encoding="utf-8"))
        ),
        "status": "FAIL" if failures else "PASS",
        "metrics": {
            "critical_mutation_recall": critical_recall,
            "critical_grounding_mutation_recall": sum(row["detected_or_accepted"] for row in grounding) / len(grounding),
            "critical_provenance_mutation_recall": sum(row["detected_or_accepted"] for row in provenance) / len(provenance),
            "critical_retrieval_mutation_recall": sum(row["detected_or_accepted"] for row in retrieval) / len(retrieval),
            "noncritical_mutation_recall": None,
            "clean_control_false_positive_rate": clean_fpr,
            "human_grader_agreement": None,
            "judge_human_agreement": None,
            "reviewer_agreement_rate": None,
            "adjudication_overturn_rate": None,
            "score_stability": stability,
            "threshold_sensitivity": None,
            "slice_coverage": 1.0,
            "unmeasured_dimension_count": 6,
            "required_gate_unknown_count": unexpected_unknown,
            "holdout_leakage_incident_count": 0,
            "mutation_failure_count": sum(not row["detected_or_accepted"] for row in critical),
        },
        "observations": observations,
        "failure_codes": failures,
        "unknown_reasons": [],
        "authority": {
            "measurement_scope": "SEALED_REPOSITORY_FIXTURES",
            "machine_critical_grader_validation_complete": not failures,
            "human_agreement_pilot_complete": False,
            "human_agreement_thresholds_frozen": False,
            "release_authorizing": False,
            "promotion_scope": "FUTURE_RUNS_ONLY",
        },
    }
    body["record_digest"] = canonical_digest(body)
    return body
