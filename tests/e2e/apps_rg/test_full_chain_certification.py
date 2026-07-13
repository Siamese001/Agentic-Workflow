"""Deterministic certification cassette for the Apps Research -> Apps RG chain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from apps_rg.runtime.e2e_stage_ledger import (
    ReceiptDerivedE2EStageLedger,
    StageTransitionError,
    verify_e2e_stage_ledger,
)
from apps_rg.runtime.terminal_manifest import (
    seal_terminal_manifest,
    verify_terminal_manifest,
)
from apps_rg.runtime.terminal_state import (
    TerminalStateError,
    TerminalStateMachine,
    persist_product_authorization_receipt,
)

_FIXED_TIME = "2026-07-13T12:00:00+00:00"
_REPO_ROOT = Path(__file__).resolve().parents[3]
_AUTHORITY_STAGES = tuple(
    row["stage_id"]
    for row in json.loads(
        (
            _REPO_ROOT
            / "config/certification/apps_research_rg_e2e_authority_contract.v1.json"
        ).read_text(encoding="utf-8")
    )["stages"]
)
_PRODUCT_STAGE_PATH = _AUTHORITY_STAGES[
    : _AUTHORITY_STAGES.index("MANDATORY_OUTPUTS") + 1
]
_EXTERNAL_CLOSE_STAGES = {
    "STAGE_LEDGER_SEAL",
    "TERMINAL_MANIFEST_SEAL",
    "PIPELINE_COMPLETION_CLOSE",
}


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _identity() -> dict[str, str]:
    return {
        "producer_app_id": "apps_research",
        "consumer_app_id": "apps_rg",
        "parent_run_id": "parent-certification-001",
        "child_run_id": "child-certification-001",
        "request_id": "request-certification-001",
        "trace_root": "trace-certification-001",
        "tenant_id": "tenant-certification-001",
        "target_company": "Anthropic",
        "target_role": "Applied AI Manager",
        "jd_sha256": "sha256:" + "1" * 64,
        "brief_sha256": "sha256:" + "2" * 64,
        "policy_hash": "sha256:" + "3" * 64,
        "blueprint_hash": "sha256:" + "4" * 64,
        "schema_version": "apps_research_rg_run_identity.v1",
    }


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _write_stage_receipt(
    root: Path,
    *,
    sequence: int,
    stage_id: str,
    identity: dict[str, str],
    status: str = "PASS",
) -> Path:
    payload: dict[str, object] = {
        "schema_version": f"certification.{stage_id.lower()}.v1",
        "status": status,
        "identity": identity,
        "created_at_utc": _FIXED_TIME,
    }
    if stage_id == "X3_DISPOSITION":
        payload["x3_code"] = "X3D_ALLOW_FINISH"
    elif status == "PASS" and stage_id == "APPS_RESEARCH_RUNTIME":
        payload.update(
            {
                "run_id": identity["child_run_id"],
                "trace_root": identity["trace_root"],
                "created_after_exit": True,
                "exit_disposition_ref": "sha256:" + "5" * 64,
                "gate_mesh_result_ref": "sha256:" + "6" * 64,
                "sealed_result_ref": "sha256:" + "7" * 64,
            }
        )
    elif status == "PASS" and stage_id == "APPS_RESEARCH_EXIT":
        payload.update(
            {
                "run_id": identity["child_run_id"],
                "request_id": identity["request_id"],
                "trace_root": identity["trace_root"],
                "x3_code": "X3D_ALLOW_FINISH",
                "required_gates_passed": True,
                "hard_fail_count": 0,
                "unknown_count": 0,
                "missing_gate_count": 0,
            }
        )
    elif status == "PASS" and stage_id == "HANDOFF_BUNDLE_COMMIT":
        payload.update(
            {
                "schema_version": "apps_research.apps_rg_handoff.v2",
                "commit_protocol": {
                    "commit_marker_ref": "bundle_commit_manifest.json",
                    "commit_marker_sha256": "sha256:" + "8" * 64,
                },
            }
        )
    elif status == "PASS" and stage_id == "UWG_COMMIT":
        payload.update(
            {
                "commit_status": "COMMITTED",
                "run_id": identity["parent_run_id"],
                "request_id": identity["request_id"],
                "trace_root": identity["trace_root"],
            }
        )
    elif status == "PASS" and stage_id == "PRODUCT_AUTHORIZATION_CLOSE":
        payload.update(
            {"status": "AUTHORIZED", "authorized": True, "immutable": True}
        )
    if stage_id == "PROMOTION_TERMINAL":
        payload["promotion_status"] = "NO_CHANGE"
    return _write_json(
        root / f"{sequence:02d}_{stage_id.lower()}_receipt.json",
        payload,
    )


def test_full_chain_cassette_seals_receipts_and_exact_output_bytes(
    tmp_path: Path,
) -> None:
    identity = _identity()
    ledger = ReceiptDerivedE2EStageLedger.create(
        artifact_dir=tmp_path,
        identity=identity,
        clock=lambda: _FIXED_TIME,
    )
    handoff_bundle = _write_json(
        tmp_path / "apps_research_handoff_bundle.json",
        {
            "schema_version": "apps_research_apps_rg_handoff.v2",
            "identity": identity,
            "brief_sha256": identity["brief_sha256"],
            "commit_state": "COMMITTED",
        },
    )
    authorized_output = tmp_path / "authorized_resume.md"
    authorized_output.write_text(
        "# Authorized resume\n\nExact current-run output bytes.\n",
        encoding="utf-8",
    )
    mandatory_report = _write_json(
        tmp_path / "mandatory_run_report.json",
        {
            "schema_version": "apps_rg.mandatory_run_report.v1",
            "status": "PASS",
            "identity": identity,
        },
    )

    receipts: dict[str, Path] = {}
    terminal_state = TerminalStateMachine()
    product_authorization_receipt: Path | None = None
    for sequence, stage_id in enumerate(_PRODUCT_STAGE_PATH):
        receipt = _write_stage_receipt(
            tmp_path,
            sequence=sequence,
            stage_id=stage_id,
            identity=identity,
        )
        receipts[stage_id] = receipt
        artifact_refs: tuple[Path, ...] = ()
        if stage_id == "HANDOFF_BUNDLE_COMMIT":
            artifact_refs = (handoff_bundle,)
        elif stage_id == "UWG_COMMIT":
            terminal_state.close_product_authorization(
                authorized=True,
                decision_receipt_ref=receipt.name,
                decision_receipt_sha256=_sha256(receipt),
                output_artifact_sha256=_sha256(authorized_output),
                closed_at_utc=_FIXED_TIME,
            )
            product_authorization_receipt = persist_product_authorization_receipt(
                artifact_dir=tmp_path,
                identity=identity,
                state=terminal_state.product_authorization,
                decision_receipt_ref=receipt,
                output_artifact_ref=authorized_output,
            )
            artifact_refs = (authorized_output, product_authorization_receipt)
        elif stage_id == "PRODUCT_AUTHORIZATION_CLOSE":
            assert product_authorization_receipt is not None
            artifact_refs = (product_authorization_receipt,)
        elif stage_id == "MANDATORY_OUTPUTS":
            artifact_refs = (mandatory_report,)
        ledger.record_from_receipt(
            stage_id=stage_id,
            receipt_ref=receipt,
            artifact_refs=artifact_refs,
            next_stage_id=(
                "APPS_RESEARCH_U0"
                if stage_id == "FRESH_PREFLIGHT"
                else "PRODUCT_ELIGIBILITY"
                if stage_id == "X3_DISPOSITION"
                else None
            ),
        )

    terminal_state.record_pipeline_completion(
        complete=True,
        decisive_stage_id="MANDATORY_OUTPUTS",
    )
    ledger.seal(
        terminal_state=terminal_state.snapshot(),
        sealed_at_utc=_FIXED_TIME,
    )
    ledger_report = verify_e2e_stage_ledger(ledger.path)
    assert ledger_report.valid is True, ledger_report.errors
    assert ledger_report.complete is True
    assert ledger_report.entry_count == len(_PRODUCT_STAGE_PATH)

    manifest_path, completion_path = seal_terminal_manifest(
        artifact_dir=tmp_path,
        identity=identity,
        x3_code="X3D_ALLOW_FINISH",
        x3_receipt_ref=receipts["X3_DISPOSITION"],
        terminal_state=terminal_state,
        promotion_status="NO_CHANGE",
        promotion_receipt_ref=receipts["PROMOTION_TERMINAL"],
        mandatory_output_refs={
            "authorized_resume": authorized_output,
            "product_authorization_receipt": product_authorization_receipt,
            "mandatory_run_report": mandatory_report,
        },
        clock=lambda: _FIXED_TIME,
    )
    manifest_report = verify_terminal_manifest(manifest_path)
    completion = json.loads(completion_path.read_text(encoding="utf-8"))

    assert manifest_report.valid is True, manifest_report.errors
    assert completion["product_authorized"] is True
    assert completion["pipeline_complete"] is True
    assert completion["observability_repair_required"] is False
    assert completion["terminal_manifest_sha256"] == _sha256(manifest_path)


def test_receipt_ledger_rejects_replay_cross_run_and_byte_tamper(
    tmp_path: Path,
) -> None:
    identity = _identity()
    ledger = ReceiptDerivedE2EStageLedger.create(
        artifact_dir=tmp_path,
        identity=identity,
        clock=lambda: _FIXED_TIME,
    )
    preflight = _write_stage_receipt(
        tmp_path,
        sequence=0,
        stage_id="FRESH_PREFLIGHT",
        identity=identity,
    )
    ledger.record_from_receipt(
        stage_id="FRESH_PREFLIGHT",
        receipt_ref=preflight,
        next_stage_id="APPS_RESEARCH_U0",
    )

    with pytest.raises(StageTransitionError, match="prior next stage"):
        ledger.record_from_receipt(
            stage_id="FRESH_PREFLIGHT",
            receipt_ref=preflight,
            next_stage_id="APPS_RESEARCH_U0",
        )

    wrong_identity = dict(identity, child_run_id="child-from-another-run")
    cross_run = _write_stage_receipt(
        tmp_path,
        sequence=1,
        stage_id="APPS_RESEARCH_U0",
        identity=wrong_identity,
    )
    with pytest.raises(StageTransitionError, match="identity does not match"):
        ledger.record_from_receipt(
            stage_id="APPS_RESEARCH_U0",
            receipt_ref=cross_run,
        )

    current_run = _write_stage_receipt(
        tmp_path,
        sequence=1,
        stage_id="APPS_RESEARCH_U0",
        identity=identity,
    )
    ledger.record_from_receipt(
        stage_id="APPS_RESEARCH_U0",
        receipt_ref=current_run,
    )
    current_run.write_bytes(current_run.read_bytes() + b" ")

    report = verify_e2e_stage_ledger(ledger.path)
    assert report.valid is False
    assert "authoritative_receipt_digest_mismatch:APPS_RESEARCH_U0" in report.errors


def _next_product_stage(stage_id: str) -> str | None:
    if stage_id == "FRESH_PREFLIGHT":
        return "APPS_RESEARCH_U0"
    if stage_id == "X3_DISPOSITION":
        return "PRODUCT_ELIGIBILITY"
    return None


def _build_passing_product_ledger(
    root: Path,
) -> tuple[ReceiptDerivedE2EStageLedger, dict[str, str], dict[str, Path]]:
    identity = _identity()
    ledger = ReceiptDerivedE2EStageLedger.create(
        artifact_dir=root,
        identity=identity,
        clock=lambda: _FIXED_TIME,
    )
    receipts: dict[str, Path] = {}
    for sequence, stage_id in enumerate(_PRODUCT_STAGE_PATH):
        receipt = _write_stage_receipt(
            root,
            sequence=sequence,
            stage_id=stage_id,
            identity=identity,
        )
        receipts[stage_id] = receipt
        ledger.record_from_receipt(
            stage_id=stage_id,
            receipt_ref=receipt,
            next_stage_id=_next_product_stage(stage_id),
        )
    return ledger, identity, receipts


def _exercise_embedded_stage_failure(root: Path, failure_stage: str) -> None:
    identity = _identity()
    ledger = ReceiptDerivedE2EStageLedger.create(
        artifact_dir=root,
        identity=identity,
        clock=lambda: _FIXED_TIME,
    )
    failed_entry: dict[str, object] | None = None
    for sequence, stage_id in enumerate(_PRODUCT_STAGE_PATH):
        receipt = _write_stage_receipt(
            root,
            sequence=sequence,
            stage_id=stage_id,
            identity=identity,
            status="FAIL" if stage_id == failure_stage else "PASS",
        )
        failed_entry = ledger.record_from_receipt(
            stage_id=stage_id,
            receipt_ref=receipt,
            next_stage_id=_next_product_stage(stage_id),
        )
        if stage_id == failure_stage:
            break

    assert failed_entry is not None
    assert failed_entry["stage_id"] == failure_stage
    assert failed_entry["status"] in {"FAIL", "BLOCKED"}
    assert failed_entry["next_stage_id"] is None
    ledger_report = verify_e2e_stage_ledger(ledger.path)
    assert ledger_report.valid is True, ledger_report.errors
    assert ledger_report.complete is False
    assert ledger_report.terminal_stage == failure_stage

    authorized = _PRODUCT_STAGE_PATH.index(failure_stage) > _PRODUCT_STAGE_PATH.index(
        "UWG_COMMIT"
    )
    machine = TerminalStateMachine()
    machine.close_product_authorization(
        authorized=authorized,
        decision_receipt_ref=f"{failure_stage.lower()}_decision.json",
        decision_receipt_sha256="sha256:" + "a" * 64,
        output_artifact_sha256=("sha256:" + "b" * 64 if authorized else None),
        closed_at_utc=_FIXED_TIME,
    )
    machine.record_pipeline_completion(
        complete=False,
        failed=True,
        decisive_stage_id=failure_stage,
    )
    assert machine.snapshot() == {
        "product_authorized": authorized,
        "pipeline_complete": False,
        "observability_repair_required": authorized,
    }


def _exercise_external_close_failure(root: Path, failure_stage: str) -> None:
    ledger, identity, receipts = _build_passing_product_ledger(root)
    if failure_stage == "STAGE_LEDGER_SEAL":
        receipts["MANDATORY_OUTPUTS"].write_bytes(
            receipts["MANDATORY_OUTPUTS"].read_bytes() + b" "
        )
        with pytest.raises(StageTransitionError, match="invalid receipt-derived ledger"):
            ledger.seal(
                terminal_state={
                    "product_authorized": True,
                    "pipeline_complete": False,
                    "observability_repair_required": True,
                },
                sealed_at_utc=_FIXED_TIME,
            )
        assert verify_e2e_stage_ledger(ledger.path).sealed is False
        return

    output = root / "authorized_resume.md"
    output.write_text("Authorized product bytes\n", encoding="utf-8")
    decision = receipts["UWG_COMMIT"]
    machine = TerminalStateMachine()
    machine.close_product_authorization(
        authorized=True,
        decision_receipt_ref=decision.name,
        decision_receipt_sha256=_sha256(decision),
        output_artifact_sha256=_sha256(output),
        closed_at_utc=_FIXED_TIME,
    )
    machine.record_pipeline_completion(
        complete=False,
        failed=True,
        decisive_stage_id=failure_stage,
    )
    ledger.seal(terminal_state=machine.snapshot(), sealed_at_utc=_FIXED_TIME)

    if failure_stage == "TERMINAL_MANIFEST_SEAL":
        with pytest.raises(TerminalStateError, match="terminal artifact is missing"):
            seal_terminal_manifest(
                artifact_dir=root,
                identity=identity,
                x3_code="X3D_ALLOW_FINISH",
                x3_receipt_ref=receipts["X3_DISPOSITION"],
                terminal_state=machine,
                promotion_status="NO_CHANGE",
                promotion_receipt_ref=root / "missing_promotion_receipt.json",
                mandatory_output_refs={
                    "mandatory_run_output": receipts["MANDATORY_OUTPUTS"]
                },
                clock=lambda: _FIXED_TIME,
            )
        return

    manifest_path, completion_path = seal_terminal_manifest(
        artifact_dir=root,
        identity=identity,
        x3_code="X3D_ALLOW_FINISH",
        x3_receipt_ref=receipts["X3_DISPOSITION"],
        terminal_state=machine,
        promotion_status="NO_CHANGE",
        promotion_receipt_ref=receipts["PROMOTION_TERMINAL"],
        mandatory_output_refs={"mandatory_run_output": receipts["MANDATORY_OUTPUTS"]},
        clock=lambda: _FIXED_TIME,
    )
    completion_path.unlink()
    manifest_report = verify_terminal_manifest(manifest_path)
    assert manifest_report.valid is False
    assert "pipeline_completion_receipt_unreadable:FileNotFoundError" in (
        manifest_report.errors
    )


def _exercise_terminal_non_product_path(root: Path) -> None:
    identity = _identity()
    ledger = ReceiptDerivedE2EStageLedger.create(
        artifact_dir=root,
        identity=identity,
        clock=lambda: _FIXED_TIME,
    )
    for sequence, stage_id in enumerate(
        _PRODUCT_STAGE_PATH[: _PRODUCT_STAGE_PATH.index("X3_DISPOSITION") + 1]
    ):
        receipt = _write_stage_receipt(
            root,
            sequence=sequence,
            stage_id=stage_id,
            identity=identity,
        )
        next_stage = _next_product_stage(stage_id)
        if stage_id == "X3_DISPOSITION":
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["x3_code"] = "X3E_SAFE_ABSTAIN"
            _write_json(receipt, payload)
            next_stage = "TERMINAL_NON_PRODUCT"
        ledger.record_from_receipt(
            stage_id=stage_id,
            receipt_ref=receipt,
            next_stage_id=next_stage,
        )
    terminal_receipt = _write_stage_receipt(
        root,
        sequence=_PRODUCT_STAGE_PATH.index("X3_DISPOSITION") + 1,
        stage_id="TERMINAL_NON_PRODUCT",
        identity=identity,
        status="SKIPPED",
    )
    ledger.record_from_receipt(
        stage_id="TERMINAL_NON_PRODUCT",
        receipt_ref=terminal_receipt,
    )
    machine = TerminalStateMachine()
    machine.close_product_authorization(
        authorized=False,
        non_product=True,
        decision_receipt_ref=terminal_receipt.name,
        decision_receipt_sha256=_sha256(terminal_receipt),
        output_artifact_sha256=None,
        closed_at_utc=_FIXED_TIME,
    )
    machine.record_pipeline_completion(
        complete=False,
        decisive_stage_id="TERMINAL_NON_PRODUCT",
    )
    ledger.seal(terminal_state=machine.snapshot(), sealed_at_utc=_FIXED_TIME)
    ledger_report = verify_e2e_stage_ledger(ledger.path)
    assert ledger_report.valid is True, ledger_report.errors
    assert ledger_report.complete is True
    assert ledger_report.terminal_stage == "TERMINAL_NON_PRODUCT"
    assert machine.snapshot() == {
        "product_authorized": False,
        "pipeline_complete": False,
        "observability_repair_required": False,
    }


@pytest.mark.parametrize(
    "failure_stage",
    json.loads(
        (
            Path(__file__).resolve().parents[3]
            / "config"
            / "certification"
            / "apps_research_rg_e2e_dependencies.v1.json"
        ).read_text(encoding="utf-8")
    )["failure_injection_stages"],
)
def test_failure_matrix_preserves_the_uwg_authorization_boundary(
    failure_stage: str,
    tmp_path: Path,
) -> None:
    assert failure_stage in _AUTHORITY_STAGES
    if failure_stage in _PRODUCT_STAGE_PATH:
        _exercise_embedded_stage_failure(tmp_path, failure_stage)
    elif failure_stage in _EXTERNAL_CLOSE_STAGES:
        _exercise_external_close_failure(tmp_path, failure_stage)
    else:
        assert failure_stage == "TERMINAL_NON_PRODUCT"
        _exercise_terminal_non_product_path(tmp_path)
