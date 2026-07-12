"""Negative controls for Exit/X3C and R1B commit evidence authority."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from apps_rg.cache.r1b_commit_authority import (
    REASON_X3C_REQUIRED,
    assess_r1b_commit_authority,
    assess_r1b_commit_authority_from_run_dir,
    compute_r1b_commit_request_signature,
    validate_r1b_commit_request_evidence,
)
from apps_rg.cache.r1b_constants import R1B_UWG_TARGET_SURFACE
from apps_rg.runtime.l5.packet_builder import compute_l5_packet_verification_digest


def _request(**overrides):
    request_id = "request-1"
    run_id = "run-1"
    trace_root = "trace-1"
    packet_digest = "d" * 64
    runtime_binding = "b" * 64
    packet_ref = f"l5_packet:{packet_digest}"
    verification = compute_l5_packet_verification_digest(
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_root,
        packet_ref=packet_ref,
        packet_digest=packet_digest,
        status="L5_CERTIFIED",
        runtime_binding_digest_value=runtime_binding,
    )
    values = {
        "commit_request_id": "cr-1",
        "request_id": request_id,
        "run_id": run_id,
        "trace_root": trace_root,
        "policy_hash": "policy-1",
        "blueprint_hash": "blueprint-1",
        "staged_diff_hash": "diff-1",
        "clearance_proof_id": "exit_packet_digest:abc",
        "cleared_exit_review_packet_ref": "exit_packet_digest:abc",
        "capability_token_ref": "capability:apps_rg:r1b:run-1",
        "registry_digest_set": (
            "registry:policy:policy-1",
            "registry:blueprint:blueprint-1",
        ),
        "affected_state_surfaces": (R1B_UWG_TARGET_SURFACE,),
        "l5_certification_ref": packet_ref,
        "l5_certification_refs": (
            f"packet_digest={packet_digest}",
            "status=L5_CERTIFIED",
            f"runtime_binding_digest={runtime_binding}",
            "verified=true",
            f"verification_digest={verification}",
        ),
    }
    values["commit_request_signature"] = compute_r1b_commit_request_signature(
        commit_request_id=values["commit_request_id"],
        staged_diff_hash=values["staged_diff_hash"],
        clearance_proof_id=values["clearance_proof_id"],
        l5_packet_digest=packet_digest,
        l5_verification_digest=verification,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_literal_x3c_is_the_only_commit_authority() -> None:
    assert assess_r1b_commit_authority(x3_code="X3C").authorized is True
    for finish_code in ("X3_ALLOW", "X3D", "EXIT_OK", "EXIT_PARTIAL"):
        result = assess_r1b_commit_authority(x3_code=finish_code)
        assert result.authorized is False
        assert result.reason_code == REASON_X3C_REQUIRED


def test_run_dir_authority_fails_closed_on_missing_or_malformed(tmp_path: Path) -> None:
    assert assess_r1b_commit_authority_from_run_dir(tmp_path).authorized is False
    (tmp_path / "x3_disposition.json").write_text("[]", encoding="utf-8")
    assert assess_r1b_commit_authority_from_run_dir(tmp_path).authorized is False
    (tmp_path / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3C"}), encoding="utf-8"
    )
    assert assess_r1b_commit_authority_from_run_dir(tmp_path).authorized is True


def test_valid_evidence_passes() -> None:
    assert validate_r1b_commit_request_evidence(_request()) == ((), ())


def test_forged_signature_fails_closed() -> None:
    failed, reasons = validate_r1b_commit_request_evidence(
        _request(commit_request_signature="forged")
    )
    assert "r1b_commit_request_signature" in failed
    assert "commit_request_signature_invalid" in reasons


def test_l5_verification_digest_is_recomputed() -> None:
    request = _request()
    refs = tuple(
        "verification_digest=forged"
        if item.startswith("verification_digest=")
        else item
        for item in request.l5_certification_refs
    )
    failed, reasons = validate_r1b_commit_request_evidence(
        _request(l5_certification_refs=refs)
    )
    assert "r1b_l5_certification_evidence" in failed
    assert "l5_certification_evidence_not_verified" in reasons


def test_capability_registry_clearance_and_surface_are_bound() -> None:
    variants = (
        (
            _request(capability_token_ref="capability:other"),
            "missing_or_invalid_capability_token_ref",
        ),
        (
            _request(registry_digest_set=("registry:other",)),
            "registry_digest_binding_mismatch",
        ),
        (_request(clearance_proof_id="different"), "clearance_proof_binding_mismatch"),
        (
            _request(affected_state_surfaces=("l4.other",)),
            "target_surface_not_allowlisted",
        ),
    )
    for request, expected in variants:
        _failed, reasons = validate_r1b_commit_request_evidence(request)
        assert expected in reasons
