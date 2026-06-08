"""Runtime proof bundle — 99-style no-bypass verification for canonical apps_lic runs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_lic.runtime.dispatch.canonical_dispatch import (
    ROUTE_FAMILY_R4,
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.dispatch.runtime_proof_bundle import (
    FILENAME_RUNTIME_PROOF_BUNDLE,
    PROOF_BUNDLE_SCHEMA_VERSION,
    build_runtime_proof_bundle,
)


def _load_proof_bundle(run_dir: Path) -> dict:
    path = run_dir / FILENAME_RUNTIME_PROOF_BUNDLE
    assert path.is_file(), f"missing {FILENAME_RUNTIME_PROOF_BUNDLE}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_r4_managed_workflow_writes_passing_proof_bundle(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        run_id="proof_r4_01",
        request_id="req_proof_r4_01",
        manual_brief="Proof bundle R4 managed workflow for Acme Corp renewal.",
    )
    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "r4")
    assert result.route_family == ROUTE_FAMILY_R4
    assert result.terminal_r5 is False
    assert result.x3_disposition == "X3D"
    assert result.outcome_authorized is True

    bundle = _load_proof_bundle(result.artifact_dir)
    assert bundle["schema_version"] == PROOF_BUNDLE_SCHEMA_VERSION
    assert bundle["status"] == "PASS"
    assert bundle["terminal_r5"] is False
    assert bundle["violations"] == []
    assert bundle["no_bypass_assertions"]["shadow_files_absent"] is True
    assert bundle["no_bypass_assertions"]["canonical_dispatch_only"] is True
    assert bundle["no_bypass_assertions"]["bindings_under_apps_lic_runtime"] is True

    manifest = json.loads(
        (result.artifact_dir / "spine_run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["x3_disposition"] == "X3D"
    assert manifest["outcome_authorized"] is True
    assert FILENAME_RUNTIME_PROOF_BUNDLE in str(result.artifacts)


def test_r5_terminal_reduced_receipt_policy(tmp_path: Path) -> None:
    raw = build_cli_ingress_raw(manual_brief="", allow_research=False)
    result = run_canonical_apps_lic_spine(
        raw,
        artifact_root=tmp_path / "r5",
        skip_r3r4_research=True,
    )
    assert result.terminal_r5 is True
    assert result.x3_disposition == "DENY"

    bundle = _load_proof_bundle(result.artifact_dir)
    assert bundle["status"] == "PASS"
    assert bundle["terminal_r5"] is True
    assert bundle["checks"]["r5_forbidden_absent"] == []
    assert "terminal_r5_manifest_x3_deny_by_design" in bundle["checks"]["r5_terminal_exit_policy"]

    for forbidden in (
        "c0_final_evidence_contract.json",
        "pa_receipt.json",
        "l3_workflow_receipt.json",
        "l2_execution_receipt.json",
        "exit_disposition_receipt.json",
    ):
        assert not (result.artifact_dir / forbidden).exists()


def test_build_runtime_proof_bundle_detects_missing_r4_file(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "broken"
    artifact_dir.mkdir()
    manifest = {
        "request_id": "req_x",
        "run_id": "run_x",
        "route_family": "R4_MANAGED_DRAFT",
        "terminal_r5": False,
        "x3_disposition": "X3D",
        "outcome_authorized": True,
        "exit_status": "success",
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "stage_receipt_refs": [],
    }
    bundle = build_runtime_proof_bundle(artifact_dir, manifest, terminal_r5=False)
    assert bundle["status"] == "FAIL"
    assert any(v.startswith("missing_file:") for v in bundle["violations"])
