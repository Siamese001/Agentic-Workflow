"""Tests for ``tools/adg/run_full_adg_audit.py`` (wrapper).

Plan: ``.windsurf/plans/adg-audit-pipeline-integration-7f2c93.md`` W4.1.

Strategy: mock ``subprocess.run`` inside ``run_full_adg_audit`` so we
exercise manifest discovery + required-gate cross-check + certification
classification without launching real subprocesses. A single shared
fixture paints the manifests the wrapper expects to read.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest import mock

import pytest

from tools.adg import run_full_adg_audit as wrapper
from tools.generate._required_gates import required_gate_names


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def temp_artifacts(tmp_path, monkeypatch):
    """Redirect the wrapper's manifest/receipt paths into a sandbox."""
    monkeypatch.setattr(wrapper, "ARTIFACTS_ADG", tmp_path / "artifacts" / "adg")
    monkeypatch.setattr(wrapper, "RECEIPT_PATH", tmp_path / "docs" / "receipt.json")
    wrapper.ARTIFACTS_ADG.mkdir(parents=True, exist_ok=True)
    return tmp_path


def _make_snapshot(path: Path, *, with_runtime_view: bool, attested: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    try:
        con.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, resolved_path TEXT, file_path TEXT, adg_name TEXT)")
        con.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INT, dst_id INT, relation_type TEXT, authority TEXT)")
        if with_runtime_view:
            con.execute(
                "CREATE TABLE v_runtime_proof (static_edge_id INT, attesting_trace_count INT)"
            )
            for _ in range(attested):
                con.execute("INSERT INTO v_runtime_proof(static_edge_id, attesting_trace_count) VALUES (NULL, 1)")
        con.commit()
    finally:
        con.close()
    return path


def _write_manifests(
    artifacts_dir: Path,
    *,
    ts: str = "test01",
    snapshot: Path,
    runtime_proof_status: str = "attested",
    runtime_attested: int = 5,
    generation_exit_code: int = 0,
    gates: list[dict] | None = None,
) -> tuple[Path, Path]:
    """Write a (gate_manifest, generation_manifest) pair."""
    if gates is None:
        # Include every required gate with status=pass so the wrapper
        # cross-check passes.
        gates = [
            {
                "name": name,
                "phase": "preflight",
                "kind": "python_function",
                "blocking_mode": "hard_fail",
                "status": "pass",
                "exit_code": 0,
                "duration_s": 0.01,
                "started_at_utc": "2026-01-01T00:00:00Z",
                "finished_at_utc": "2026-01-01T00:00:00Z",
                "script_rel": None,
                "message": None,
            }
            for name in sorted(required_gate_names())
        ]
    gate_manifest = {
        "timestamp": "2026-01-01T00:00:00Z",
        "generator_entrypoint": "tools/generate/generate_full_adg.py",
        "sqlite_path": str(snapshot),
        "generation_exit_code": generation_exit_code,
        "certification_status": "clean" if generation_exit_code == 0 else "failed",
        "gates": gates,
        "unexpected_skips": [],
        "failed_gates": [],
        "deferred_failures": [],
    }
    gate_manifest_path = artifacts_dir / f"adg_gate_invocation_manifest_{ts}.json"
    gate_manifest_path.write_text(json.dumps(gate_manifest), encoding="utf-8")

    gen_manifest = {
        "timestamp": "2026-01-01T00:00:01Z",
        "sqlite_path": str(snapshot),
        "snapshot_path": str(snapshot),
        "commit_sha": None,
        "repo_state_hash": None,
        "generation_exit_code": generation_exit_code,
        "p0_status": "pass",
        "gate_manifest_path": str(gate_manifest_path),
        "runtime_proof_status": runtime_proof_status,
        "runtime_attested_edge_count": runtime_attested,
        "registry_bucket_edge_count": 0,
        "created_at_utc": "2026-01-01T00:00:01Z",
        "certification_status": "clean" if generation_exit_code == 0 else "failed",
    }
    gen_manifest_path = artifacts_dir / f"adg_generation_manifest_{ts}.json"
    gen_manifest_path.write_text(json.dumps(gen_manifest), encoding="utf-8")
    return gate_manifest_path, gen_manifest_path


def _patch_generator(monkeypatch, *, return_code: int = 0, writes_manifests: bool = True,
                     snapshot: Path | None = None, gate_kwargs: dict | None = None,
                     runtime_proof_status: str = "attested", runtime_attested: int = 5) -> mock.Mock:
    """Patch ``_run_generator`` to simulate the generator writing manifests."""
    def _fake(extra_args, timeout_s, certification_mode):  # noqa: ARG001
        if writes_manifests and snapshot is not None:
            _write_manifests(
                wrapper.ARTIFACTS_ADG,
                snapshot=snapshot,
                runtime_proof_status=runtime_proof_status,
                runtime_attested=runtime_attested,
                generation_exit_code=return_code,
                **(gate_kwargs or {}),
            )
        return return_code

    m = mock.Mock(side_effect=_fake)
    monkeypatch.setattr(wrapper, "_run_generator", m)
    return m


def _patch_report(monkeypatch, *, return_code: int = 0) -> mock.Mock:
    m = mock.Mock(return_value=return_code)
    monkeypatch.setattr(wrapper, "_run_report", m)
    return m


# ---------------------------------------------------------------------------
# Tests (plan §10 cases 1..18)
# ---------------------------------------------------------------------------
def test_certification_stops_when_generator_exit_nonzero(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, return_code=5, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert result.generator_exit_code == 5
    assert any("generator exit_code=5" in r for r in result.reasons)


def test_diagnostic_mode_continues_and_labels_output_diagnostic(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, return_code=5, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="diagnostic", diagnostic_allow_failed_generator=True)
    assert result.certification_status == "diagnostic_only"


def test_wrapper_passes_explicit_snapshot_to_report(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    report_mock = _patch_report(monkeypatch)
    wrapper.run_audit(mode="certification")
    assert report_mock.call_count == 1
    # Snapshot passed as kwarg; verify the path matches.
    call_kwargs = report_mock.call_args.kwargs
    assert Path(call_kwargs["snapshot"]).resolve() == snap.resolve()


def test_certification_fails_when_gate_invocation_manifest_missing(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    # Generator runs but writes ONLY the generation manifest (simulate crash mid-finalize).
    def _fake(extra_args, timeout_s, certification_mode):  # noqa: ARG001
        gen = {
            "timestamp": "x", "sqlite_path": str(snap), "snapshot_path": str(snap),
            "commit_sha": None, "repo_state_hash": None, "generation_exit_code": 0,
            "p0_status": "pass",
            "gate_manifest_path": str(temp_artifacts / "artifacts" / "adg" / "nonexistent.json"),
            "runtime_proof_status": "attested", "runtime_attested_edge_count": 1,
            "registry_bucket_edge_count": 0, "created_at_utc": "x", "certification_status": "clean",
        }
        (wrapper.ARTIFACTS_ADG / "adg_generation_manifest_test.json").write_text(json.dumps(gen))
        return 0

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_fake))
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert any("gate manifest path declared but missing" in r for r in result.reasons)


def test_certification_fails_when_required_gate_absent_from_manifest(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    # Build manifest with ONLY a subset of required gates.
    partial_gates = [{
        "name": "mcp_config_drift", "phase": "preflight", "kind": "python_function",
        "blocking_mode": "hard_fail", "status": "pass", "exit_code": 0,
        "duration_s": 0.01, "started_at_utc": "x", "finished_at_utc": "x",
        "script_rel": None, "message": None,
    }]
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": partial_gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert any("absent from manifest" in r for r in result.reasons)


def test_certification_fails_when_required_gate_skip_without_diagnostic_mode(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = []
    for name in sorted(required_gate_names()):
        gates.append({
            "name": name, "phase": "preflight", "kind": "python_function",
            "blocking_mode": "hard_fail",
            "status": "missing_script" if name == "wiring" else "pass",
            "exit_code": None, "duration_s": 0.0,
            "started_at_utc": "x", "finished_at_utc": "x",
            "script_rel": "ops_scripts/ci/check_expected_wiring.py",
            "message": None,
        })
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert any("wiring" in r and "missing_script" in r for r in result.reasons)


def test_missing_post_adg_hard_gate_script_fails_certification(temp_artifacts, monkeypatch):
    # Same as above but using any required gate — ensures categorical behavior.
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = []
    for name in sorted(required_gate_names()):
        gates.append({
            "name": name, "phase": "post-ADG-subprocess", "kind": "subprocess",
            "blocking_mode": "hard_fail",
            "status": "missing_script" if name == "test-coverage" else "pass",
            "exit_code": None, "duration_s": 0.0,
            "started_at_utc": "x", "finished_at_utc": "x",
            "script_rel": "ops_scripts/ci/check_test_harness_coverage.py",
            "message": None,
        })
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"


def test_post_adg_subprocess_ci_failure_exits_nonzero(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = []
    for name in sorted(required_gate_names()):
        gates.append({
            "name": name, "phase": "post-ADG-subprocess", "kind": "subprocess",
            "blocking_mode": "hard_fail",
            "status": "fail" if name == "lifecycle" else "pass",
            "exit_code": 1, "duration_s": 0.0,
            "started_at_utc": "x", "finished_at_utc": "x",
            "script_rel": None, "message": None,
        })
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"


def test_p0_failure_halts_in_normal_mode(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, return_code=1, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"


def test_p0_failure_with_continue_on_p0_completes_diagnostics_but_exits_nonzero(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gen_mock = _patch_generator(monkeypatch, return_code=1, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification", continue_on_p0=True)
    # Generator was invoked with --continue-on-p0 in extra_args.
    assert "--continue-on-p0" in gen_mock.call_args.kwargs["extra_args"]
    assert result.certification_status == "failed"


def test_gate_invocation_manifest_is_written(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.gate_manifest_path is not None
    assert result.gate_manifest_path.is_file()


@pytest.mark.parametrize("gate_name", ["dead_production_imports", "structural_conformance",
                                        "witness_tier_gates", "p0_violations"])
def test_required_validation_gate_recorded_as_invoked(temp_artifacts, monkeypatch, gate_name):
    """Umbrella for: dead_production_imports, structural_conformance, witness_tier, closure (p0_violations)."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.gate_manifest_path is not None
    manifest = json.loads(result.gate_manifest_path.read_text())
    names = {g["name"] for g in manifest["gates"]}
    assert gate_name in names


def test_subprocess_calls_use_sys_executable_and_shell_false_and_timeout(temp_artifacts, monkeypatch):
    """Verify the wrapper's real subprocess call enforces argv form + timeout (§14)."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _write_manifests(wrapper.ARTIFACTS_ADG, snapshot=snap)

    captured: dict = {}

    def _fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return mock.Mock(returncode=0)

    # We call the internal helpers directly so we don't double-mock.
    with mock.patch("subprocess.run", side_effect=_fake_run):
        wrapper._run_report(
            snapshot=snap, fmt="json", require_runtime_proof=False, timeout_s=30
        )
    assert isinstance(captured["argv"], list)
    assert captured["argv"][0] == __import__("sys").executable
    assert captured["kwargs"].get("shell") is False
    assert captured["kwargs"].get("timeout") == 30


def test_no_hard_gate_failure_hidden_by_broad_exception(temp_artifacts, monkeypatch):
    """A failed required gate MUST surface in reasons; never silently discarded."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = [{
        "name": name, "phase": "post-ADG-subprocess", "kind": "subprocess",
        "blocking_mode": "hard_fail",
        "status": "fail" if name == "wiring" else "pass",
        "exit_code": 1 if name == "wiring" else 0,
        "duration_s": 0.1, "started_at_utc": "x", "finished_at_utc": "x",
        "script_rel": None, "message": "intentional",
    } for name in sorted(required_gate_names())]
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert any("wiring" in r and "fail" in r for r in result.reasons)


def test_diagnostic_mode_certification_status_is_diagnostic_only(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="diagnostic")
    assert result.certification_status == "diagnostic_only"


def test_require_runtime_proof_fails_when_not_attested(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=False, attested=0)
    _patch_generator(monkeypatch, snapshot=snap, runtime_proof_status="view_absent", runtime_attested=0)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)
    assert result.certification_status == "failed"
    assert any("runtime_proof_status" in r for r in result.reasons)


def test_wrapper_writes_receipt(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    wrapper.run_audit(mode="certification")
    assert wrapper.RECEIPT_PATH.is_file()
    payload = json.loads(wrapper.RECEIPT_PATH.read_text())
    assert "certification_status" in payload
    assert "runtime_proof_status" in payload


def test_certification_fails_when_dispatcher_block(temp_artifacts, monkeypatch):
    """DoD-3: plane-3 BLOCK fails certification via enforcement report."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=3)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_: [])

    disp_path = wrapper.ARTIFACTS_ADG / "adg_gate_results_test_block.json"
    disp_path.write_text(
        json.dumps(
            {
                "overall_exit_code": 1,
                "gates": [
                    {
                        "gate_id": "3_write_sovereignty",
                        "enforcement": "block",
                        "classification": "blocked",
                        "exit_code": 1,
                    }
                ],
                "total_gates": 1,
            }
        ),
        encoding="utf-8",
    )

    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)
    assert not result.ok
    assert result.certification_status == "failed"
    assert any("adg_gate_dispatcher" in r for r in result.reasons)


def test_clean_certification_run_returns_ok(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=3)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_: [])

    def _certified_report(**_kwargs):  # noqa: ANN003
        return {
            "certified_rollup": "CERTIFIED",
            "p0_failed": [],
            "planes": {"plane1": [], "plane2": [], "plane3": {}},
        }

    def _write_report(_report, ts=None):  # noqa: ANN001, ARG001
        out = wrapper.ARTIFACTS_ADG / "adg_enforcement_report_test.json"
        out.write_text(json.dumps(_report), encoding="utf-8")
        return out

    import tools.adg.integration.enforcement_report as enforcement_mod

    monkeypatch.setattr(enforcement_mod, "build_enforcement_report", _certified_report)
    monkeypatch.setattr(enforcement_mod, "write_enforcement_report", _write_report)

    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)
    assert result.ok
    assert result.certification_status == "clean"
    assert result.reasons == []


def test_certification_generator_enables_three_bucket_env(monkeypatch):
    """ADR-079: CI certification must opt into three-bucket without changing default regen."""
    monkeypatch.delenv("ADG_THREE_BUCKET", raising=False)
    captured: dict[str, object] = {}

    def _fake_run(cmd, **kwargs):  # noqa: ANN001
        captured["env"] = dict(kwargs.get("env") or {})
        proc = mock.Mock()
        proc.returncode = 124
        return proc

    monkeypatch.setattr(wrapper.subprocess, "run", _fake_run)
    wrapper._run_generator(extra_args=[], timeout_s=10, certification_mode=True)
    env = captured["env"]
    assert env.get("ADG_CERTIFICATION_MODE") == "1"
    assert env.get("ADG_THREE_BUCKET") == "1"
    assert env.get("ADG_THREE_BUCKET_SIGN") == "1"


def test_diagnostic_generator_does_not_force_three_bucket(monkeypatch):
    monkeypatch.delenv("ADG_THREE_BUCKET", raising=False)
    captured: dict[str, object] = {}

    def _fake_run(cmd, **kwargs):  # noqa: ANN001
        captured["env"] = dict(kwargs.get("env") or {})
        proc = mock.Mock()
        proc.returncode = 0
        return proc

    monkeypatch.setattr(wrapper.subprocess, "run", _fake_run)
    wrapper._run_generator(extra_args=[], timeout_s=10, certification_mode=False)
    env = captured["env"]
    assert "ADG_THREE_BUCKET" not in env or env.get("ADG_THREE_BUCKET") != "1"
