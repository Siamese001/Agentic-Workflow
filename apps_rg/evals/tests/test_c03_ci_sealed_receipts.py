from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from apps_rg.evals.c03_ci_ratchet import (
    GATE_RECEIPT_SCHEMA_VERSION,
    REQUIRED_SCORE_GROUPS,
    build_ratchet_receipt,
    seal_gate_receipt,
)


def _junit(path: Path, *, baseline: bool = False) -> None:
    name = (
        "test_agentic_core_does_not_embed_resume_graph_skill_authority_literals"
        if baseline
        else "test_strict"
    )
    classname = "TestAgenticCoreGraphSkillBoundary" if baseline else "TestStrict"
    failure = '<failure message="augmented_skills_graph">known debt</failure>' if baseline else ""
    failures = 1 if baseline else 0
    path.write_text(
        f'<testsuite tests="1" failures="{failures}" errors="0" skipped="0">'
        f'<testcase classname="{classname}" name="{name}">{failure}</testcase></testsuite>',
        encoding="utf-8",
    )


def _receipts() -> dict[str, dict]:
    gate_ids = {
        "retrieval_quality": "G1",
        "binding_accuracy": "G2",
        "factual_grounding": "G3",
        "section_quality": "G4",
        "whole_resume_quality": "G4",
        "runtime_repeatability": "G5",
        "evaluator_validity": "G6",
    }
    return {
        score_group: seal_gate_receipt(
            {
                "schema_version": GATE_RECEIPT_SCHEMA_VERSION,
                "score_group": score_group,
                "gate_id": gate_ids[score_group],
                "source_receipt_digest": f"{index + 1:064x}",
                "status": "PASS",
                "metrics": {"measured": 1},
                "critical_failure_count": 0,
                "required_unknown_count": 0,
                "holdout_leakage_incidents": 0,
                "unsupported_material_claim_count": 0,
                "mutation_failure_count": 0,
                "baseline_signature": f"baseline::{score_group}::v1",
                "record_digest": "",
            }
        )
        for index, score_group in enumerate(REQUIRED_SCORE_GROUPS)
    }


@pytest.fixture
def junit_paths(tmp_path: Path) -> tuple[Path, Path]:
    strict = tmp_path / "strict.xml"
    baseline = tmp_path / "baseline.xml"
    _junit(strict)
    _junit(baseline, baseline=True)
    return strict, baseline


def _build(junit_paths: tuple[Path, Path], receipts: dict[str, dict], **kwargs: object) -> dict:
    strict, baseline = junit_paths
    kwargs.setdefault(
        "expected_baselines",
        {name: value["baseline_signature"] for name, value in receipts.items()},
    )
    return build_ratchet_receipt(
        strict_junit=strict,
        baseline_junit=baseline,
        source_commit="source",
        base_commit="base",
        evaluation_receipts=receipts,
        **kwargs,
    )


def test_all_seven_valid_receipts_pass(junit_paths: tuple[Path, Path]) -> None:
    gate_receipts = _receipts()
    schema = json.loads(
        (Path(__file__).resolve().parents[1] / "schemas" / "ci_gate_receipt.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(schema)
    for gate_receipt in gate_receipts.values():
        Draft202012Validator(schema).validate(gate_receipt)
    receipt = _build(junit_paths, gate_receipts)
    assert receipt["status"] == "PASS"
    assert receipt["evaluation_receipt_mode"] == "SEALED_ALL_SCORE_GROUPS"
    assert set(receipt["evaluation_receipts"]) == set(REQUIRED_SCORE_GROUPS)


def test_missing_receipt_fails(junit_paths: tuple[Path, Path]) -> None:
    receipts = _receipts()
    del receipts["runtime_repeatability"]
    receipt = _build(junit_paths, receipts)
    assert receipt["status"] == "FAIL"
    assert "evaluation_receipt_missing::runtime_repeatability" in receipt["failure_codes"]


def test_non_mapping_receipt_bundle_fails_closed(junit_paths: tuple[Path, Path]) -> None:
    strict, baseline = junit_paths
    receipt = build_ratchet_receipt(
        strict_junit=strict,
        baseline_junit=baseline,
        source_commit="source",
        base_commit="base",
        evaluation_receipts=[],  # type: ignore[arg-type]
    )
    assert receipt["status"] == "FAIL"
    assert "evaluation_receipt_bundle_invalid" in receipt["failure_codes"]


def test_expected_baseline_bundle_is_required(junit_paths: tuple[Path, Path]) -> None:
    strict, baseline = junit_paths
    receipt = build_ratchet_receipt(
        strict_junit=strict,
        baseline_junit=baseline,
        source_commit="source",
        base_commit="base",
        evaluation_receipts=_receipts(),
    )
    assert receipt["status"] == "FAIL"
    assert "evaluation_baseline_bundle_missing" in receipt["failure_codes"]


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("status", "UNKNOWN", "required_status_unknown"),
        ("required_unknown_count", 1, "required_unknown"),
        ("holdout_leakage_incidents", 1, "holdout_leakage"),
        ("unsupported_material_claim_count", 1, "unsupported_material_claim"),
        ("mutation_failure_count", 1, "mutation_failure"),
        ("critical_failure_count", 1, "critical_failure"),
    ],
)
def test_governed_failures_fail_ratchet(
    junit_paths: tuple[Path, Path], field: str, value: object, code: str
) -> None:
    receipts = _receipts()
    target = dict(receipts["factual_grounding"])
    target[field] = value
    receipts["factual_grounding"] = seal_gate_receipt(target)
    receipt = _build(junit_paths, receipts)
    assert receipt["status"] == "FAIL"
    assert f"evaluation_receipt::factual_grounding::{code}" in receipt["failure_codes"]


def test_tampered_receipt_digest_fails(junit_paths: tuple[Path, Path]) -> None:
    receipts = _receipts()
    receipts["section_quality"]["metrics"]["measured"] = 2
    receipt = _build(junit_paths, receipts)
    assert "evaluation_receipt::section_quality::record_digest_invalid" in receipt["failure_codes"]


def test_score_group_gate_identity_mismatch_fails(junit_paths: tuple[Path, Path]) -> None:
    receipts = _receipts()
    target = dict(receipts["retrieval_quality"])
    target["gate_id"] = "G6"
    receipts["retrieval_quality"] = seal_gate_receipt(target)
    receipt = _build(junit_paths, receipts)
    assert "evaluation_receipt::retrieval_quality::gate_id_mismatch" in receipt["failure_codes"]


def test_unexpected_baseline_signature_fails(junit_paths: tuple[Path, Path]) -> None:
    receipts = _receipts()
    baselines = {name: value["baseline_signature"] for name, value in receipts.items()}
    baselines["retrieval_quality"] = "different"
    receipt = _build(junit_paths, receipts, expected_baselines=baselines)
    assert "evaluation_receipt::retrieval_quality::unexpected_baseline_signature" in receipt["failure_codes"]


def test_cli_consumes_sealed_receipt_bundle(junit_paths: tuple[Path, Path], tmp_path: Path) -> None:
    strict, baseline = junit_paths
    receipts_path = tmp_path / "receipts.json"
    baselines_path = tmp_path / "baselines.json"
    out = tmp_path / "ratchet.json"
    receipts = _receipts()
    receipts_path.write_text(json.dumps(receipts), encoding="utf-8")
    baselines_path.write_text(
        json.dumps({name: value["baseline_signature"] for name, value in receipts.items()}),
        encoding="utf-8",
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[3])
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg.evals.c03_ci_ratchet",
            "--strict-junit",
            str(strict),
            "--baseline-junit",
            str(baseline),
            "--source-commit",
            "source",
            "--base-commit",
            "base",
            "--evaluation-receipts",
            str(receipts_path),
            "--expected-baselines",
            str(baselines_path),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(out.read_text(encoding="utf-8"))["status"] == "PASS"
