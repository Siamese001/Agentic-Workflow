"""R4 manifest / Exit disposition consistency when L2 faults (apps_rg + core)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import V6Disposition


def _raw_request_minimal() -> dict:
    return {
        "transport": "ui",
        "method": "POST",
        "content_type": "application/json",
        "source_channel": "apps_rg_cli",
        "declared_schema": "apps_rg_jd_v1",
        "body_text": "{}",
        "tenant_id": "default",
        "user_id": "u-test",
        "target_company": "TestCo",
        "target_role": "Engineer",
        "jd_payload": {"title": "Eng", "description": "Do things"},
        "jd_hash": "abc123",
        "brief_hash": "def456",
        "resume_hash": "ghi789",
        "policy_hash": "a" * 64,
        "blueprint_hash": "b" * 64,
    }


def test_integrated_r4_l2_fault_coerces_x3_not_allow(tmp_path: Path) -> None:
    """Simulated L2 failure must not leave X3D on sealed R4 manifests."""
    from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
        run_integrated_r4_deterministic_pipeline,
    )

    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()

    def _failing_l2() -> dict:
        raise RuntimeError("FAILED_PROVIDER: simulated envelope failure")

    result = run_integrated_r4_deterministic_pipeline(
        raw_request=_raw_request_minimal(),
        app_name="apps_rg",
        artifact_dir=artifact_dir,
        l2_callable=_failing_l2,
        _test_mode=True,
    )

    assert result.fault.strip()
    assert result.x3_disposition == V6Disposition.DENY.value

    manifest = json.loads((artifact_dir / "r4_run_manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("l2_fault")
    assert manifest["x3_disposition"] == V6Disposition.DENY.value
    assert manifest["x3_disposition"] != V6Disposition.ALLOW.value

    x3_env = json.loads((artifact_dir / "x3_disposition_receipt.json").read_text(encoding="utf-8"))
    assert x3_env["payload"]["disposition"] == V6Disposition.DENY.value

    exit_rev = json.loads((artifact_dir / "exit_review_packet.json").read_text(encoding="utf-8"))
    assert exit_rev["payload"]["x3_disposition"] == V6Disposition.DENY.value

    assert not (artifact_dir / "outputs" / "generated_resume.json").exists()
    assert not (artifact_dir / "outputs" / "resume.docx").exists()


def test_augment_r4_manifest_adds_apps_rg_product_fields_on_fault(tmp_path: Path) -> None:
    from apps_rg.runtime.orchestration.canonical_dispatch import (
        _augment_r4_run_manifest_for_apps_rg_l2_fault,
    )

    base = {
        "producer_component": "test",
        "run_id": "r1",
        "request_id": "q1",
        "route_id": "R4_SINGLE_ACTION",
        "chain_kind": "R4_SINGLE_ACTION",
        "x3_disposition": V6Disposition.DENY.value,
        "terminal_r5": False,
        "l2_fault": "L2_EXECUTION_ERROR:RuntimeError:FAILED_PROVIDER: x",
        "artifact_hash": "sha256:00",
        "emitted_at": "2026-01-01T00:00:00Z",
    }
    man_path = tmp_path / "r4_run_manifest.json"
    man_path.write_text(json.dumps(base, indent=2) + "\n", encoding="utf-8")

    _augment_r4_run_manifest_for_apps_rg_l2_fault(
        tmp_path,
        fault=base["l2_fault"],
        x3_disposition=V6Disposition.DENY.value,
    )
    data = json.loads(man_path.read_text(encoding="utf-8"))
    assert data["apps_rg_product_outcome_authorized"] is False
    assert data["apps_rg_full_resume_generated"] is False
    assert data["apps_rg_generation_status"] == "FAILED_PROVIDER"
    assert data["apps_rg_terminal_class"] == "failure"
    assert data["apps_rg_required_resume_artifacts"]["outputs/generated_resume.json"] == "missing"
    assert data["apps_rg_required_resume_artifacts"]["outputs/resume.docx"] == "missing"
