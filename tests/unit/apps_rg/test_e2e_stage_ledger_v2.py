"""Receipt-derived product-v2 ledger and external seal tests."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _identity() -> dict[str, str]:
    return {
        "producer_app_id": "apps_research",
        "consumer_app_id": "apps_rg",
        "parent_run_id": "parent-001",
        "child_run_id": "child-001",
        "request_id": "request-001",
        "trace_root": "trace-001",
        "tenant_id": "tenant-001",
        "target_company": "Anthropic",
        "target_role": "Applied AI Manager",
        "jd_sha256": "sha256:" + "1" * 64,
        "brief_sha256": "sha256:" + "2" * 64,
        "policy_hash": "sha256:" + "3" * 64,
        "blueprint_hash": "sha256:" + "4" * 64,
        "schema_version": "apps_research_rg_run_identity.v1",
    }


def _write_receipt(
    root: Path,
    *,
    sequence: int,
    stage_id: str,
    identity: dict[str, str],
    status: str = "PASS",
) -> Path:
    stage_fields: dict[str, object] = {}
    if stage_id == "X3_DISPOSITION":
        stage_fields["x3_code"] = "X3D_ALLOW_FINISH"
    elif stage_id == "UWG_COMMIT":
        stage_fields.update(
            {
                "commit_status": "COMMITTED",
                "run_id": identity["parent_run_id"],
                "request_id": identity["request_id"],
                "trace_root": identity["trace_root"],
            }
        )
    elif stage_id == "PRODUCT_AUTHORIZATION_CLOSE":
        stage_fields.update(
            {"status": "AUTHORIZED", "authorized": True, "immutable": True}
        )
    path = root / f"{sequence:02d}_{stage_id.lower()}_receipt.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": f"test.{stage_id.lower()}.v1",
                "status": status,
                "identity": identity,
                **stage_fields,
                "created_at_utc": "2026-07-13T12:00:00+00:00",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _build_product_ledger(root: Path, *, include_mandatory: bool = True):
    from apps_rg.runtime.e2e_stage_ledger import ReceiptDerivedE2EStageLedger

    identity = _identity()
    ledger = ReceiptDerivedE2EStageLedger.create(
        artifact_dir=root,
        identity=identity,
    )
    stage_ids = (
        "FRESH_PREFLIGHT",
        "APPS_RG_U0",
        "APPS_RG_L1",
        "APPS_RG_L0",
        "APPS_RG_C0",
        "APPS_RG_PA",
        "APPS_RG_L2",
        "X1_REVIEW",
        "X2_AGGREGATION",
        "X3_DISPOSITION",
        "PRODUCT_ELIGIBILITY",
        "UWG_COMMIT",
        "PRODUCT_AUTHORIZATION_CLOSE",
        "APPS_EVAL",
        "L6_SHADOW",
        "INDEPENDENT_PARITY",
        "PROMOTION_TERMINAL",
        "MANDATORY_OUTPUTS",
    )
    if not include_mandatory:
        stage_ids = stage_ids[:-1]
    receipts: dict[str, Path] = {}
    for sequence, stage_id in enumerate(stage_ids):
        receipt = _write_receipt(
            root,
            sequence=sequence,
            stage_id=stage_id,
            identity=identity,
        )
        receipts[stage_id] = receipt
        next_stage_id = (
            "APPS_RG_U0"
            if stage_id == "FRESH_PREFLIGHT"
            else "PRODUCT_ELIGIBILITY"
            if stage_id == "X3_DISPOSITION"
            else None
        )
        ledger.record_from_receipt(
            stage_id=stage_id,
            receipt_ref=receipt,
            next_stage_id=next_stage_id,
        )
    return ledger, identity, receipts


def test_whole_run_product_activation_replaces_preidentity_ledger_with_v2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.runtime.e2e_preflight import (
        E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME,
        E2E_PREFLIGHT_SCHEMA_VERSION,
        _payload_digest,
        _signature,
        validate_preflight_continuation,
    )
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, verify_e2e_stage_ledger
    from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
        _activate_product_stage_ledger,
    )

    run_root = tmp_path / "consumer-run"
    producer_root = tmp_path / "producer-run"
    run_root.mkdir()
    producer_root.mkdir()
    identity = _identity()
    secret = "unit-test-route-signing-secret"
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_SECRET", secret)
    issued = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)
    continuation_body = {
        "schema_version": E2E_PREFLIGHT_SCHEMA_VERSION,
        "status": "PASS",
        "e2e_run_id": run_root.name,
        "artifact_dir": str(run_root.resolve()),
        "artifact_dir_sha256": _payload_digest(str(run_root.resolve())),
        "identity": {"e2e_run_id": run_root.name},
        "identity_sha256": _payload_digest({"e2e_run_id": run_root.name}),
        "product_entry_eligible": False,
        "route_signing_key_id": "unit-key",
        "issued_at_utc": issued.isoformat(),
        "expires_at_utc": (issued + timedelta(minutes=5)).isoformat(),
        "continuation_nonce": "one-use-nonce",
    }
    continuation = {
        **continuation_body,
        "continuation_payload_digest": _payload_digest(continuation_body),
        "continuation_signature": _signature(secret, continuation_body),
    }
    continuation_path = run_root / E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME
    _write_json(continuation_path, continuation)
    validation = validate_preflight_continuation(
        receipt_path=continuation_path,
        secret=secret,
        expected_e2e_run_id=run_root.name,
        expected_key_id="unit-key",
        consumer_id="apps_rg.whole_run.primary",
        consume=True,
        require_product_identity=False,
        now_utc=issued + timedelta(seconds=1),
    )
    assert validation.valid is True

    legacy = E2EStageLedger.create(
        artifact_dir=run_root,
        e2e_run_id=run_root.name,
    )
    _write_json(
        producer_root / "apps_research_u0_receipt.json",
        {
            "schema_version": "apps_research.u0_receipt.v1",
            "status": "PASS",
            "parent_run_id": identity["parent_run_id"],
            "child_run_id": identity["child_run_id"],
            "request_id": identity["request_id"],
            "trace_root": identity["trace_root"],
            "tenant_id": identity["tenant_id"],
        },
    )
    _write_json(
        producer_root / "runtime_exhaust_bundle.json",
        {
            "schema_version": "apps_research.runtime_exhaust.v1",
            "run_id": identity["child_run_id"],
            "trace_root": identity["trace_root"],
            "created_after_exit": True,
            "exit_disposition_ref": "sha256:" + "5" * 64,
            "gate_mesh_result_ref": "sha256:" + "6" * 64,
            "sealed_result_ref": "sha256:" + "7" * 64,
        },
    )
    _write_json(
        producer_root / "exit_disposition_receipt.json",
        {
            "schema_version": "apps_research.exit_disposition.v1",
            "run_id": identity["child_run_id"],
            "request_id": identity["request_id"],
            "trace_root": identity["trace_root"],
            "x3_code": "X3D_ALLOW_FINISH",
            "required_gates_passed": True,
            "hard_fail_count": 0,
            "unknown_count": 0,
            "missing_gate_count": 0,
        },
    )
    _write_json(producer_root / "bundle_commit_manifest.json", {"committed": True})
    _write_json(
        producer_root / "apps_research_apps_rg_handoff_v2.json",
        {
            "schema_version": "apps_research.apps_rg_handoff.v2",
            "identity": identity,
            "commit_protocol": {
                "commit_marker_ref": str(
                    producer_root / "bundle_commit_manifest.json"
                ),
                "commit_marker_sha256": "sha256:" + "8" * 64,
            },
        },
    )
    _write_json(
        producer_root / "apps_research_handoff_validation_receipt.json",
        {
            "schema_version": "apps_rg.apps_research_handoff_validation_receipt.v2",
            "status": "PASS",
            "identity": identity,
        },
    )
    brief = producer_root / "briefing.md"
    brief.write_text("Committed research briefing\n", encoding="utf-8")
    for name in ("l1_plan_contract.json", "route_contract.json"):
        _write_json(
            run_root / name,
            {
                "schema_version": f"test.{name}.v1",
                "status": "PASS",
                "identity": identity,
            },
        )

    product = _activate_product_stage_ledger(
        artifact_dir=run_root,
        legacy_ledger=legacy,
        identity=identity,
        preflight_validation=validation,
        continuation_path=continuation_path,
        manual_brief=str(brief),
        research_ran=True,
    )
    payload = json.loads(product.path.read_text(encoding="utf-8"))
    report = verify_e2e_stage_ledger(product.path)

    assert payload["schema_version"] == "apps_rg.e2e_stage_ledger.v2"
    assert [entry["stage_id"] for entry in payload["entries"]] == [
        "FRESH_PREFLIGHT",
        "APPS_RESEARCH_U0",
        "APPS_RESEARCH_RUNTIME",
        "APPS_RESEARCH_EXIT",
        "HANDOFF_BUNDLE_COMMIT",
        "APPS_RG_U0",
        "APPS_RG_L1",
        "APPS_RG_L0",
    ]
    assert all(
        entry["status_derivation"] == "AUTHORITATIVE_RECEIPT_BYTES"
        for entry in payload["entries"]
    )
    assert (run_root / "e2e_stage_ledger_preidentity_non_product.json").is_file()
    assert report.valid is True
    assert report.complete is False


def test_product_terminal_helper_closes_only_after_product_mandatory_profile(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.e2e_stage_ledger import verify_e2e_stage_ledger
    from apps_rg.runtime.mandatory_outputs import (
        PRODUCT_MANDATORY_OUTPUT_PROFILE,
        seal_mandatory_output_bundle,
    )
    from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
        _seal_product_terminal_authority,
    )
    from apps_rg.runtime.terminal_manifest import verify_terminal_manifest

    ledger, identity, _ = _build_product_ledger(
        tmp_path,
        include_mandatory=False,
    )
    mandatory_document = {
        "schema_version": "apps_rg.mandatory_run_output.v1",
        "mandatory_output_hard_stop": {
            "gate_id": "APPS_RG_MANDATORY_OUTPUTS_INCOMPLETE",
            "required": True,
            "pass": True,
            "errors": [],
        },
    }
    sealed_files = {
        "APPS_RG_MANDATORY_RUN_OUTPUT.json": (
            json.dumps(mandatory_document) + "\n"
        ).encode(),
        "02_section_lane_summary_table.md": b"# mandatory\n",
        "01_BCG_executive_output.md": b"# executive\n",
        "02_output_bisect.md": b"# bisect\n",
        "03_L7_audit_ability_output.md": b"# audit\n",
        "FINAL_RESUME_OUTPUT.txt": b"authorized output\n",
        "FINAL_RESUME_OUTPUT.json": b'{"authorized":true}\n',
        "outputs/resume.docx": b"authorized-docx",
        "modular_r4/final_resume_assembly/final_resume.json": (
            b'{"authorized":true}\n'
        ),
        "apps_rg_output_manifest.json": b'{"status":"PASS"}\n',
    }
    seal_mandatory_output_bundle(
        tmp_path,
        sealed_files,
        profile_id=PRODUCT_MANDATORY_OUTPUT_PROFILE,
        required_artifacts=tuple(sealed_files),
    )
    _write_json(
        tmp_path / "x3_disposition_receipt.json",
        {
            "schema_version": "x3_disposition_receipt.v1",
            "disposition": "X3D_ALLOW_FINISH",
        },
    )
    decision = tmp_path / "uwg" / "uwg_commit_receipt.json"
    _write_json(decision, {"commit_status": "COMMITTED"})
    output = tmp_path / "outputs" / "resume.docx"
    product_authorization = tmp_path / "apps_rg_product_authorization_receipt.json"
    _write_json(
        product_authorization,
        {
            "schema_version": "apps_rg.product_authorization_receipt.v1",
            "identity": identity,
            "authorized": True,
            "status": "AUTHORIZED",
            "immutable": True,
            "closed_at_utc": "2026-07-13T12:00:00+00:00",
            "decision_receipt": {
                "artifact_ref": "uwg/uwg_commit_receipt.json",
                "sha256": "sha256:"
                + hashlib.sha256(decision.read_bytes()).hexdigest(),
            },
            "output_artifact": {
                "artifact_ref": "outputs/resume.docx",
                "sha256": "sha256:"
                + hashlib.sha256(output.read_bytes()).hexdigest(),
            },
        },
    )
    _write_json(
        tmp_path
        / "e2e_authority_receipts"
        / "promotion_terminal_authority_receipt.json",
        {
            "schema_version": "apps_rg.e2e_stage_authority.promotion_terminal.v1",
            "status": "PASS",
            "identity": identity,
            "promotion_terminal_status": "PROMOTED",
        },
    )

    refs = _seal_product_terminal_authority(
        artifact_dir=tmp_path,
        product_ledger=ledger,
        identity=identity,
        product_authorization_ref=product_authorization.name,
    )
    ledger_report = verify_e2e_stage_ledger(ledger.path)
    manifest_report = verify_terminal_manifest(Path(refs["terminal_manifest_ref"]))

    assert ledger_report.valid is True
    assert ledger_report.complete is True
    assert ledger_report.sealed is True
    assert manifest_report.valid is True
    assert manifest_report.pipeline_completion_receipt["pipeline_complete"] is True


def test_product_mandatory_authority_rejects_closeout_profile_shrinkage(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.mandatory_outputs import (
        CLOSEOUT_MANDATORY_OUTPUT_PROFILE,
        seal_mandatory_output_bundle,
    )
    from apps_rg.runtime.product_stage_authority import (
        emit_mandatory_outputs_authority_receipt,
    )

    mandatory = {
        "schema_version": "apps_rg.mandatory_run_output.v1",
        "mandatory_output_hard_stop": {"required": True, "pass": True},
    }
    files = {
        "APPS_RG_MANDATORY_RUN_OUTPUT.json": (
            json.dumps(mandatory) + "\n"
        ).encode(),
    }
    seal_mandatory_output_bundle(
        tmp_path,
        files,
        profile_id=CLOSEOUT_MANDATORY_OUTPUT_PROFILE,
        required_artifacts=tuple(files),
    )

    receipt_path = emit_mandatory_outputs_authority_receipt(
        artifact_dir=tmp_path,
        identity=_identity(),
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    assert receipt["status"] == "BLOCKED"
    assert receipt["checks"]["product_profile_exact"] is False
    assert receipt["checks"]["product_required_artifacts_not_shrunk"] is False


def test_product_v2_ledger_entries_are_receipt_derived_and_external_sealed(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.e2e_stage_ledger import verify_e2e_stage_ledger

    ledger, _, _ = _build_product_ledger(tmp_path)
    seal_path = ledger.seal(
        terminal_state={
            "product_authorized": True,
            "pipeline_complete": True,
            "observability_repair_required": False,
        },
        sealed_at_utc="2026-07-13T12:01:00+00:00",
    )
    payload = json.loads(ledger.path.read_text(encoding="utf-8"))
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    report = verify_e2e_stage_ledger(ledger.path)

    assert payload["schema_version"] == "apps_rg.e2e_stage_ledger.v2"
    assert all(
        entry["status_derivation"] == "AUTHORITATIVE_RECEIPT_BYTES"
        for entry in payload["entries"]
    )
    assert not {
        "STAGE_LEDGER_SEAL",
        "TERMINAL_MANIFEST_SEAL",
        "PIPELINE_COMPLETION_CLOSE",
    }.intersection(entry["stage_id"] for entry in payload["entries"])
    assert "seal" not in payload
    assert seal["schema_version"] == "apps_rg.e2e_stage_ledger_seal.v1"
    assert seal["ledger_sha256"] == (
        "sha256:" + hashlib.sha256(ledger.path.read_bytes()).hexdigest()
    )
    assert report.valid is True
    assert report.complete is True
    assert report.sealed is True


def test_product_v2_ledger_detects_authoritative_receipt_byte_tamper(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.e2e_stage_ledger import verify_e2e_stage_ledger

    ledger, _, receipts = _build_product_ledger(tmp_path)
    receipts["X2_AGGREGATION"].write_text(
        receipts["X2_AGGREGATION"].read_text(encoding="utf-8") + " ",
        encoding="utf-8",
    )

    report = verify_e2e_stage_ledger(ledger.path)
    assert report.valid is False
    assert "authoritative_receipt_digest_mismatch:X2_AGGREGATION" in report.errors


def test_authority_contract_uses_external_ledger_and_pipeline_close_receipts() -> None:
    contract_path = (
        Path(__file__).resolve().parents[3]
        / "config"
        / "certification"
        / "apps_research_rg_e2e_authority_contract.v1.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    stages = {row["stage_id"]: row for row in contract["stages"]}

    assert stages["STAGE_LEDGER_SEAL"]["authoritative_receipt"] == (
        "e2e_stage_ledger_seal_receipt.json"
    )
    assert stages["PIPELINE_COMPLETION_CLOSE"]["authoritative_receipt"] == (
        "apps_rg_pipeline_completion_receipt.json"
    )
    assert (
        stages["STAGE_LEDGER_SEAL"]["authoritative_receipt"]
        != "e2e_stage_ledger.json"
    )
    assert (
        stages["PIPELINE_COMPLETION_CLOSE"]["authoritative_receipt"]
        != "apps_rg_e2e_terminal_manifest.json"
    )


def test_post_boundary_authority_reopens_eval_seal_and_rejects_tamper(
    tmp_path: Path,
) -> None:
    from apps_eval.runner.core import _seal_apps_rg_eval_package
    from apps_rg.runtime.product_stage_authority import (
        emit_post_boundary_authority_receipts,
    )

    identity = _identity()
    eval_dir = tmp_path / "apps_eval" / "run"
    eval_dir.mkdir(parents=True)
    eval_record = eval_dir / "eval_record.json"
    scorecard_rows = eval_dir / "scorecard_rows.jsonl"
    component_scorecards = eval_dir / "component_scorecards.json"
    coverage_matrix = eval_dir / "coverage_matrix.csv"
    regression_summary = eval_dir / "regression.json"
    _write_json(
        eval_record,
        {
            "schema_version": "apps_eval.completed_eval.v3",
            "record_id": "eval-001",
            "eval_record_id": "eval-001",
            "app_id": "apps_rg",
            "parent_run_id": identity["parent_run_id"],
        },
    )
    scorecard_rows.write_text('{"row_id":"row-1"}\n', encoding="utf-8")
    _write_json(component_scorecards, {"status": "PASS"})
    coverage_matrix.write_text("row_id,status\nrow-1,PASS\n", encoding="utf-8")
    _write_json(regression_summary, {"verdict": "pass"})
    _seal_apps_rg_eval_package(
        run_dir=eval_dir,
        record_id="eval-001",
        planned_eval_artifacts={
            "__emission_complete__": True,
            "eval_record": eval_record.as_posix(),
            "scorecard_rows": scorecard_rows.as_posix(),
            "component_scorecards": component_scorecards.as_posix(),
            "coverage_matrix": coverage_matrix.as_posix(),
            "regression_summary": regression_summary.as_posix(),
        },
    )

    l6_bridge = tmp_path / "l6_shadow_bridge.json"
    parity = tmp_path / "l6_apps_eval_binding_closure.json"
    promotion = tmp_path / "fact_vector_writeback_completion_receipt.json"
    _write_json(l6_bridge, {"status": "PASS"})
    _write_json(parity, {"binding_closure_status": "PASS"})
    _write_json(promotion, {"status": "PASS"})
    completion = {
        "apps_eval": {
            "record_id": "eval-001",
            "eval_record_ref": eval_record.relative_to(tmp_path).as_posix(),
            "coverage_summary": {
                "coverage_complete": True,
                "release_blocked": False,
            },
        },
        "l6_shadow": {
            "l6_shadow_bridge_ref": l6_bridge.name,
            "l6_apps_eval_binding_closure_ref": parity.name,
            "grain_parity_status": "PASS",
            "apps_eval_rows_bound": True,
        },
        "fact_vector_writeback": {"status": "PASS"},
    }
    _write_json(tmp_path / "apps_rg_post_x3_completion_receipt.json", completion)

    receipts = emit_post_boundary_authority_receipts(
        artifact_dir=tmp_path,
        identity=identity,
        post_x3_completion=completion,
    )
    eval_authority = json.loads(
        receipts["APPS_EVAL"].read_text(encoding="utf-8")
    )
    bound_refs = {
        row["artifact_ref"] for row in eval_authority["source_bindings"]
    }
    seal = json.loads(
        (eval_dir / "apps_rg_eval_package_seal.json").read_text(encoding="utf-8")
    )
    sealed_refs = {
        (eval_dir / row["artifact_ref"])
        .relative_to(tmp_path)
        .as_posix()
        for row in seal["artifacts"]
    }

    assert eval_authority["status"] == "PASS"
    assert eval_authority["checks"]["eval_package_seal_valid"] is True
    assert sealed_refs <= bound_refs
    assert "apps_eval/run/apps_rg_eval_package_seal.json" in bound_refs

    coverage_matrix.write_text(
        "row_id,status\nrow-1,FAIL\n",
        encoding="utf-8",
    )
    receipts = emit_post_boundary_authority_receipts(
        artifact_dir=tmp_path,
        identity=identity,
        post_x3_completion=completion,
    )
    tampered_authority = json.loads(
        receipts["APPS_EVAL"].read_text(encoding="utf-8")
    )

    assert tampered_authority["status"] == "BLOCKED"
    assert tampered_authority["checks"]["eval_package_seal_valid"] is False
    assert "eval_package_seal_valid" in tampered_authority["failed_checks"]


def test_post_boundary_failure_requires_repair_without_revoking_authorization(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.terminal_state import TerminalStateError, TerminalStateMachine

    decision = tmp_path / "uwg_commit_receipt.json"
    decision.write_text("uwg-committed\n", encoding="utf-8")
    output = tmp_path / "generated_resume.md"
    output.write_text("authorized product bytes\n", encoding="utf-8")
    machine = TerminalStateMachine()
    machine.close_product_authorization(
        authorized=True,
        decision_receipt_ref=decision.name,
        decision_receipt_sha256=(
            "sha256:" + hashlib.sha256(decision.read_bytes()).hexdigest()
        ),
        output_artifact_sha256=(
            "sha256:" + hashlib.sha256(output.read_bytes()).hexdigest()
        ),
    )
    pipeline = machine.record_pipeline_completion(
        complete=False,
        failed=True,
        decisive_stage_id="APPS_EVAL",
    )

    assert machine.product_authorized is True
    assert pipeline.complete is False
    assert pipeline.observability_repair_required is True
    with pytest.raises(TerminalStateError, match="immutable"):
        machine.close_product_authorization(
            authorized=False,
            decision_receipt_ref=decision.name,
            decision_receipt_sha256=(
                "sha256:" + hashlib.sha256(decision.read_bytes()).hexdigest()
            ),
            output_artifact_sha256=None,
        )
    assert machine.product_authorized is True


def test_terminal_manifest_and_completion_receipt_bind_exact_bytes(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.terminal_manifest import (
        seal_terminal_manifest,
        verify_terminal_manifest,
    )
    from apps_rg.runtime.terminal_state import TerminalStateMachine

    ledger, identity, receipts = _build_product_ledger(tmp_path)
    output = tmp_path / "generated_resume.md"
    output.write_text("authorized product bytes\n", encoding="utf-8")
    decision = receipts["PRODUCT_AUTHORIZATION_CLOSE"]
    machine = TerminalStateMachine()
    machine.close_product_authorization(
        authorized=True,
        decision_receipt_ref=decision.name,
        decision_receipt_sha256=(
            "sha256:" + hashlib.sha256(decision.read_bytes()).hexdigest()
        ),
        output_artifact_sha256=(
            "sha256:" + hashlib.sha256(output.read_bytes()).hexdigest()
        ),
        closed_at_utc="2026-07-13T12:00:30+00:00",
    )
    machine.record_pipeline_completion(
        complete=False,
        failed=True,
        decisive_stage_id="APPS_EVAL",
    )
    ledger.seal(
        terminal_state=machine.snapshot(),
        sealed_at_utc="2026-07-13T12:01:00+00:00",
    )
    manifest_path, completion_path = seal_terminal_manifest(
        artifact_dir=tmp_path,
        identity=identity,
        x3_code="X3D_ALLOW_FINISH",
        x3_receipt_ref=receipts["X3_DISPOSITION"],
        terminal_state=machine,
        promotion_status="REJECTED",
        promotion_receipt_ref=receipts["PROMOTION_TERMINAL"],
        mandatory_output_refs={
            "mandatory_run_output": receipts["MANDATORY_OUTPUTS"]
        },
        clock=lambda: "2026-07-13T12:02:00+00:00",
    )
    report = verify_terminal_manifest(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    completion = json.loads(completion_path.read_text(encoding="utf-8"))

    assert report.valid is True, report.errors
    assert manifest["product_authorization"]["authorized"] is True
    assert manifest["pipeline_completion"]["complete"] is False
    assert manifest["pipeline_completion"]["observability_repair_required"] is True
    assert completion["terminal_manifest_sha256"] == (
        "sha256:" + hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    )

    mutated = dict(manifest)
    mutated["pipeline_completion"]["decisive_stage_id"] = "L6_SHADOW"
    manifest_path.write_text(json.dumps(mutated, indent=2), encoding="utf-8")
    tampered = verify_terminal_manifest(manifest_path)
    assert tampered.valid is False
    assert "manifest_seal_digest_mismatch" in tampered.errors
    assert "pipeline_completion_manifest_digest_mismatch" in tampered.errors
