from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from apps_rg.evals.meta_eval import run_meta_evaluation
from apps_rg.evals.resume_graph.reporting import canonical_digest


def test_real_critical_graders_detect_all_controlled_mutations() -> None:
    receipt = run_meta_evaluation()
    schema = json.loads(
        (Path(__file__).resolve().parents[1] / "schemas" / "receipt.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(receipt)
    assert receipt["status"] == "PASS"
    assert receipt["metrics"]["critical_mutation_recall"] == 1.0
    assert receipt["metrics"]["critical_grounding_mutation_recall"] == 1.0
    assert receipt["metrics"]["critical_provenance_mutation_recall"] == 1.0
    assert receipt["metrics"]["critical_retrieval_mutation_recall"] == 1.0
    assert receipt["metrics"]["mutation_failure_count"] == 0


def test_clean_controls_pass_without_false_positives() -> None:
    receipt = run_meta_evaluation()
    clean = [row for row in receipt["observations"] if row["case_class"] == "CLEAN_CONTROL"]
    assert clean
    assert all(row["detected_or_accepted"] for row in clean)
    assert {row["grader"] for row in clean} == {
        "G1_RETRIEVAL",
        "G1_SPLIT_LEAKAGE",
        "G2_BINDING",
        "G3_GROUNDING",
        "G3_PROVENANCE",
    }
    assert receipt["metrics"]["clean_control_false_positive_rate"] == 0.0


def test_intended_fail_closed_unknown_is_not_required_gate_unknown() -> None:
    receipt = run_meta_evaluation()
    provenance = [
        row for row in receipt["observations"] if row["case_id"].startswith("provenance::")
    ]
    assert any(row["observed_status"] == "UNKNOWN" for row in provenance)
    assert receipt["metrics"]["required_gate_unknown_count"] == 0


def test_human_agreement_is_explicitly_unmeasured_and_non_authorizing() -> None:
    receipt = run_meta_evaluation()
    assert receipt["metrics"]["human_grader_agreement"] is None
    assert receipt["metrics"]["judge_human_agreement"] is None
    assert receipt["authority"]["human_agreement_thresholds_frozen"] is False
    assert receipt["authority"]["release_authorizing"] is False


def test_receipt_digest_and_repeated_score_are_stable() -> None:
    receipt = run_meta_evaluation()
    assert receipt["record_digest"] == canonical_digest(
        {key: value for key, value in receipt.items() if key != "record_digest"}
    )
    assert receipt["metrics"]["score_stability"] == 1.0


def test_meta_eval_cli(tmp_path: Path) -> None:
    output = tmp_path / "meta.json"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[4])
    completed = subprocess.run(
        [sys.executable, "-m", "apps_rg.evals.meta_eval", "--out", str(output)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "PASS"
