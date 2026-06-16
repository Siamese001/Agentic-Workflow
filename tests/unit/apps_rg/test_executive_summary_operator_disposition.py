"""Unit tests for executive_summary operator disposition tiers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.cli_section_execution_report import (
    build_section_cli_execution_report_payload,
    section_lane_process_exit_code,
)
from apps_rg.runtime.sections.executive_summary_operator_disposition import (
    compute_executive_summary_operator_disposition,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import judge_regeneration_enabled


def _write_run_artifacts(
    tmp_path: Path,
    *,
    x3_code: str = "X3_REVIEW_JUDGE_SOFT_FAIL",
    x3_pass: bool = False,
    product_quality_status: str = "PASS",
    runtime_generation_status: str = "REAL_LLM",
) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "run_manifest.json").write_text(
        json.dumps(
            {
                "section_id": "executive_summary",
                "runtime_generation_status": runtime_generation_status,
                "proof_eligible": False,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": x3_code,
                "pass": x3_pass,
                "product_quality_status": product_quality_status,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "l2_output.json").write_text(
        json.dumps({"runtime_generation_status": runtime_generation_status}),
        encoding="utf-8",
    )
    return tmp_path


def test_draft_ready_soft_fail_exit_zero(tmp_path: Path) -> None:
    rd = _write_run_artifacts(tmp_path)
    op = compute_executive_summary_operator_disposition(
        artifact_dir=rd,
        x3_loaded=json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8")),
        manifest_loaded=json.loads((rd / "run_manifest.json").read_text(encoding="utf-8")),
        cli_path_pass=True,
    )
    assert op.draft_ready is True
    assert op.certified is False
    assert op.disposition_tier == "draft"
    assert op.process_exit_code == 0

    result = {
        "exit_status": "error",
        "outcome_authorized": False,
        "artifact_dir": str(rd),
        "fault": "",
    }
    assert (
        section_lane_process_exit_code(
            result=result,
            allow_non_allow_exit_zero_effective=False,
            section_id="executive_summary",
        )
        == 0
    )


def test_certified_exit_zero(tmp_path: Path) -> None:
    rd = _write_run_artifacts(
        tmp_path,
        x3_code="X3_ALLOW",
        x3_pass=True,
    )
    op = compute_executive_summary_operator_disposition(
        artifact_dir=rd,
        x3_loaded=json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8")),
        manifest_loaded=json.loads((rd / "run_manifest.json").read_text(encoding="utf-8")),
        cli_path_pass=True,
    )
    assert op.certified is True
    assert op.draft_ready is True
    assert op.disposition_tier == "certified"
    assert op.process_exit_code == 0


def test_x2_fail_not_draft_ready(tmp_path: Path) -> None:
    rd = _write_run_artifacts(tmp_path, x3_code="X3_BLOCK", product_quality_status="FAIL")
    op = compute_executive_summary_operator_disposition(
        artifact_dir=rd,
        x3_loaded=json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8")),
        manifest_loaded=json.loads((rd / "run_manifest.json").read_text(encoding="utf-8")),
        cli_path_pass=True,
    )
    assert op.draft_ready is False
    assert op.process_exit_code == 1


def test_blocked_generation_not_draft_ready(tmp_path: Path) -> None:
    rd = _write_run_artifacts(
        tmp_path,
        runtime_generation_status="BLOCKED",
        x3_code="X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
    )
    op = compute_executive_summary_operator_disposition(
        artifact_dir=rd,
        x3_loaded=json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8")),
        manifest_loaded=json.loads((rd / "run_manifest.json").read_text(encoding="utf-8")),
        cli_path_pass=True,
    )
    assert op.draft_ready is False
    assert op.process_exit_code == 1


def test_cli_report_emits_operator_status(tmp_path: Path) -> None:
    rd = _write_run_artifacts(tmp_path)
    result = {
        "exit_status": "error",
        "outcome_authorized": False,
        "artifact_dir": str(rd),
        "fault": "",
    }
    payload = build_section_cli_execution_report_payload(
        result=result,
        lane_provider_resolution_source=None,
        allow_non_allow_exit_zero_effective=False,
        process_exit_code=0,
    )
    assert payload["operator_status"] == "DRAFT_READY"
    assert payload["draft_ready"] is True
    assert payload["expected_nonzero_exit"] is False
    assert payload["process_exit_code"] == 0


def test_judge_regen_default_on_product_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", raising=False)
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    assert judge_regeneration_enabled() is True


def test_judge_regen_opt_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "0")
    assert judge_regeneration_enabled() is False
