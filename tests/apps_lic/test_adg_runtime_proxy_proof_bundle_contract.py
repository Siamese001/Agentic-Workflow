"""W8 ADG runtime-proxy coverage for runtime proof-bundle contracts."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from apps_lic.engines.message_type_requirement_gate import MESSAGE_GENERAL_INTRO
from apps_lic.runtime.dispatch import stage_receipts as sr
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.dispatch.runtime_proof_bundle import (
    FILENAME_RUNTIME_PROOF_BUNDLE,
    build_runtime_proof_bundle,
)
from tests.apps_lic.canonical_readiness_fixtures import ready_governed_opportunity_facts


def _load_json(path: Path) -> dict[str, Any]:
    assert path.is_file(), f"missing {path.name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _ready_general_intro_raw() -> dict[str, Any]:
    return build_cli_ingress_raw(
        manual_brief="General intro for a technical recruiter.",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        message_modifiers={"uses_referral_context": False},
        campaign_objective="Draft a concise general LinkedIn introduction.",
        lead_profile={
            "verified_name": "Jane Smith",
            "title": "Senior Technical Recruiter",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )


def _copy_run(src: Path, dst: Path) -> Path:
    shutil.copytree(src, dst)
    return dst


def _rebuilt_bundle(run_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    return build_runtime_proof_bundle(
        run_dir,
        dict(manifest),
        terminal_r5=False,
    )


def test_runtime_proof_bundle_rejects_mutated_r4_receipts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    result = run_canonical_apps_lic_spine(
        _ready_general_intro_raw(),
        artifact_root=tmp_path / "base",
    )
    manifest = _load_json(result.artifact_dir / sr.FILENAME_SPINE_MANIFEST)
    original = _load_json(result.artifact_dir / FILENAME_RUNTIME_PROOF_BUNDLE)
    assert original["status"] == "PASS"

    missing_c03 = _copy_run(result.artifact_dir, tmp_path / "missing_c03")
    (missing_c03 / sr.FILENAME_C03_SENDER_PROOF).unlink()
    missing_bundle = _rebuilt_bundle(missing_c03, manifest)
    assert missing_bundle["status"] == "FAIL"
    assert f"missing_file:{sr.FILENAME_C03_SENDER_PROOF}" in missing_bundle["violations"]

    malformed_exit = _copy_run(result.artifact_dir, tmp_path / "malformed_exit")
    exit_receipt = _load_json(malformed_exit / sr.FILENAME_EXIT_DISPOSITION)
    exit_receipt["payload"]["x3_disposition"] = "UNKNOWN"
    _write_json(malformed_exit / sr.FILENAME_EXIT_DISPOSITION, exit_receipt)
    malformed_bundle = _rebuilt_bundle(malformed_exit, manifest)
    assert malformed_bundle["status"] == "FAIL"
    assert "exit_x3_invalid:'UNKNOWN'" in malformed_bundle["violations"]

    write_authorized = _copy_run(result.artifact_dir, tmp_path / "write_authorized")
    l2_receipt = _load_json(write_authorized / sr.FILENAME_L2_EXECUTION)
    l2_receipt["payload"]["state_diff_authorized"] = True
    l2_receipt["payload"]["proposed_state_diff"] = {"message_status": "sent"}
    _write_json(write_authorized / sr.FILENAME_L2_EXECUTION, l2_receipt)
    write_bundle = _rebuilt_bundle(write_authorized, manifest)
    assert write_bundle["status"] == "FAIL"
    assert "l2_state_diff_authorized_true" in write_bundle["violations"]
    assert "l2_proposed_state_diff_non_empty" in write_bundle["violations"]


def test_terminal_r5_proof_bundle_stays_parseable_without_managed_stage_receipts(
    tmp_path: Path,
) -> None:
    result = run_canonical_apps_lic_spine(
        build_cli_ingress_raw(manual_brief="", allow_research=False),
        artifact_root=tmp_path / "r5",
        skip_r3r4_research=True,
    )

    proof = _load_json(result.artifact_dir / FILENAME_RUNTIME_PROOF_BUNDLE)
    manifest = _load_json(result.artifact_dir / sr.FILENAME_SPINE_MANIFEST)

    assert result.terminal_r5 is True
    assert proof["status"] == "PASS"
    assert proof["proof_mode"] == "terminal_r5"
    assert proof["canonical_stage_order"] == ["INGRESS", "U0", "L1", "L0", "EXIT"]
    assert manifest["outcome_authorized"] is False
    for forbidden in (
        sr.FILENAME_C0_FEC,
        sr.FILENAME_C03_SENDER_PROOF,
        sr.FILENAME_PA_RECEIPT,
        sr.FILENAME_L3_WORKFLOW,
        sr.FILENAME_L2_EXECUTION,
        sr.FILENAME_W4_CANDIDATE_BATCH,
        sr.FILENAME_C03_POSTGEN_VALIDATION,
        sr.FILENAME_W5_VALIDATION_EXIT,
    ):
        assert not (result.artifact_dir / forbidden).exists()
