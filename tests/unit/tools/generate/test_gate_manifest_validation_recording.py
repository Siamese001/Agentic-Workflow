"""Manifest recording for post-commit validation gates."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate._gate_manifest import (
    GateManifestRecorder,
    run_recorded_validation,
    runtime_proof_from_sqlite,
    seal_sqlite_snapshot,
    set_current_recorder,
    sqlite_snapshot_sidecars,
)
from tools.generate._required_gates import required_gate_names
from tools.generate.integration.deferred_failures import (
    record_failure,
    reset_for_tests,
)


@pytest.fixture(autouse=True)
def _reset_deferred_registry() -> None:
    reset_for_tests()
    yield
    reset_for_tests()
    set_current_recorder(None)


@pytest.fixture
def recorder(tmp_path: Path) -> GateManifestRecorder:
    rec = GateManifestRecorder(tmp_path, "test01")
    set_current_recorder(rec)
    return rec


def test_run_recorded_validation_pass(recorder: GateManifestRecorder) -> None:
    def _ok() -> None:
        return None

    run_recorded_validation("p0_violations", _ok)
    names = {r.name for r in recorder.records}
    assert "p0_violations" in names
    row = next(r for r in recorder.records if r.name == "p0_violations")
    assert row.status == "pass"
    assert row.phase == "post-commit-validation"
    assert row.kind == "validation"


def test_run_recorded_validation_fail_on_system_exit(recorder: GateManifestRecorder) -> None:
    def _boom() -> None:
        raise SystemExit(1)

    with pytest.raises(SystemExit):
        run_recorded_validation("p2_ratchet", _boom)
    row = next(r for r in recorder.records if r.name == "p2_ratchet")
    assert row.status == "fail"
    assert row.phase == "build"


def test_run_recorded_validation_deferred_fail(monkeypatch, recorder: GateManifestRecorder) -> None:
    monkeypatch.setenv("ADG_CONTINUE_ON_GATE_FAILURE", "1")

    def _defer() -> None:
        record_failure("P2_ratchet", 1, message="ratchet regression")

    run_recorded_validation("p2_ratchet", _defer)
    row = next(r for r in recorder.records if r.name == "p2_ratchet")
    assert row.status == "deferred_fail"


def test_finalize_manifest_satisfies_required_gate_cross_check(
    recorder: GateManifestRecorder,
    tmp_path: Path,
) -> None:
    from tools.adg.run_full_adg_audit import _cross_check_required_gates

    sqlite = tmp_path / "adg_indexed_test01.sqlite"
    sqlite.write_bytes(b"")
    for name in sorted(required_gate_names()):
        if name in {
            "mcp_config_drift",
            "wal_checkpoint",
            "locked_files",
            "wiring",
            "config-ref",
            "lifecycle",
            "except-contract",
            "test-coverage",
        }:
            recorder.record(
                name,
                phase="preflight",
                kind="python_function",
                blocking_mode="hard_fail",
                status="pass",
            )
        elif name == "p2_ratchet":
            recorder.record_validation_gate("p2_ratchet", status="pass")
        else:
            recorder.record_validation_gate(name, status="pass")

    recorder.finalize(sqlite_path=sqlite, generation_exit_code=0, p0_status="pass")
    gate_manifest_path = tmp_path / "adg_gate_invocation_manifest_test01.json"
    import json

    manifest = json.loads(gate_manifest_path.read_text(encoding="utf-8"))
    reasons = _cross_check_required_gates(manifest)
    assert reasons == [], reasons


def test_required_validation_gates_are_recordable_names() -> None:
    expected = {
        "p0_violations",
        "p1_ratchet",
        "p2_ratchet",
        "dead_production_imports",
        "structural_conformance",
        "agentic_antipatterns",
        "witness_tier_gates",
    }
    assert expected <= required_gate_names()


def test_runtime_proof_reads_exact_snapshot_without_mutation(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot.sqlite"
    con = sqlite3.connect(snapshot)
    try:
        con.execute("CREATE TABLE v_runtime_proof (static_edge_id INT, attesting_trace_count INT)")
        con.execute("INSERT INTO v_runtime_proof(static_edge_id, attesting_trace_count) VALUES (1, 1)")
        con.commit()
    finally:
        con.close()
    before = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    directory_entries_before = {path.name for path in tmp_path.iterdir()}

    assert runtime_proof_from_sqlite(snapshot) == ("attested", 1)
    assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == before
    assert {path.name for path in tmp_path.iterdir()} == directory_entries_before


def test_runtime_proof_missing_snapshot_is_unreadable_and_not_created(tmp_path: Path) -> None:
    snapshot = tmp_path / "deleted.sqlite"

    assert runtime_proof_from_sqlite(snapshot) == ("snapshot_unreadable", 0)
    assert not snapshot.exists()


def test_runtime_proof_connect_failure_is_explicitly_unreadable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshot = tmp_path / "locked.sqlite"
    snapshot.write_bytes(b"locked fixture")

    monkeypatch.setattr(
        sqlite3,
        "connect",
        mock.Mock(side_effect=sqlite3.OperationalError("database is locked")),
    )

    assert runtime_proof_from_sqlite(snapshot) == ("snapshot_unreadable", 0)


def test_runtime_proof_first_query_failure_is_explicitly_unreadable(
    tmp_path: Path,
) -> None:
    snapshot = tmp_path / "unreadable.sqlite"
    snapshot.write_bytes(b"not a sqlite database")

    assert runtime_proof_from_sqlite(snapshot) == ("snapshot_unreadable", 0)


def test_runtime_proof_rejects_undigested_sqlite_sidecar(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot.sqlite"
    con = sqlite3.connect(snapshot)
    try:
        con.execute("CREATE TABLE v_runtime_proof (static_edge_id INT, attesting_trace_count INT)")
        con.execute("INSERT INTO v_runtime_proof VALUES (1, 1)")
        con.commit()
    finally:
        con.close()
    Path(str(snapshot) + "-wal").write_bytes(b"undigested committed state")

    assert runtime_proof_from_sqlite(snapshot) == ("snapshot_unreadable", 0)


def test_seal_sqlite_snapshot_normalizes_journal_authority(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot.sqlite"
    con = sqlite3.connect(snapshot)
    try:
        assert con.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        con.execute("CREATE TABLE proof (value TEXT)")
        con.execute("INSERT INTO proof VALUES ('sealed')")
        con.commit()
    finally:
        con.close()

    seal_sqlite_snapshot(snapshot)

    assert sqlite_snapshot_sidecars(snapshot) == ()
    con = sqlite3.connect(snapshot.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        assert con.execute("SELECT value FROM proof").fetchone() == ("sealed",)
        assert con.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
    finally:
        con.close()


def test_unreadable_runtime_proof_forces_failed_generation_manifest(
    recorder: GateManifestRecorder,
    tmp_path: Path,
) -> None:
    snapshot = tmp_path / "snapshot.sqlite"
    snapshot.write_bytes(b"not a sqlite database")

    recorder.finalize(
        sqlite_path=snapshot,
        generation_exit_code=0,
        runtime_proof_status="snapshot_unreadable",
    )

    gate_manifest = json.loads(
        (tmp_path / "adg_gate_invocation_manifest_test01.json").read_text(encoding="utf-8")
    )
    generation_manifest = json.loads(
        (tmp_path / "adg_generation_manifest_test01.json").read_text(encoding="utf-8")
    )
    latest_generation_manifest = json.loads(
        (tmp_path / "adg_generation_manifest_latest.json").read_text(encoding="utf-8")
    )
    assert gate_manifest["certification_status"] == "failed"
    assert generation_manifest["certification_status"] == "failed"
    assert latest_generation_manifest == generation_manifest
    assert generation_manifest["snapshot_sha256"] == hashlib.sha256(snapshot.read_bytes()).hexdigest()
    assert list(tmp_path.glob("*.tmp")) == []


def test_sidecar_forces_failed_manifest_without_main_file_digest(
    recorder: GateManifestRecorder,
    tmp_path: Path,
) -> None:
    snapshot = tmp_path / "snapshot.sqlite"
    snapshot.write_bytes(b"main-file")
    Path(str(snapshot) + "-wal").write_bytes(b"outside-digest")

    recorder.finalize(
        sqlite_path=snapshot,
        generation_exit_code=0,
        runtime_proof_status="snapshot_unreadable",
        commit_sha="snapshot-commit",
        repo_state_hash="snapshot-tree",
    )

    generation_manifest = json.loads(
        (tmp_path / "adg_generation_manifest_test01.json").read_text(encoding="utf-8")
    )
    assert generation_manifest["certification_status"] == "failed"
    assert generation_manifest["snapshot_sha256"] is None
