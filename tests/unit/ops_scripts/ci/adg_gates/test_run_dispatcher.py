"""Fail-closed and machine-output contracts for the ADG gate dispatcher."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops_scripts.ci import _adg_wiring_gate_base
from ops_scripts.ci.adg_gates import run


@pytest.mark.parametrize(
    "row",
    [
        {"enforcement": "block", "violation_count": -1, "exit_code": -1, "status": "error"},
        {"enforcement": "block", "violation_count": 0, "exit_code": None, "status": "pass"},
        {"enforcement": "block", "violation_count": "0", "exit_code": 0, "status": "pass"},
        {"enforcement": "invalid", "violation_count": 0, "exit_code": 0, "status": "pass"},
        {"enforcement": "warn", "violation_count": 0, "exit_code": 0, "status": "unknown"},
        {"enforcement": "block", "violation_count": 0, "exit_code": 0, "status": "fail"},
        {"enforcement": "block", "violation_count": 0, "exit_code": 1, "status": "pass"},
    ],
)
def test_classify_normalizes_invalid_evidence_to_error(row: dict[str, object]) -> None:
    assert run._classify(row) == "error"


def _isolate_dispatcher(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Path:
    sink_dir = tmp_path / "governance"
    gate_spec = run.CANONICAL_GATES[0]
    monkeypatch.setattr(run, "CANONICAL_GATES", [gate_spec])
    monkeypatch.setattr(run, "WIRING_GATES", [])
    monkeypatch.setattr(
        run,
        "_run_gate",
        lambda _spec, snapshot=None: {
            "gate_id": gate_spec.gate_id,
            "band": gate_spec.band.value,
            "enforcement": gate_spec.enforcement.value,
            "source": gate_spec.source.value,
            "owner": "adg_gates",
            "handler": gate_spec.handler,
            "gate_class": gate_spec.gate_class,
            "dispatch": "in-process",
            "exit_code": 0,
            "violation_count": 0,
            "status": "pass",
            "stderr_tail": [],
        },
    )
    monkeypatch.setattr(run, "SINK_DIR", sink_dir)
    monkeypatch.setattr(run, "SINK_FILE", sink_dir / "dispatcher.jsonl")
    return tmp_path / "results"


def test_json_only_emits_only_current_result_path_and_skips_reports(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = _isolate_dispatcher(monkeypatch, tmp_path)
    snapshot = tmp_path / "current.sqlite"
    snapshot.write_bytes(b"snapshot")
    monkeypatch.setattr(_adg_wiring_gate_base, "latest_snapshot", lambda: snapshot)

    import tools.reports.adg_burndown_report as burndown_report

    monkeypatch.setattr(
        burndown_report,
        "emit_mandatory_adg_burndown_report",
        lambda **_kwargs: pytest.fail("json-only dispatcher must not materialize reports"),
    )

    rc = run.main(["--json-only", "--markers", "--output-dir", str(output_dir)])

    stdout_lines = [line for line in capsys.readouterr().out.splitlines() if line]
    assert rc == 0
    assert len(stdout_lines) == 1
    result_path = Path(stdout_lines[0])
    assert result_path.is_file()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["snapshot_path"] == str(snapshot)
    assert payload["snapshot_sha256"]
    assert payload["overall_exit_code"] == 0
    assert not list(output_dir.glob(".*.tmp"))


def test_missing_snapshot_cannot_produce_green_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = _isolate_dispatcher(monkeypatch, tmp_path)

    def _missing_snapshot() -> Path:
        raise FileNotFoundError("no current snapshot")

    monkeypatch.setattr(_adg_wiring_gate_base, "latest_snapshot", _missing_snapshot)

    rc = run.main(["--json-only", "--output-dir", str(output_dir)])

    result_path = Path(capsys.readouterr().out.strip())
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert rc == 1
    assert payload["snapshot_path"] is None
    assert payload["overall_exit_code"] == 1


def test_empty_fleet_registry_cannot_produce_green_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_dir = _isolate_dispatcher(monkeypatch, tmp_path)
    snapshot = tmp_path / "current.sqlite"
    snapshot.write_bytes(b"snapshot")
    monkeypatch.setattr(_adg_wiring_gate_base, "latest_snapshot", lambda: snapshot)
    monkeypatch.setattr(run, "CANONICAL_GATES", [])

    rc = run.main(["--json-only", "--output-dir", str(output_dir)])

    payload = json.loads(Path(capsys.readouterr().out.strip()).read_text(encoding="utf-8"))
    assert rc == 1
    assert payload["fleet_registry_valid"] is False
