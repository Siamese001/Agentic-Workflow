from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
import pytest
from referencing import Registry, Resource
import yaml


EVALS_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = EVALS_ROOT / "contracts" / "evaluation_contract.v2.yaml"
GATE_SCHEMA_PATH = EVALS_ROOT / "schemas" / "evaluation_gate_result.v1.schema.json"
REPORT_SCHEMA_PATH = EVALS_ROOT / "schemas" / "evaluation_report.v2.schema.json"

GATE_IDS = ("G1", "G2", "G3", "G4", "G5", "G6")
SCORE_GROUPS = (
    "retrieval_quality",
    "binding_accuracy",
    "factual_grounding",
    "section_quality",
    "whole_resume_quality",
    "runtime_repeatability",
    "evaluator_validity",
)
RESULT_STATES = {"PASS", "FAIL", "UNKNOWN", "NOT_MEASURED"}


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _schemas() -> tuple[dict[str, Any], dict[str, Any]]:
    return _load_json(GATE_SCHEMA_PATH), _load_json(REPORT_SCHEMA_PATH)


def _report_validator() -> Draft202012Validator:
    gate_schema, report_schema = _schemas()
    registry = Registry().with_resource(
        gate_schema["$id"],
        Resource.from_contents(gate_schema),
    )
    return Draft202012Validator(
        report_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def _gate_result(contract: dict[str, Any], gate_id: str) -> dict[str, Any]:
    gate = contract["gates"][gate_id]
    return {
        "schema_version": "apps_rg.evaluation_gate_result.v1",
        "contract_version": "apps_rg.evaluation_contract.v2",
        "gate_id": gate_id,
        "evaluation_question": gate["evaluation_question"],
        "score_groups": gate["score_groups"],
        "status": "PASS",
        "authority": {
            "classification": gate["threshold_authority"]["classification"],
            "human_review_required": gate["human_review_required"],
            "human_review_satisfied": gate["human_review_required"],
            "promotion_scope": gate["promotion_scope"],
            "release_authorizing": False,
            "authority_receipt_ref": "receipt:fixture",
        },
        "measurement_scope": gate["measurement_scope"],
        "evidence": [
            {
                "type": gate["required_evidence"][0]["type"],
                "artifact_id": f"artifact:{gate_id.lower()}",
                "digest": "sha256:" + (gate_id[-1].lower() * 64),
                "valid": True,
                "trusted": True,
            }
        ],
        "metrics": {
            gate["metrics"][0]["name"]: {
                "status": "PASS",
                "value": 1.0,
                "evidence_refs": [f"artifact:{gate_id.lower()}"],
            }
        },
        "failure_codes": [],
        "unknown_reasons": [],
        "unmeasured_reasons": [],
    }


def _complete_report() -> dict[str, Any]:
    contract = _load_yaml(CONTRACT_PATH)
    return {
        "schema_version": "apps_rg.evaluation_report.v2",
        "contract_version": "apps_rg.evaluation_contract.v2",
        "evaluation_id": "evaluation-contract-fixture",
        "generated_at": "2026-08-01T12:00:00Z",
        "artifact_set_digest": "sha256:" + ("a" * 64),
        "measurement_scope": "sealed_completed_artifacts",
        "gates": {
            gate_id: _gate_result(contract, gate_id) for gate_id in GATE_IDS
        },
        "score_groups": {
            group: {"status": "PASS", "metrics": {"fixture": 1.0}}
            for group in SCORE_GROUPS
        },
        "release_authority": {
            "current_run_authority_unchanged": True,
            "threshold_promotion_scope": "future_runs_only",
            "promotion_eligible": False,
            "blocking_gate_ids": [],
        },
        "failure_codes": [],
    }


def test_contract_defines_six_independent_gates_and_seven_score_groups() -> None:
    contract = _load_yaml(CONTRACT_PATH)

    assert contract["schema_version"] == "apps_rg.evaluation_contract.v2"
    assert tuple(contract["gates"]) == GATE_IDS
    assert tuple(contract["score_groups"]) == SCORE_GROUPS
    assert contract["principles"]["no_blended_overall_score"] is True
    assert contract["principles"]["missing_evidence_is_pass"] is False
    assert "overall_score" not in contract

    referenced_groups: set[str] = set()
    for gate_id, gate in contract["gates"].items():
        assert gate["evaluation_question"].endswith("?")
        assert gate["unit_of_analysis"]
        assert gate["required_evidence"]
        assert gate["metrics"]
        assert gate["threshold_authority"]["classification"] in {
            "advisory",
            "conditionally_release_authoritative",
            "release_authoritative",
        }
        assert isinstance(gate["human_review_required"], bool)
        assert gate["measurement_scope"]
        assert gate["promotion_scope"] in {"future_runs_only", "current_run", "none"}
        referenced_groups.update(gate["score_groups"])

        metric_names = [metric["name"] for metric in gate["metrics"]]
        assert len(metric_names) == len(set(metric_names)), gate_id
        assert all(metric["definition"] for metric in gate["metrics"])

    assert referenced_groups == set(SCORE_GROUPS)


def test_state_semantics_fail_closed_and_preserve_missing_distinctions() -> None:
    contract = _load_yaml(CONTRACT_PATH)

    assert set(contract["state_semantics"]) == RESULT_STATES
    assert contract["missing_evidence_disposition"] == "UNKNOWN"
    assert contract["unimplemented_lane_disposition"] == "NOT_MEASURED"
    for state in RESULT_STATES:
        semantics = contract["state_semantics"][state]
        assert semantics["meaning"]
        assert semantics["release_authorizing_by_itself"] is False


def test_authority_invariants_preserve_w6_w9_and_future_run_rules() -> None:
    authority = _load_yaml(CONTRACT_PATH)["authority_invariants"]

    assert authority == {
        "existing_w6_authority": "unchanged",
        "w9_authorized_pair_count": 6,
        "current_run_release_authority": "unchanged",
        "threshold_promotion_scope": "future_runs_only",
        "model_judge_authority_before_human_calibration": "advisory",
    }


def test_json_schemas_are_valid_and_accept_a_complete_named_gate_report() -> None:
    gate_schema, report_schema = _schemas()
    Draft202012Validator.check_schema(gate_schema)
    Draft202012Validator.check_schema(report_schema)

    _report_validator().validate(_complete_report())


@pytest.mark.parametrize("missing_gate", GATE_IDS)
def test_report_rejects_an_omitted_gate(missing_gate: str) -> None:
    report = _complete_report()
    report["gates"].pop(missing_gate)

    with pytest.raises(ValidationError):
        _report_validator().validate(report)


def test_report_rejects_blended_overall_score_and_gate_identity_drift() -> None:
    report = _complete_report()
    report["overall_score"] = 0.99
    with pytest.raises(ValidationError):
        _report_validator().validate(report)

    report = _complete_report()
    report["gates"]["G1"]["gate_id"] = "G2"
    with pytest.raises(ValidationError):
        _report_validator().validate(report)


def test_pass_requires_evidence_and_a_metric() -> None:
    report = _complete_report()
    report["gates"]["G3"]["evidence"] = []
    with pytest.raises(ValidationError):
        _report_validator().validate(report)

    report = _complete_report()
    report["gates"]["G3"]["metrics"] = {}
    with pytest.raises(ValidationError):
        _report_validator().validate(report)


@pytest.mark.parametrize(("field", "value"), (("valid", False), ("trusted", False)))
def test_pass_requires_valid_trusted_evidence(field: str, value: bool) -> None:
    report = _complete_report()
    report["gates"]["G3"]["evidence"][0][field] = value

    with pytest.raises(ValidationError):
        _report_validator().validate(report)


@pytest.mark.parametrize(
    ("status", "reason_field"),
    (("UNKNOWN", "unknown_reasons"), ("NOT_MEASURED", "unmeasured_reasons")),
)
def test_nonpass_missing_states_require_their_own_reason(
    status: str,
    reason_field: str,
) -> None:
    report = _complete_report()
    gate = report["gates"]["G5"]
    gate["status"] = status
    gate["evidence"] = []
    gate["metrics"] = {}

    with pytest.raises(ValidationError):
        _report_validator().validate(report)

    gate[reason_field] = [f"fixture {status.lower()} reason"]
    _report_validator().validate(report)


def test_fail_requires_a_stable_failure_code() -> None:
    report = _complete_report()
    gate = report["gates"]["G2"]
    gate["status"] = "FAIL"

    with pytest.raises(ValidationError):
        _report_validator().validate(report)

    gate["failure_codes"] = ["EXACT_BINDING_MISMATCH"]
    _report_validator().validate(report)


def test_promotion_eligibility_rejects_unknown_or_unmeasured_gates() -> None:
    report = _complete_report()
    report["release_authority"]["promotion_eligible"] = True
    report["gates"]["G6"]["status"] = "NOT_MEASURED"
    report["gates"]["G6"]["evidence"] = []
    report["gates"]["G6"]["metrics"] = {}
    report["gates"]["G6"]["unmeasured_reasons"] = ["grader lane unavailable"]

    with pytest.raises(ValidationError):
        _report_validator().validate(report)
