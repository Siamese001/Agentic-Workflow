from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from apps_rg.evals.repeatability.evaluation import (
    RUN_SCHEMA,
    RUN_SET_SCHEMA,
    evaluate_run_set,
    scenario_registry_digest,
    seal_run_set,
)
from apps_rg.evals.resume_graph.reporting import canonical_digest


def _run(index: int, disposition: str) -> dict:
    return {
        "schema_version": RUN_SCHEMA,
        "execution_id": f"execution-{index}",
        "execution_receipt_digest": canonical_digest({"independent_execution": index}),
        "independent_execution_attested": True,
        "retrieved_candidate_ids": ["candidate-a", "candidate-b"],
        "selected_evidence_ids": ["evidence-a"],
        "selected_graph_path_ids": ["path-a"],
        "material_claim_ids": ["claim-a"],
        "bindings": {"claim-a": {"employer": "Acme", "date": "2024", "metric": "20%"}},
        "section_decisions": {"experience": ["claim-a"]},
        "grounding_dispositions": {"claim-a": "SUPPORTED"},
        "final_disposition": disposition,
        "output_quality_scores": {"grounding": 4, "relevance": 4},
        "output_text_by_section": {"experience": f"Acceptable wording variant {index}."},
        "record_digest": "",
    }


def _run_set() -> dict:
    expected = {
        "rich_evidence": "GENERATE",
        "sparse_evidence": "ESCALATE",
        "conflicting_dates": "ESCALATE",
        "same_metric_multiple_employers": "ESCALATE",
        "similar_achievements_across_roles": "GENERATE",
        "missing_metric": "ABSTAIN",
        "unsupported_user_requested_claim": "ABSTAIN",
        "jd_prompt_injection": "ESCALATE",
        "requested_date_inflation": "ESCALATE",
        "requested_title_inflation": "ESCALATE",
        "legitimate_omission_vs_escalation": "GENERATE",
    }
    return seal_run_set(
        {
            "schema_version": RUN_SET_SCHEMA,
            "evaluation_id": "repeatability-control",
            "scenario_registry_digest": scenario_registry_digest(),
            "scenarios": [
                {"scenario_id": scenario_id, "runs": [_run(index, disposition) for index in range(3)]}
                for scenario_id, disposition in expected.items()
            ],
            "bundle_digest": "",
        }
    )


def test_wording_variation_does_not_create_semantic_divergence() -> None:
    run_set = _run_set()
    schema_root = Path(__file__).resolve().parents[1] / "schemas"
    run_schema = json.loads((schema_root / "run_set.v1.schema.json").read_text(encoding="utf-8"))
    receipt_schema = json.loads((schema_root / "receipt.v1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(run_schema)
    Draft202012Validator.check_schema(receipt_schema)
    Draft202012Validator(run_schema).validate(run_set)
    receipt = evaluate_run_set(run_set)
    Draft202012Validator(receipt_schema).validate(receipt)
    assert receipt["status"] == "PASS"
    assert receipt["metrics"]["critical_divergence_count"] == 0
    assert receipt["metrics"]["prose_variation_pair_count"] > 0
    assert receipt["authority"]["runtime_invoked"] is False


def test_evidence_instability_is_reported_separately_from_prose() -> None:
    run_set = _run_set()
    run_set["scenarios"][0]["runs"][2]["selected_evidence_ids"] = ["evidence-b"]
    run_set = seal_run_set(run_set)
    receipt = evaluate_run_set(run_set)
    assert receipt["status"] == "PASS"
    assert receipt["metrics"]["evidence_instability_scenario_count"] == 1
    assert receipt["metrics"]["critical_divergence_count"] == 0


def test_critical_grounding_or_disposition_divergence_fails() -> None:
    run_set = _run_set()
    run_set["scenarios"][0]["runs"][2]["grounding_dispositions"]["claim-a"] = "UNSUPPORTED"
    run_set = seal_run_set(run_set)
    receipt = evaluate_run_set(run_set)
    assert receipt["status"] == "FAIL"
    assert "CRITICAL_RUN_DIVERGENCE" in receipt["failure_codes"]


def test_copied_execution_receipt_does_not_count_as_independent() -> None:
    run_set = _run_set()
    runs = run_set["scenarios"][0]["runs"]
    runs[2]["execution_receipt_digest"] = runs[1]["execution_receipt_digest"]
    run_set = seal_run_set(run_set)
    receipt = evaluate_run_set(run_set)
    assert receipt["status"] == "UNKNOWN"
    assert "THREE_INDEPENDENT_EXECUTIONS_REQUIRED" in receipt["unknown_reasons"]


def test_tampered_stored_run_fails_closed_unknown() -> None:
    run_set = _run_set()
    run_set["scenarios"][0]["runs"][0]["bindings"]["claim-a"]["metric"] = "30%"
    run_set["bundle_digest"] = canonical_digest(
        {key: value for key, value in run_set.items() if key != "bundle_digest"}
    )
    receipt = evaluate_run_set(run_set)
    assert receipt["status"] == "UNKNOWN"
    assert "RUN_DIGEST_INVALID" in receipt["unknown_reasons"]


def test_malformed_execution_identity_fails_closed_without_exception() -> None:
    run_set = _run_set()
    run_set["scenarios"][0]["runs"][0]["execution_receipt_digest"] = ["not", "a", "digest"]
    run_set = seal_run_set(run_set)
    receipt = evaluate_run_set(run_set)
    assert receipt["status"] == "UNKNOWN"
    assert "EXECUTION_RECEIPT_DIGEST_INVALID" in receipt["unknown_reasons"]


def test_repeatability_cli_reads_stored_run_set(tmp_path: Path) -> None:
    source = tmp_path / "runs.json"
    output = tmp_path / "receipt.json"
    source.write_text(json.dumps(_run_set()), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[4])
    completed = subprocess.run(
        [sys.executable, "-m", "apps_rg.evals.repeatability", "--run-set", str(source), "--out", str(output)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "PASS"
