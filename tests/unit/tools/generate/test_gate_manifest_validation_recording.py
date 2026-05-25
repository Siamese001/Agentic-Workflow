"""Manifest recording for post-commit validation gates."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate._gate_manifest import (
    GateManifestRecorder,
    run_recorded_validation,
    set_current_recorder,
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
    recorder: GateManifestRecorder, tmp_path: Path,
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
