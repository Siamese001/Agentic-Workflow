import hashlib
import json
import sqlite3

import pytest

from tools.adg.shared_modules.snapshot_registry import (
    POINTER_FILENAMES,
    SnapshotPointerError,
    load_snapshot_pointer,
    protected_snapshot_run_ids,
    publish_snapshot_pointer,
)


def _db(path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE nodes(id INTEGER)")
    return path


def _manifest(path):
    path.write_text('{"ok": true}\n', encoding="utf-8")
    return path


def test_failed_repair_does_not_replace_certified(tmp_path):
    certified = _db(tmp_path / "adg_indexed_07112026_1200.sqlite")
    manifest = _manifest(tmp_path / "adg_generation_manifest_07112026_1200.json")
    publish_snapshot_pointer(
        adg_dir=tmp_path,
        role="certified",
        snapshot_path=certified,
        certification_status="clean",
        artifact_status="certified",
        source_artifacts={"generation_manifest": manifest},
    )
    before = (tmp_path / POINTER_FILENAMES["certified"]).read_bytes()

    repair = _db(tmp_path / "adg_indexed_07112026_1300.sqlite")
    repair_manifest = _manifest(tmp_path / "adg_generation_manifest_07112026_1300.json")
    publish_snapshot_pointer(
        adg_dir=tmp_path,
        role="repair",
        snapshot_path=repair,
        certification_status="failed",
        artifact_status="repair_ready",
        source_artifacts={"generation_manifest": repair_manifest},
    )

    assert (tmp_path / POINTER_FILENAMES["certified"]).read_bytes() == before
    assert load_snapshot_pointer(tmp_path, "certified", verify_digest=True).path == certified
    assert load_snapshot_pointer(tmp_path, "repair", verify_digest=True).path == repair
    assert protected_snapshot_run_ids(tmp_path) == {"07112026_1200"}


def test_digest_mismatch_fails_closed(tmp_path):
    snapshot = _db(tmp_path / "adg_indexed_07112026_1200.sqlite")
    publish_snapshot_pointer(
        adg_dir=tmp_path,
        role="certified",
        snapshot_path=snapshot,
        certification_status="clean",
        artifact_status="certified",
    )
    payload = json.loads((tmp_path / POINTER_FILENAMES["certified"]).read_text())
    payload["snapshot_sha256"] = hashlib.sha256(b"wrong").hexdigest()
    (tmp_path / POINTER_FILENAMES["certified"]).write_text(json.dumps(payload))

    with pytest.raises(SnapshotPointerError, match="SHA-256 mismatch"):
        load_snapshot_pointer(tmp_path, "certified", verify_digest=True)


def test_source_manifest_tamper_fails_closed(tmp_path):
    snapshot = _db(tmp_path / "adg_indexed_07112026_1200.sqlite")
    manifest = _manifest(tmp_path / "adg_generation_manifest_07112026_1200.json")
    publish_snapshot_pointer(
        adg_dir=tmp_path,
        role="certified",
        snapshot_path=snapshot,
        certification_status="clean",
        artifact_status="certified",
        source_artifacts={"generation_manifest": manifest},
    )
    manifest.write_text("tampered but same?", encoding="utf-8")
    with pytest.raises(SnapshotPointerError, match="source artifact size mismatch|source artifact SHA-256 mismatch"):
        load_snapshot_pointer(tmp_path, "certified", verify_digest=True)


def test_role_contracts_fail_closed(tmp_path):
    snapshot = _db(tmp_path / "adg_indexed_07112026_1200.sqlite")
    with pytest.raises(SnapshotPointerError, match="certified pointer requires"):
        publish_snapshot_pointer(
            adg_dir=tmp_path,
            role="certified",
            snapshot_path=snapshot,
            certification_status="failed",
            artifact_status="repair_ready",
        )
