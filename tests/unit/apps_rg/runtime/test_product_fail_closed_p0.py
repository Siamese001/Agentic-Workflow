"""P0 product fail-closed: pointers, product quality status, phase-1 bar."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_rg.l2_recipe.modular_lane_adapter import resolve_latest_lane_run_dir
from apps_rg.runtime.product_output_policy import (
    lane_run_dir_meets_product_bar,
    phase1_dispatch_hard_failed,
)
from apps_rg.runtime.runtime_proof_layout import resolve_accepted_real_rollup_run_dir
from apps_rg.l2_recipe.modular_resume_generation import ModularResumeInputPackage, ModularResumeProfile, run_modular_resume_generation
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import infer_product_quality_blocked_or_mock
from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import REPO, unify_bullets_parsed_from_mock


@pytest.fixture
def product_fail_closed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.setenv("APPS_RG_WHOLE_RUN_ENVELOPE", "1")


def test_infer_product_quality_fail_on_blocked_when_fail_closed(
    product_fail_closed_env: None,
) -> None:
    status, reason = infer_product_quality_blocked_or_mock(
        runtime_generation_status="BLOCKED_UPSTREAM_NOT_FINALIZED",
        x2_failed_gate_ids=[],
        pass_reason="unused",
    )
    assert status == "FAIL"
    assert "REAL_LLM" in reason


def test_resolve_latest_lane_run_dir_rejects_latest_real_only(
    product_fail_closed_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sections_root = REPO / "artifacts/apps_rg/runtime_proofs/contract_harness/_p0_pointer_strict"
    lane_base = sections_root / "headline"
    run_dir = lane_base / "real" / "headline_failed_attempt"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "l2_output.json").write_text(
        json.dumps(
            {
                "section_id": "headline",
                "runtime_generation_status": "REAL_LLM",
                "product_quality_status": "FAIL",
                "headline_line": "x",
            }
        ),
        encoding="utf-8",
    )
    rel = os.path.relpath(run_dir, REPO).replace("\\", "/")
    (lane_base / "latest_real_run.json").write_text(json.dumps({"run_dir": rel}), encoding="utf-8")

    monkeypatch.setenv("APPS_RG_MODULAR_R4_SECTIONS_ROOT", str(sections_root.resolve()))
    with pytest.raises(FileNotFoundError, match="latest_successful|product bar|pointer"):
        resolve_latest_lane_run_dir(REPO, sections_root, "headline")


def test_migration_scan_disabled_on_product_fail_closed(
    product_fail_closed_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lane = "_p0_migration_scan_headline"
    real_root = REPO / "artifacts/apps_rg/runtime_proofs" / lane / "real"
    real_root.mkdir(parents=True, exist_ok=True)
    orphan = real_root / f"{lane}_orphan_mtime"
    orphan.mkdir(parents=True, exist_ok=True)
    (orphan / "l2_output.json").write_text(
        json.dumps(
            {
                "section_id": lane,
                "runtime_generation_status": "REAL_LLM",
                "product_quality_status": "PASS",
            }
        ),
        encoding="utf-8",
    )
    (orphan / "provider_request.json").write_text(
        json.dumps({"provider_requested": "retired_provider_profile"}),
        encoding="utf-8",
    )
    rd, tag = resolve_accepted_real_rollup_run_dir(REPO, lane)
    assert rd is None
    assert "product_fail_closed" in tag


def test_phase1_dispatch_hard_failed_detects_fault() -> None:
    # Only transport-level ``fault`` strings cascade-abort phase1. Per Author-Gate decision
    # dec_19e6e344d5db19589 (E2E-05 lane isolation), an individual lane X3_BLOCK
    # (``exit_status=='error'``) does NOT poison independent downstream lanes, so it must
    # NOT report a hard phase1 failure.
    assert phase1_dispatch_hard_failed({"fault": "upstream_not_finalized"}) is True
    assert phase1_dispatch_hard_failed({"exit_status": "error"}) is False
    assert phase1_dispatch_hard_failed({"exit_status": "success"}) is False


def test_lane_run_dir_meets_product_bar_pass(
    product_fail_closed_env: None,
) -> None:
    parsed, _ = unify_bullets_parsed_from_mock()
    run_dir = (
        REPO
        / "artifacts/apps_rg/runtime_proofs/contract_harness/_p0_lane_bar_pass/unify_bullets/real/run1"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "l2_output.json").write_text(
        json.dumps(
            {
                "section_id": "unify_bullets",
                "runtime_generation_status": "REAL_LLM",
                "product_quality_status": "PASS",
                "bullets": parsed["bullets"],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW"}),
        encoding="utf-8",
    )
    (run_dir / "provider_request.json").write_text(
        json.dumps({"provider_requested": "external_claude"}),
        encoding="utf-8",
    )
    ok, reason = lane_run_dir_meets_product_bar(run_dir)
    assert ok is True
    assert reason == "ok"


def test_lane_run_dir_accepts_external_openai_product_bar(
    product_fail_closed_env: None,
) -> None:
    parsed, _ = unify_bullets_parsed_from_mock()
    run_dir = (
        REPO
        / "artifacts/apps_rg/runtime_proofs/contract_harness/_p0_lane_bar_pass/unify_bullets/real/run_openai"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "l2_output.json").write_text(
        json.dumps(
            {
                "section_id": "unify_bullets",
                "runtime_generation_status": "REAL_LLM",
                "product_quality_status": "PASS",
                "bullets": parsed["bullets"],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW"}),
        encoding="utf-8",
    )
    (run_dir / "provider_request.json").write_text(
        json.dumps({"provider_requested": "external_openai"}),
        encoding="utf-8",
    )
    ok, reason = lane_run_dir_meets_product_bar(run_dir)
    assert ok is True
    assert reason == "ok"


def test_lane_run_dir_rejects_phase0_synthetic_stub(product_fail_closed_env: None) -> None:
    run_dir = (
        REPO
        / "artifacts/apps_rg/runtime_proofs/contract_harness/_p0_phase0_stub/unify_bullets/real/phase0_synthetic"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "l2_output.json").write_text(
        json.dumps(
            {
                "section_id": "unify_bullets",
                "runtime_generation_status": "REAL_LLM",
                "product_quality_status": "PHASE0_SYNTHETIC",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "x3_disposition.json").write_text(json.dumps({"x3_code": "X3_ALLOW"}), encoding="utf-8")
    (run_dir / "provider_request.json").write_text(
        json.dumps({"provider_requested": "retired_provider_profile"}),
        encoding="utf-8",
    )
    ok, reason = lane_run_dir_meets_product_bar(run_dir)
    assert ok is False
    assert "phase0" in reason


def test_modular_phase0_blocked_on_product_fail_closed(
    product_fail_closed_env: None,
) -> None:
    art = REPO / "artifacts/apps_rg/runtime_proofs/contract_harness/_p0_phase0_modular_block"
    art.mkdir(parents=True, exist_ok=True)
    pkg = ModularResumeInputPackage(repo_root=REPO)
    result = run_modular_resume_generation(
        pkg,
        art,
        "p0-phase0-block-test",
        profile=ModularResumeProfile(
            run_phase0_synthetic_assembly=True,
            phase1_invoke_real_lanes=False,
            validate_rg_output_fixture=False,
        ),
    )
    assert result.decisive_status == "FAIL"
    assert "phase0_synthetic_not_permitted" in (result.failure_reason or "")
    block_doc = art / "modular_r4" / "phase0_product_fail_closed_block.json"
    assert block_doc.is_file()
