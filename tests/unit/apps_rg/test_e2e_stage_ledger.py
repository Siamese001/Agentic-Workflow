"""apps-test-model: APP CONTRACT.

Deterministic contract tests for the apps_rg E2E stage ledger.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


def _clock(values: list[str]):
    iterator = iter(values)
    return lambda: next(iterator)


def test_stage_ledger_hash_chains_the_canonical_success_path(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, verify_e2e_stage_ledger

    ledger = E2EStageLedger.create(
        artifact_dir=tmp_path,
        e2e_run_id="e2e-run-001",
        clock=_clock([f"2026-07-10T00:00:{index:02d}+00:00" for index in range(40)]),
    )
    for stage_id in (
        "PREFLIGHT",
        "RESEARCH",
        "U0",
        "L1",
        "L0",
        "C0",
        "L2",
        "X1",
        "X2",
        "X3",
        "CANDIDATE",
        "APPS_EVAL",
        "L6_SHADOW",
        "STATE_PROMOTION",
        "CLOSEOUT",
    ):
        ledger.record(
            stage_id=stage_id,
            status="PASS",
            input_refs={"source": f"{stage_id.lower()}-input.json"},
            output_refs={"receipt": f"{stage_id.lower()}-receipt.json"},
            child_run_id="research-child-001" if stage_id == "RESEARCH" else "",
        )

    report = verify_e2e_stage_ledger(ledger.path)
    payload = json.loads(ledger.path.read_text(encoding="utf-8"))

    assert report.valid is True
    assert report.complete is True
    assert report.errors == ()
    assert payload["e2e_run_id"] == "e2e-run-001"
    assert payload["entries"][0]["previous_receipt_digest"] == ""
    assert all(entry["receipt_digest"].startswith("sha256:") for entry in payload["entries"])
    assert payload["entries"][-1]["stage_id"] == "CLOSEOUT"


def test_stage_ledger_rejects_out_of_order_transition(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, StageTransitionError

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="e2e-run-order")

    with pytest.raises(StageTransitionError, match="U0.*RESEARCH"):
        ledger.record(stage_id="U0", status="PASS")


def test_stage_ledger_allows_closeout_after_terminal_failure(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, StageTransitionError

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="e2e-run-failure")
    ledger.record(stage_id="PREFLIGHT", status="PASS")
    ledger.record(
        stage_id="RESEARCH",
        status="FAIL",
        reason_code="APPS_RESEARCH_ARTIFACT_MISSING",
    )

    with pytest.raises(StageTransitionError, match="terminal failure"):
        ledger.record(stage_id="U0", status="PASS")

    receipt = ledger.record(
        stage_id="CLOSEOUT",
        status="PASS",
        reason_code="FAILED_RUN_REPORTED",
    )
    assert receipt.stage_id == "CLOSEOUT"


def test_stage_ledger_requires_contiguous_retry_attempts(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, StageTransitionError

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="e2e-run-retry")
    ledger.record(stage_id="PREFLIGHT", status="PASS")
    ledger.record(stage_id="RESEARCH", status="PASS")
    ledger.record(stage_id="U0", status="PASS")
    ledger.record(stage_id="L1", status="PASS")
    ledger.record(stage_id="L0", status="PASS")
    ledger.record(stage_id="C0", status="PASS")
    ledger.record(stage_id="L2", status="RETRYABLE", attempt=1, reason_code="PROVIDER_TIMEOUT")

    with pytest.raises(StageTransitionError, match="attempt 2"):
        ledger.record(stage_id="L2", status="PASS", attempt=3)

    receipt = ledger.record(stage_id="L2", status="PASS", attempt=2)
    assert receipt.attempt == 2


def test_stage_ledger_detects_tampering(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, verify_e2e_stage_ledger

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="e2e-run-tamper")
    ledger.record(stage_id="PREFLIGHT", status="PASS")
    payload = json.loads(ledger.path.read_text(encoding="utf-8"))
    payload["entries"][0]["reason_code"] = "ALTERED"
    ledger.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report = verify_e2e_stage_ledger(ledger.path)

    assert report.valid is False
    assert "receipt_digest_mismatch:PREFLIGHT:1" in report.errors


def test_stage_ledger_reports_malformed_attempt_without_throwing(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, verify_e2e_stage_ledger

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="e2e-run-malformed")
    ledger.record(stage_id="PREFLIGHT", status="PASS")
    payload = json.loads(ledger.path.read_text(encoding="utf-8"))
    payload["entries"][0]["attempt"] = {"invalid": True}
    ledger.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report = verify_e2e_stage_ledger(ledger.path)

    assert report.valid is False
    assert "attempt_invalid:PREFLIGHT" in report.errors


def test_launch_receipt_binds_exact_run_directory_without_secret_value(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import emit_e2e_launch_receipt

    output_root = tmp_path / "runs"
    run_dir = output_root / "run-001"
    run_dir.mkdir(parents=True)

    path = emit_e2e_launch_receipt(
        output_root=output_root,
        run_dir=run_dir,
        e2e_run_id="e2e-run-launch",
        command=("python", "-m", "apps_rg", "--fresh-e2e"),
        route_signing_key_id="local-test-key",
        baseline_ref="baseline.json",
        created_at_utc="2026-07-10T00:00:00+00:00",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert Path(payload["run_dir"]).resolve() == run_dir.resolve()
    assert payload["route_signing_key_id"] == "local-test-key"
    assert "secret" not in json.dumps(payload).lower()
    assert payload["command"] == ["python", "-m", "apps_rg", "--fresh-e2e"]


def test_launch_receipt_records_missing_key_id_without_inventing_a_value(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import emit_e2e_launch_receipt

    output_root = tmp_path / "runs"
    run_dir = output_root / "run-001"
    run_dir.mkdir(parents=True)

    path = emit_e2e_launch_receipt(
        output_root=output_root,
        run_dir=run_dir,
        e2e_run_id="e2e-run-launch",
        command=("python", "-m", "apps_rg", "--fresh-e2e"),
        route_signing_key_id="",
        baseline_ref="baseline.json",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["route_signing_key_id"] == ""
    assert payload["route_signing_key_id_present"] is False
    assert "secret" not in json.dumps(payload).lower()


def test_cached_e2e_completion_requires_post_x3_l6_mandatory_and_complete_ledger(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.e2e_stage_ledger import (
        E2EStageLedger,
        validate_cached_e2e_completion,
    )

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="cache-complete")
    for stage_id in (
        "PREFLIGHT",
        "RESEARCH",
        "U0",
        "L1",
        "L0",
        "C0",
        "L2",
        "X1",
        "X2",
        "X3",
        "CANDIDATE",
        "APPS_EVAL",
        "L6_SHADOW",
        "STATE_PROMOTION",
        "CLOSEOUT",
    ):
        output_refs = (
            {
                "research_bridge_response": "research/research_bridge_response.json",
                "delegated_briefing": "research/delegated_briefing.md",
            }
            if stage_id == "RESEARCH"
            else None
        )
        ledger.record(stage_id=stage_id, status="PASS", output_refs=output_refs)
    (tmp_path / "apps_rg_post_x3_completion_receipt.json").write_text(
        json.dumps(
            {
                "completed": True,
                "x3_to_uwg_to_eval_to_l6_completed": True,
                "durable_promotion_committed": True,
            }
        ),
        encoding="utf-8",
    )
    from apps_rg.runtime.run_output_contract import MANDATORY_OUTPUT_FILENAMES

    for filename in MANDATORY_OUTPUT_FILENAMES:
        (tmp_path / filename).write_text("complete", encoding="utf-8")
    producer = tmp_path / "producer"
    producer.mkdir()
    producer_paths = {
        "research_briefing_path": producer / "briefing.md",
        "research_company_brief_path": producer / "company_brief.json",
        "research_handoff_v2_path": producer / "apps_research_apps_rg_handoff_v2.json",
    }
    for path in producer_paths.values():
        path.write_text("complete", encoding="utf-8")
    research_ref = tmp_path / "research" / "research_artifact_ref.json"
    research_ref.parent.mkdir()
    research_ref.write_text(
        json.dumps(
            {
                "research_run_id": "research-child-001",
                "research_artifact_dir": str(producer),
                **{key: str(path) for key, path in producer_paths.items()},
            }
        ),
        encoding="utf-8",
    )

    report = validate_cached_e2e_completion(tmp_path)
    fresh_report = validate_cached_e2e_completion(
        tmp_path,
        require_research_execution=True,
    )

    assert report.valid is True
    assert report.errors == ()
    assert fresh_report.valid is True
    assert fresh_report.errors == ()


def test_cached_e2e_completion_rejects_partial_cache_hit(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import validate_cached_e2e_completion

    (tmp_path / "apps_rg_post_x3_completion_receipt.json").write_text(
        json.dumps({"completed": False}),
        encoding="utf-8",
    )

    report = validate_cached_e2e_completion(tmp_path)

    assert report.valid is False
    assert "stage_ledger_missing" in report.errors
    assert "post_x3_incomplete" in report.errors
    assert "mandatory_output_missing:APPS_RG_MANDATORY_RUN_OUTPUT.json" in report.errors


def test_fresh_completion_requires_executed_research_with_producer_evidence(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger, validate_cached_e2e_completion

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="fresh-research-proof")
    ledger.record(stage_id="PREFLIGHT", status="PASS")
    ledger.record(stage_id="RESEARCH", status="SKIPPED", reason_code="AUTHORIZED_HANDOFF_REUSED")

    report = validate_cached_e2e_completion(tmp_path, require_research_execution=True)

    assert report.valid is False
    assert "research_stage_not_executed" in report.errors
    assert "research_stage_evidence_missing" in report.errors


def test_receipt_derived_entry_binds_exact_authority_bytes(tmp_path: Path) -> None:
    from apps_rg.runtime.e2e_stage_ledger import (
        E2EStageLedger,
        verify_e2e_stage_ledger,
    )

    receipt_path = tmp_path / "preflight.json"
    receipt_path.write_text(
        json.dumps({"schema_version": "test.receipt.v1", "status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    ledger = E2EStageLedger.create(
        artifact_dir=tmp_path,
        e2e_run_id="receipt-derived",
    )
    entry = ledger.record_from_receipt(
        stage_id="PREFLIGHT",
        receipt_ref=receipt_path,
        expected_schema_version="test.receipt.v1",
    )
    expected = "sha256:" + hashlib.sha256(receipt_path.read_bytes()).hexdigest()

    assert entry.status == "PASS"
    assert entry.status_derivation == "AUTHORITATIVE_RECEIPT_BYTES"
    assert entry.authoritative_receipt_sha256 == expected
    assert verify_e2e_stage_ledger(ledger.path).valid is True

    receipt_path.write_text(
        json.dumps({"schema_version": "test.receipt.v1", "status": "FAIL"}) + "\n",
        encoding="utf-8",
    )
    report = verify_e2e_stage_ledger(ledger.path)
    assert report.valid is False
    assert "authoritative_receipt_digest_mismatch:PREFLIGHT:1" in report.errors
    assert "authoritative_receipt_status_mismatch:PREFLIGHT:1" in report.errors


def test_external_ledger_seal_has_no_self_reference_and_detects_later_mutation(
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.e2e_stage_ledger import (
        E2EStageLedger,
        verify_e2e_stage_ledger,
    )

    ledger = E2EStageLedger.create(artifact_dir=tmp_path, e2e_run_id="sealed-ledger")
    for stage_id in (
        "PREFLIGHT",
        "RESEARCH",
        "U0",
        "L1",
        "L0",
        "C0",
        "L2",
        "X1",
        "X2",
        "X3",
        "CANDIDATE",
        "APPS_EVAL",
        "L6_SHADOW",
        "STATE_PROMOTION",
        "CLOSEOUT",
    ):
        ledger.record(stage_id=stage_id, status="PASS")
    seal_path = ledger.seal(
        terminal_state={
            "product_authorized": False,
            "pipeline_complete": False,
            "observability_repair_required": False,
        }
    )
    ledger_bytes = ledger.path.read_bytes()
    seal = json.loads(seal_path.read_text(encoding="utf-8"))

    assert seal["ledger_sha256"] == (
        "sha256:" + hashlib.sha256(ledger_bytes).hexdigest()
    )
    assert seal["compatibility_classification"] == "NON_PRODUCT_ONLY"
    assert "seal" not in json.loads(ledger_bytes)
    assert verify_e2e_stage_ledger(ledger.path).sealed is True

    ledger.path.write_bytes(ledger_bytes + b" ")
    report = verify_e2e_stage_ledger(ledger.path)
    assert report.valid is False
    assert "ledger_seal_digest_mismatch" in report.errors
