"""Tests for audit-wrapper snapshot promotion authority."""

from __future__ import annotations

import hashlib
import json
import sqlite3

from tools.adg.run_full_adg_audit import (
    WrapperResult,
    _publish_result_snapshot_pointer,
)
from tools.adg.shared_modules.snapshot_registry import (
    POINTER_FILENAMES,
    load_snapshot_pointer,
)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE nodes(id INTEGER PRIMARY KEY)")
    return path


def _source(path):
    path.write_text(json.dumps({"ok": True}) + "\n", encoding="utf-8")
    return path


def _result(
    *,
    certification_status,
    artifact_status,
    snapshot,
    generation_manifest,
):
    return WrapperResult(
        certification_status=certification_status,
        generator_exit_code=0,
        report_exit_code=0,
        generation_manifest_path=generation_manifest,
        gate_manifest_path=None,
        runtime_proof_status="attested",
        reasons=[],
        artifact_status=artifact_status,
        adg_run_id=snapshot.stem.replace("adg_indexed_", ""),
        repair_handoff={
            "status": artifact_status,
            "artifacts": {
                "snapshot": {
                    "path": str(snapshot),
                    "sha256": _sha(snapshot),
                },
                "generation_manifest": {
                    "path": str(generation_manifest),
                    "sha256": _sha(generation_manifest),
                },
            },
            "validation_errors": [],
        },
    )


def test_failed_audit_never_replaces_certified_pointer(tmp_path):
    certified = _snapshot(
        tmp_path / "adg_indexed_07112026_1200.sqlite"
    )
    certified_manifest = _source(
        tmp_path / "adg_generation_manifest_07112026_1200.json"
    )
    certified_result = _result(
        certification_status="clean",
        artifact_status="certified",
        snapshot=certified,
        generation_manifest=certified_manifest,
    )
    assert _publish_result_snapshot_pointer(
        certified_result,
        artifacts_adg=tmp_path,
    ) == []
    pointer_path = tmp_path / POINTER_FILENAMES["certified"]
    before = pointer_path.read_bytes()

    repair = _snapshot(tmp_path / "adg_indexed_07112026_1300.sqlite")
    repair_manifest = _source(
        tmp_path / "adg_generation_manifest_07112026_1300.json"
    )
    repair_result = _result(
        certification_status="failed",
        artifact_status="repair_ready",
        snapshot=repair,
        generation_manifest=repair_manifest,
    )
    assert _publish_result_snapshot_pointer(
        repair_result,
        artifacts_adg=tmp_path,
    ) == []

    assert pointer_path.read_bytes() == before
    assert load_snapshot_pointer(
        tmp_path,
        "certified",
        verify_digest=True,
    ).path == certified
    assert load_snapshot_pointer(
        tmp_path,
        "repair",
        verify_digest=True,
    ).path == repair


def test_clean_result_with_missing_snapshot_cannot_promote(tmp_path):
    result = WrapperResult(
        certification_status="clean",
        generator_exit_code=0,
        report_exit_code=0,
        generation_manifest_path=None,
        gate_manifest_path=None,
        runtime_proof_status="attested",
        reasons=[],
        artifact_status="certified",
        repair_handoff={"artifacts": {}},
    )

    errors = _publish_result_snapshot_pointer(
        result,
        artifacts_adg=tmp_path,
    )

    assert errors
    assert not (tmp_path / POINTER_FILENAMES["certified"]).exists()
