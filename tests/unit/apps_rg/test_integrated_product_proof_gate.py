"""Integrated-R4 product proof gate — reject non-product paths; validate artifacts."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from apps_rg.runtime.integrated_product_proof_gate import (
    CONTRACT_TEST_ONLY_CLASSIFICATION,
    INTEGRATED_R4_PRODUCT_CLASSIFICATION,
    reject_non_integrated_product_claim,
    validate_integrated_product_proof,
)
from apps_rg.runtime.non_product_proof_stamp import (
    CI_LANE_DEV_HARNESS_CLASSIFICATION,
    DEMO_HARNESS_PROOF_CLASSIFICATION,
    ORCHESTRATOR_PROOF_CLASSIFICATION,
    PACKAGE_DISPOSITION_CLASSIFICATION,
    SECTION_L7_CORRELATION_CLASSIFICATION,
    demo_harness_non_product_stamp,
    orchestrator_non_product_stamp,
    package_rollup_non_product_stamp,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
R4_FIXTURE = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "r4_latest"
SECTION_RUN = (
    REPO_ROOT
    / "artifacts"
    / "apps_rg"
    / "runtime_proofs"
    / "executive_summary"
    / "real"
    / "exec_summary_20260520_151944"
)
CI_PROOF = REPO_ROOT / "artifacts" / "ci" / "apps_rg_e2e_runtime_proof.json"


def _copy_r4_fixture(dest: Path) -> None:
    if not R4_FIXTURE.is_dir():
        pytest.skip("r4_latest certification fixture missing")
    for name in R4_FIXTURE.iterdir():
        if name.is_file():
            shutil.copy2(name, dest / name.name)
    (dest / "whole_run_cache_preflight.json").write_text(
        json.dumps(
            {
                "cache_preflight_completed": True,
                "r1a_preflight_status": "miss",
                "r1b_preflight_status": "miss",
                "cache_result": "fallthrough_generation",
                "generation_spine_invocation_allowed": True,
                "route_family": "R4_SINGLE_ACTION",
            }
        ),
        encoding="utf-8",
    )


def test_section_only_run_dir_fails_product_proof():
    if not SECTION_RUN.is_dir():
        pytest.skip("section run dir missing")
    result = validate_integrated_product_proof(SECTION_RUN)
    assert result.status == "FAIL"
    assert result.section_mode is True
    assert SECTION_L7_CORRELATION_CLASSIFICATION in result.rejected_non_product_classifications or result.section_mode
    assert "section_mode" in result.decisive_reason


def test_orchestrator_offline_rollup_fails(tmp_path: Path):
    receipt = orchestrator_non_product_stamp()
    (tmp_path / "orchestrator_receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert ORCHESTRATOR_PROOF_CLASSIFICATION in result.rejected_non_product_classifications


def test_resume_package_x3_offline_rollup_fails(tmp_path: Path):
    receipt = package_rollup_non_product_stamp(package_x3_allow=True)
    (tmp_path / "resume_package_x3_disposition.json").write_text(json.dumps(receipt), encoding="utf-8")
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert PACKAGE_DISPOSITION_CLASSIFICATION in result.rejected_non_product_classifications
    assert result.package_x3_only is True


def test_demo_harness_fails(tmp_path: Path):
    stamp = demo_harness_non_product_stamp()
    (tmp_path / "demo_harness_proof_stamp.json").write_text(json.dumps(stamp), encoding="utf-8")
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert DEMO_HARNESS_PROOF_CLASSIFICATION in result.rejected_non_product_classifications


def test_ci_lane_dev_harness_fails(tmp_path: Path):
    stamp = {
        "proof_classification": CI_LANE_DEV_HARNESS_CLASSIFICATION,
        "product_certification": "NOT_CLAIMED",
        "integrated_r4_invoked": False,
    }
    (tmp_path / "apps_rg_e2e_runtime_proof.json").write_text(json.dumps(stamp), encoding="utf-8")
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert CI_LANE_DEV_HARNESS_CLASSIFICATION in result.rejected_non_product_classifications


def test_missing_how_trace_fails(tmp_path: Path):
    _copy_r4_fixture(tmp_path)
    (tmp_path / "agentic_core_how_trace.json").unlink()
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert "agentic_core_how_trace.json" in result.required_artifacts_missing


def test_missing_spine_proof_fails(tmp_path: Path):
    _copy_r4_fixture(tmp_path)
    (tmp_path / "agentic_core_spine_proof.json").unlink()
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert "agentic_core_spine_proof.json" in result.required_artifacts_missing


def test_package_x3_without_exit_x3_fails(tmp_path: Path):
    receipt = package_rollup_non_product_stamp(package_x3_allow=True)
    (tmp_path / "resume_package_x3_disposition.json").write_text(json.dumps(receipt), encoding="utf-8")
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert result.package_x3_only or "package_x3_only" in result.decisive_reason


def test_integrated_fixture_contract_test_only_without_canonical_command(tmp_path: Path):
    _copy_r4_fixture(tmp_path)
    blocked = validate_integrated_product_proof(tmp_path)
    assert blocked.status == "BLOCKED"
    assert blocked.proof_classification == INTEGRATED_R4_PRODUCT_CLASSIFICATION
    result = validate_integrated_product_proof(
        tmp_path,
        require_canonical_command_evidence=False,
    )
    assert result.status == "PASS"
    assert result.proof_classification == CONTRACT_TEST_ONLY_CLASSIFICATION
    assert result.canonical_entrypoint is False
    assert result.integrated_r4_invoked is True


def test_validator_reports_exact_missing_artifacts_and_decisive_reason(tmp_path: Path):
    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert result.required_artifacts_missing
    assert result.decisive_reason


def test_reject_non_integrated_product_claim_raises_on_certified_without_run_dir():
    with pytest.raises(ValueError, match="run_dir"):
        reject_non_integrated_product_claim(
            {"product_certification": "CERTIFIED", "proof_classification": "LIVE_RUNTIME_PROOF"},
            run_dir=None,
        )


def test_reject_non_integrated_product_claim_raises_on_orchestrator_stamp(tmp_path: Path):
    receipt = orchestrator_non_product_stamp()
    with pytest.raises(ValueError, match="non-product"):
        reject_non_integrated_product_claim(receipt, run_dir=tmp_path, context="test")
