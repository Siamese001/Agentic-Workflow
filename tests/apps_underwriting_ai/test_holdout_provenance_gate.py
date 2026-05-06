from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_underwriting_holdout.py"
spec = importlib.util.spec_from_file_location("validate_underwriting_holdout", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)

BASE_EXAMPLE = {
    "decision_id": "uw-holdout-evidence_sufficiency-001",
    "dim_id": "evidence_sufficiency",
    "evidence_refs": ["financial::income_verified"],
    "ground_truth_score": 0.8,
    "human_score": 0.8,
    "labeled_at": "2026-05-05",
    "labeler_id": "uw-analyst-A1",
    "rationale_text": "Evidence is sufficient and cites verified income.",
}
DIMS = [
    "evidence_sufficiency",
    "feature_derivation_correctness",
    "policy_compliance",
    "explainability",
    "fairness",
]


def make_examples() -> list[dict]:
    examples = []
    for dim in DIMS:
        for i in range(20):
            row = copy.deepcopy(BASE_EXAMPLE)
            row["dim_id"] = dim
            row["decision_id"] = f"uw-holdout-{dim}-{i + 1:03d}"
            row["labeler_id"] = f"uw-analyst-A{(i % 5) + 1}"
            examples.append(row)
    return examples


def write_holdout(tmp_path: Path, examples: list[dict]) -> Path:
    path = tmp_path / "rationale_judge_holdout.yaml"
    path.write_text(yaml.safe_dump({"examples": examples}, sort_keys=False), encoding="utf-8")
    return path


def write_provenance(tmp_path: Path, holdout_path: Path, *, verified: bool = True) -> Path:
    path = tmp_path / "rationale_judge_holdout_provenance.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "holdout_file": str(holdout_path),
                "holdout_file_sha256": validator.sha256_file(holdout_path),
                "holdout_dataset_status": "VERIFIED_ANALYST_ATTESTED" if verified else "PROVENANCE_PENDING",
                "attestation": {
                    "attestation_owner": "Underwriting QA Owner" if verified else None,
                    "attestation_owner_role": "Qualified underwriting reviewer" if verified else None,
                    "attestation_date": "2026-05-06" if verified else None,
                    "independent_human_review_confirmed": verified,
                    "qualified_underwriting_analyst_confirmed": verified,
                    "no_pii_confirmed": verified,
                    "no_real_applicant_data_confirmed": verified,
                    "no_live_lender_thresholds_confirmed": verified,
                    "no_llm_or_cascade_authored_labels_confirmed": verified,
                    "analyst_labeling_or_review_method": "Independent review of 100 examples" if verified else None,
                    "calibration_method": "Rubric calibration session" if verified else None,
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def test_valid_100_examples_20_per_dimension_schema_passes(tmp_path: Path):
    holdout = write_holdout(tmp_path, make_examples())
    errors, warnings, summary = validator.validate_holdout(holdout)
    assert errors == []
    assert "HOLDOUT_GROUND_TRUTH_EQUALS_HUMAN_SCORE" in warnings
    assert summary["example_count"] == 100
    assert all(count == 20 for count in summary["dimension_counts"].values())


def test_missing_provenance_prevents_w1_complete(tmp_path: Path):
    holdout = write_holdout(tmp_path, make_examples())
    errors, _, _ = validator.validate_provenance(tmp_path / "missing.yaml", validator.sha256_file(holdout))
    assert any("provenance file missing" in err for err in errors)


def test_pending_provenance_prevents_w1_complete(tmp_path: Path):
    holdout = write_holdout(tmp_path, make_examples())
    provenance = write_provenance(tmp_path, holdout, verified=False)
    errors, _, _ = validator.validate_provenance(provenance, validator.sha256_file(holdout))
    assert any("VERIFIED_ANALYST_ATTESTED" in err for err in errors)


def test_verified_provenance_passes(tmp_path: Path):
    holdout = write_holdout(tmp_path, make_examples())
    provenance = write_provenance(tmp_path, holdout, verified=True)
    errors, _, summary = validator.validate_provenance(provenance, validator.sha256_file(holdout))
    assert errors == []
    assert summary["provenance_status"] == "VERIFIED_ANALYST_ATTESTED"


def test_duplicate_decision_id_fails(tmp_path: Path):
    examples = make_examples()
    examples[1]["decision_id"] = examples[0]["decision_id"]
    holdout = write_holdout(tmp_path, examples)
    errors, _, _ = validator.validate_holdout(holdout)
    assert any("duplicate decision_id" in err for err in errors)


def test_missing_human_score_fails(tmp_path: Path):
    examples = make_examples()
    examples[0].pop("human_score")
    holdout = write_holdout(tmp_path, examples)
    errors, _, _ = validator.validate_holdout(holdout)
    assert any("missing required fields" in err and "human_score" in err for err in errors)


def test_out_of_range_human_score_fails(tmp_path: Path):
    examples = make_examples()
    examples[0]["human_score"] = 1.4
    holdout = write_holdout(tmp_path, examples)
    errors, _, _ = validator.validate_holdout(holdout)
    assert any("human_score must be numeric" in err for err in errors)


def test_missing_labeler_id_fails(tmp_path: Path):
    examples = make_examples()
    examples[0]["labeler_id"] = ""
    holdout = write_holdout(tmp_path, examples)
    errors, _, _ = validator.validate_holdout(holdout)
    assert any("labeler_id must be non-empty" in err for err in errors)


def test_ground_truth_equals_human_score_warns_but_does_not_fail(tmp_path: Path):
    holdout = write_holdout(tmp_path, make_examples())
    errors, warnings, _ = validator.validate_holdout(holdout)
    assert errors == []
    assert warnings == ["HOLDOUT_GROUND_TRUTH_EQUALS_HUMAN_SCORE"]
