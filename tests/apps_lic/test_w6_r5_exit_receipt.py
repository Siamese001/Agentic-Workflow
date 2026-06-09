"""W6 terminal R5 Exit-compatible proof normalization."""

from __future__ import annotations

import json
from pathlib import Path

from apps_lic.runtime.bindings.exit_binding import (
    TERMINAL_R5_NO_L4_WRITE_RECEIPT,
    TERMINAL_R5_NO_SEND_RECEIPT,
    TERMINAL_R5_RUNTIME_EXHAUST_REF,
)
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.dispatch.runtime_proof_bundle import (
    FILENAME_RUNTIME_PROOF_BUNDLE,
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_terminal_r5_emits_exit_compatible_denial_receipt(tmp_path: Path) -> None:
    raw = build_cli_ingress_raw(manual_brief="", allow_research=False)
    result = run_canonical_apps_lic_spine(
        raw,
        artifact_root=tmp_path / "r5",
        skip_r3r4_research=True,
    )

    assert result.terminal_r5 is True
    assert result.x3_disposition == "DENY"
    assert result.exit_status == "blocked"
    assert result.outcome_authorized is False
    assert result.c0_invoked is False
    assert result.pa_invoked is False
    assert result.l2_executed is False

    manifest = _load_json(result.artifact_dir / "spine_run_manifest.json")
    assert manifest["stage_receipt_refs"] == [
        "ingress_raw.json",
        "u0_receipt.json",
        "l1_plan_contract.json",
        "route_contract.json",
        "exit_disposition_receipt.json",
        "spine_run_manifest.json",
    ]
    assert manifest["trace_root"] == result.trace_id
    assert manifest["route_family"] == "R5_FALLBACK"
    assert manifest["terminal_reason"]
    assert manifest["exit_disposition"] == "blocked"
    assert manifest["no_send_receipt"] == TERMINAL_R5_NO_SEND_RECEIPT
    assert manifest["no_l4_write_receipt"] == TERMINAL_R5_NO_L4_WRITE_RECEIPT
    assert manifest["runtime_exhaust_ref"] == TERMINAL_R5_RUNTIME_EXHAUST_REF

    exit_receipt = _load_json(result.artifact_dir / "exit_disposition_receipt.json")
    assert exit_receipt["stage"] == "EXIT"
    assert exit_receipt["upstream_receipt_refs"] == ["route_contract.json"]
    assert exit_receipt["downstream_receipt_refs"] == ["spine_run_manifest.json"]
    assert exit_receipt["payload"]["x3_disposition"] == "DENY"
    assert exit_receipt["payload"]["exit_status"] == "blocked"
    assert exit_receipt["payload"]["outcome_authorized"] is False
    final_output = exit_receipt["payload"]["final_output"]
    assert final_output["terminal_r5"] is True
    assert final_output["route_family"] == "R5_FALLBACK"
    assert final_output["no_send_receipt"] == TERMINAL_R5_NO_SEND_RECEIPT
    assert final_output["no_l4_write_receipt"] == TERMINAL_R5_NO_L4_WRITE_RECEIPT
    assert final_output["runtime_exhaust_ref"] == TERMINAL_R5_RUNTIME_EXHAUST_REF

    proof_bundle = _load_json(result.artifact_dir / FILENAME_RUNTIME_PROOF_BUNDLE)
    assert proof_bundle["status"] == "PASS"
    assert proof_bundle["proof_mode"] == "terminal_r5"
    assert proof_bundle["canonical_stage_order"] == ["INGRESS", "U0", "L1", "L0", "EXIT"]
    assert proof_bundle["checks"]["single_exit_x3"] == []
    assert proof_bundle["checks"]["receipt_chain"] == []
    assert (
        "terminal_r5_exit_receipt_deny_by_design"
        in proof_bundle["checks"]["r5_terminal_exit_policy"]
    )

    for forbidden in (
        "c0_final_evidence_contract.json",
        "c03_sender_proof_packet.json",
        "pa_receipt.json",
        "l3_workflow_receipt.json",
        "l2_execution_receipt.json",
        "w4_candidate_batch.json",
        "c03_postgen_claim_validation.json",
        "w5_validation_exit.json",
    ):
        assert not (result.artifact_dir / forbidden).exists()
