from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_rg.runtime.mandatory_outputs import (
    MANDATORY_OUTPUT_COMMIT_MANIFEST,
    PRODUCT_MANDATORY_OUTPUT_PROFILE,
    apply_mandatory_closeout_state,
    begin_mandatory_output_transaction,
    seal_mandatory_output_bundle,
    validate_mandatory_output_seal,
)


def test_marker_is_written_last_and_binds_exact_bytes(tmp_path: Path) -> None:
    extra = tmp_path / "l7.md"
    extra.write_bytes(b"L7\n")
    manifest = seal_mandatory_output_bundle(
        tmp_path,
        {"a.md": b"A\n", "nested/b.json": b"{}\n"},
        additional_files={"l7": extra},
    )
    assert (tmp_path / MANDATORY_OUTPUT_COMMIT_MANIFEST).is_file()
    assert manifest["bundle_digest"].startswith("sha256:")
    assert validate_mandatory_output_seal(tmp_path) == (True, [])


def test_byte_tamper_invalidates_seal(tmp_path: Path) -> None:
    seal_mandatory_output_bundle(tmp_path, {"a.md": b"A\n"})
    (tmp_path / "a.md").write_bytes(b"tampered\n")
    valid, errors = validate_mandatory_output_seal(tmp_path)
    assert valid is False
    assert "mandatory_output_artifact_digest_mismatch:a.md" in errors


def test_product_profile_and_external_artifact_set_are_enforced(tmp_path: Path) -> None:
    seal_mandatory_output_bundle(
        tmp_path,
        {"a.md": b"A\n", "b.json": b"{}\n"},
        profile_id=PRODUCT_MANDATORY_OUTPUT_PROFILE,
        required_artifacts=("a.md", "b.json"),
    )
    valid, errors = validate_mandatory_output_seal(
        tmp_path,
        expected_profile_id=PRODUCT_MANDATORY_OUTPUT_PROFILE,
        expected_artifacts=("a.md", "b.json"),
    )
    assert valid is True
    assert errors == []

    valid, errors = validate_mandatory_output_seal(
        tmp_path,
        expected_profile_id="apps_rg.mandatory_outputs.closeout.v1",
        expected_artifacts=("a.md", "b.json"),
    )
    assert valid is False
    assert "mandatory_output_profile_mismatch" in errors


def test_self_consistent_manifest_substitution_cannot_shrink_expected_set(
    tmp_path: Path,
) -> None:
    seal_mandatory_output_bundle(
        tmp_path,
        {"a.md": b"A\n", "b.json": b"{}\n"},
        profile_id=PRODUCT_MANDATORY_OUTPUT_PROFILE,
        required_artifacts=("a.md", "b.json"),
    )
    marker = tmp_path / MANDATORY_OUTPUT_COMMIT_MANIFEST
    manifest = json.loads(marker.read_text(encoding="utf-8"))
    manifest["artifacts"].pop("b.json")
    manifest["required_artifacts"].remove("b.json")
    manifest.pop("bundle_digest")
    seed = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    manifest["bundle_digest"] = "sha256:" + hashlib.sha256(seed).hexdigest()
    marker.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    valid, errors = validate_mandatory_output_seal(
        tmp_path,
        expected_profile_id=PRODUCT_MANDATORY_OUTPUT_PROFILE,
        expected_artifacts=("a.md", "b.json"),
    )
    assert valid is False
    assert "mandatory_output_expected_artifact_set_mismatch" in errors


def test_starting_new_transaction_removes_stale_marker(tmp_path: Path) -> None:
    seal_mandatory_output_bundle(tmp_path, {"a.md": b"A\n"})
    begin_mandatory_output_transaction(tmp_path)
    assert not (tmp_path / MANDATORY_OUTPUT_COMMIT_MANIFEST).exists()


def test_closeout_failure_preserves_closed_product_authorization() -> None:
    result = apply_mandatory_closeout_state(
        {
            "result_summary": {
                "outcome_authorized": True,
                "pipeline_complete": True,
                "completion_fault": "upstream",
            }
        },
        {"pass": False, "errors": ["missing"]},
        failure_code="MANDATORY_OUTPUTS_INCOMPLETE",
    )
    summary = result["result_summary"]
    assert summary["product_authorized"] is True
    assert summary["outcome_authorized"] is True
    assert summary["pipeline_complete"] is False
    assert summary["observability_repair_required"] is True
    assert summary["mandatory_output_upstream_completion_fault"] == "upstream"


def test_passing_closeout_preserves_upstream_observability_repair() -> None:
    result = apply_mandatory_closeout_state(
        {
            "result_summary": {
                "product_authorized": True,
                "pipeline_complete": False,
                "observability_repair_required": True,
            }
        },
        {"pass": True, "errors": []},
        failure_code="MANDATORY_OUTPUTS_INCOMPLETE",
    )

    summary = result["result_summary"]
    assert summary["product_authorized"] is True
    assert summary["pipeline_complete"] is False
    assert summary["observability_repair_required"] is True
