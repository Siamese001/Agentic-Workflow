"""R1B durable-write authority is X3C-only and fail-closed."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.cache.r1b_commit_authority import (
    REASON_X3C_REQUIRED,
    REASON_X3_MALFORMED,
    REASON_X3_MISSING,
    assess_r1b_commit_authority,
    assess_r1b_commit_authority_from_run_dir,
    compute_r1b_commit_request_signature,
    validate_r1b_commit_request_evidence,
)


def _write_x3(run_dir: Path, code: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": code}),
        encoding="utf-8",
    )


def test_x3c_authorizes_r1b_commit_request() -> None:
    decision = assess_r1b_commit_authority(x3_code="x3c")
    assert decision.authorized is True
    assert decision.x3_code == "X3C"
    assert decision.reason_code == ""


@pytest.mark.parametrize("finish_code", ["X3_ALLOW", "X3D", "EXIT_OK", "EXIT_PARTIAL"])
def test_finish_outcomes_do_not_authorize_durable_r1b_write(finish_code: str) -> None:
    decision = assess_r1b_commit_authority(x3_code=finish_code)
    assert decision.authorized is False
    assert decision.reason_code == REASON_X3C_REQUIRED


def test_missing_x3_artifact_fails_closed(tmp_path: Path) -> None:
    decision = assess_r1b_commit_authority_from_run_dir(tmp_path)
    assert decision.authorized is False
    assert decision.reason_code == REASON_X3_MISSING


def test_malformed_x3_artifact_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "x3_disposition.json").write_text("not-json", encoding="utf-8")
    decision = assess_r1b_commit_authority_from_run_dir(tmp_path)
    assert decision.authorized is False
    assert decision.reason_code == REASON_X3_MALFORMED


def test_run_dir_x3c_authority_is_loaded_from_artifact(tmp_path: Path) -> None:
    _write_x3(tmp_path, "X3C")
    decision = assess_r1b_commit_authority_from_run_dir(tmp_path)
    assert decision.authorized is True
    assert decision.disposition_ref.endswith("x3_disposition.json")


def _request(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "commit_request_id": "cr:r1b:test",
        "staged_diff_hash": "diff:test",
        "clearance_proof_id": "exit:test",
        "cleared_exit_review_packet_ref": "exit:test",
        "capability_token_ref": "capability:r1b:test",
        "registry_digest_set": ("registry:policy:test", "registry:blueprint:test"),
    }
    values["commit_request_signature"] = compute_r1b_commit_request_signature(
        commit_request_id=str(values["commit_request_id"]),
        staged_diff_hash=str(values["staged_diff_hash"]),
        clearance_proof_id=str(values["clearance_proof_id"]),
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_valid_r1b_commit_evidence_has_no_extra_failures() -> None:
    failed, reasons = validate_r1b_commit_request_evidence(_request())
    assert failed == ()
    assert reasons == ()


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"commit_request_signature": "forged"}, "commit_request_signature_invalid"),
        ({"capability_token_ref": ""}, "missing_or_placeholder_capability_token_ref"),
        ({"clearance_proof_id": "different"}, "clearance_proof_binding_mismatch"),
        ({"registry_digest_set": ("unknown",)}, "missing_or_placeholder_registry_digest_set"),
        (
            {"registry_digest_set": ("registry:test", "registry:test")},
            "duplicate_registry_digest",
        ),
    ],
)
def test_invalid_r1b_commit_evidence_fails_closed(
    overrides: dict[str, object],
    reason: str,
) -> None:
    _failed, reasons = validate_r1b_commit_request_evidence(_request(**overrides))
    assert reason in reasons
