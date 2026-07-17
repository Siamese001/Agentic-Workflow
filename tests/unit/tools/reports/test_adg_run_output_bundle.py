"""Current-run sealing and terminal-render contracts for the ADG output bundle."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest

from tools.reports import (
    adg_action_queue,
    adg_bcg_adapter,
    adg_bcg_executive_synthesis,
    adg_burndown_report,
    adg_cleanup_queue_and_p2_blocker_trace,
    adg_dead_code_report,
    adg_review_template,
)
from tools.reports.adg_run_output_bundle import (
    emit_adg_run_output_bundle,
    print_adg_run_terminal_summary,
    validate_existing_adg_run_output_bundle,
)


RUN_ID = "20260717_120000"


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _current_run_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    artifacts = tmp_path / "artifacts" / "adg"
    sqlite_path = artifacts / f"adg_indexed_{RUN_ID}.sqlite"
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_path.write_bytes(b"current-run-snapshot")
    snapshot_sha256 = hashlib.sha256(sqlite_path.read_bytes()).hexdigest()
    gate_results = _write_json(
        artifacts / f"adg_gate_results_{RUN_ID}.json",
        {
            "timestamp": RUN_ID,
            "snapshot_path": str(sqlite_path),
            "snapshot_sha256": snapshot_sha256,
            "overall_exit_code": 0,
            "gates": [{"gate_id": "current_gate"}],
        },
    )
    burndown = _write_json(
        artifacts / f"adg_burndown_table_{RUN_ID}.json",
        {
            "summary": {"total": 0},
            "provenance": {
                "sqlite_source_path": str(sqlite_path),
                "sqlite_source_sha256": snapshot_sha256,
            },
        },
    )
    return artifacts, sqlite_path, gate_results, burndown


def _install_successful_producers(
    monkeypatch: pytest.MonkeyPatch,
    artifacts: Path,
) -> None:
    def _adapter(**_kwargs):
        print("adapter producer noise")
        path = _write_json(artifacts / f"adg_bcg_gate_adapter_{RUN_ID}.json", {"ok": True})
        path.with_suffix(".md").write_text("adapter", encoding="utf-8")
        return 0, path

    monkeypatch.setattr(adg_bcg_adapter, "emit_bcg_gate_adapter", _adapter)

    def _burndown(**kwargs):
        print("# ADG CI Burndown Report")
        for output_path in kwargs["output_paths"]:
            output_path.write_text("# ADG CI Burndown Report\n", encoding="utf-8")
        return 0

    monkeypatch.setattr(adg_burndown_report, "emit_mandatory_adg_burndown_report", _burndown)

    def _action(**_kwargs):
        path = _write_json(artifacts / f"adg_action_queue_{RUN_ID}.json", {"ok": True})
        return 0, path

    monkeypatch.setattr(adg_action_queue, "emit_adg_action_queue", _action)

    def _review(**_kwargs):
        path = _write_json(artifacts / f"adg_review_template_{RUN_ID}.json", {"ok": True})
        path.with_suffix(".yaml").write_text("ok: true\n", encoding="utf-8")
        return 0, path

    monkeypatch.setattr(adg_review_template, "emit_mandatory_adg_review_template", _review)

    def _dead_code(**_kwargs):
        path = _write_json(artifacts / f"dead_code_zone_control_report_{RUN_ID}.json", {"ok": True})
        return 0, path

    monkeypatch.setattr(adg_dead_code_report, "emit_mandatory_adg_dead_code_report", _dead_code)

    def _cleanup(**_kwargs):
        path = _write_json(
            artifacts / f"adg_cleanup_queue_and_p2_blocker_trace_{RUN_ID}.json",
            {"ok": True},
        )
        path.with_suffix(".md").write_text("cleanup", encoding="utf-8")
        return 0, path

    monkeypatch.setattr(
        adg_cleanup_queue_and_p2_blocker_trace,
        "emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace",
        _cleanup,
    )

    def _executive(**_kwargs):
        print("executive producer noise")
        path = _write_json(artifacts / f"adg_bcg_executive_summary_{RUN_ID}.json", {"ok": True})
        path.with_suffix(".yaml").write_text("ok: true\n", encoding="utf-8")
        path.with_suffix(".md").write_text(
            "## ADG Executive Brief\n\n"
            "### Impact Inventory\n\n"
            "No current-run defects.\n\n"
            "- **Decision gate:** PASS\n"
            "- **Fix now:** none\n",
            encoding="utf-8",
        )
        return 0, path

    monkeypatch.setattr(adg_bcg_executive_synthesis, "emit_bcg_executive_summary", _executive)


def _emit_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    artifacts, sqlite_path, gate_results, burndown = _current_run_inputs(tmp_path)
    _install_successful_producers(monkeypatch, artifacts)
    result = emit_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
        gate_results_path=gate_results,
        burndown_path=burndown,
        repo_root=tmp_path,
    )
    return result, artifacts, sqlite_path, gate_results


def test_success_seals_one_current_run_terminal_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result, artifacts, sqlite_path, _gate_results = _emit_success(tmp_path, monkeypatch)

    rendered = capsys.readouterr().out
    assert result.status == "complete"
    assert result.required_exit_code == 0
    assert rendered.count("## ADG Executive Brief") == 1
    assert rendered.count("## Final disposition") == 1
    assert "# ADG CI Burndown Report" not in rendered
    assert "producer noise" not in rendered
    assert validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
    ) == (True, "complete current-run bundle")


def test_required_rc_zero_without_artifact_blocks_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifacts, sqlite_path, gate_results, burndown = _current_run_inputs(tmp_path)
    _install_successful_producers(monkeypatch, artifacts)
    monkeypatch.setattr(adg_bcg_adapter, "emit_bcg_gate_adapter", lambda **_kwargs: (0, None))

    result = emit_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
        gate_results_path=gate_results,
        burndown_path=burndown,
        repo_root=tmp_path,
    )

    assert result.status == "blocked"
    assert result.required_exit_code == 2
    assert capsys.readouterr().out.count("## ADG Executive Brief") == 1


def test_import_failure_is_normalized_into_blocked_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifacts, sqlite_path, gate_results, burndown = _current_run_inputs(tmp_path)
    monkeypatch.delattr(adg_bcg_adapter, "emit_bcg_gate_adapter")

    result = emit_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
        gate_results_path=gate_results,
        burndown_path=burndown,
        print_terminal=False,
        repo_root=tmp_path,
    )

    payload = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert result.status == "blocked"
    assert all(gate["status"] == "blocked" for gate in payload["gates"])
    assert "output bundle producer crashed" in payload["gates"][0]["diagnostic"]


def test_validator_rejects_gate_results_changed_after_sealing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _result, artifacts, sqlite_path, gate_results = _emit_success(tmp_path, monkeypatch)
    gate_results.write_text("{}", encoding="utf-8")

    valid, reason = validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
    )
    assert not valid
    assert "gate results digest mismatch" in reason


def test_validator_rejects_required_gate_without_inventoried_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result, artifacts, sqlite_path, _gate_results = _emit_success(tmp_path, monkeypatch)
    payload = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    required_gate = next(gate for gate in payload["gates"] if gate["key"] == "bcg_gate_adapter")
    required_gate["paths"] = []
    result.manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    valid, reason = validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
    )
    assert not valid
    assert "has no artifact path" in reason


def test_suppressed_generator_finalization_is_valid_and_wrapper_replaces_disposition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifacts, sqlite_path, gate_results, burndown = _current_run_inputs(tmp_path)
    _install_successful_producers(monkeypatch, artifacts)
    result = emit_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
        gate_results_path=gate_results,
        burndown_path=burndown,
        print_terminal=False,
        repo_root=tmp_path,
    )

    print_adg_run_terminal_summary(
        result,
        final_exit_code=0,
        diagnostics=["generator complete"],
        print_terminal=False,
    )
    assert capsys.readouterr().out == ""
    assert validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
    )[0]

    print_adg_run_terminal_summary(
        result,
        final_exit_code=1,
        diagnostics=["wrapper certification failed"],
    )
    rendered = capsys.readouterr().out
    terminal = result.terminal_summary_path.read_text(encoding="utf-8")  # type: ignore[union-attr]
    assert rendered.count("## ADG Executive Brief") == 1
    assert rendered.count("## Final disposition") == 1
    assert terminal.count("## Final disposition") == 1
    assert "wrapper certification failed" in terminal
    assert "generator complete" not in terminal


def test_producer_system_exit_is_normalized_into_blocked_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifacts, sqlite_path, gate_results, burndown = _current_run_inputs(tmp_path)
    _install_successful_producers(monkeypatch, artifacts)

    def _exit(**_kwargs):
        raise SystemExit(9)

    monkeypatch.setattr(adg_bcg_adapter, "emit_bcg_gate_adapter", _exit)
    result = emit_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
        gate_results_path=gate_results,
        burndown_path=burndown,
        print_terminal=False,
        repo_root=tmp_path,
    )

    assert result.status == "blocked"
    gate = next(row for row in result.gates if row.key == "bcg_gate_adapter")
    assert gate.status == "fail"
    assert "SystemExit(9)" in gate.diagnostic


def test_missing_required_format_blocks_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifacts, sqlite_path, gate_results, burndown = _current_run_inputs(tmp_path)
    _install_successful_producers(monkeypatch, artifacts)

    def _review_without_yaml(**_kwargs):
        return 0, _write_json(
            artifacts / f"adg_review_template_{RUN_ID}.json",
            {"ok": True},
        )

    monkeypatch.setattr(
        adg_review_template,
        "emit_mandatory_adg_review_template",
        _review_without_yaml,
    )
    result = emit_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
        gate_results_path=gate_results,
        burndown_path=burndown,
        print_terminal=False,
        repo_root=tmp_path,
    )

    assert result.status == "blocked"
    review_gate = next(row for row in result.gates if row.key == "review_template")
    assert review_gate.status == "fail"
    assert "required format missing" in review_gate.diagnostic
    assert not (artifacts / f"adg_output_publication_{RUN_ID}.json").exists()


def test_terminal_diagnostics_are_single_line_and_cannot_inject_headers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result, _artifacts, _sqlite_path, _gate_results = _emit_success(tmp_path, monkeypatch)

    print_adg_run_terminal_summary(
        result,
        final_exit_code=1,
        diagnostics=["line one\n## ADG Executive Brief\n## Final disposition"],
        print_terminal=False,
    )
    terminal = result.terminal_summary_path.read_text(encoding="utf-8")  # type: ignore[union-attr]

    assert terminal.count("## ADG Executive Brief") == 1
    assert terminal.count("## Final disposition") == 1
    diagnostic = next(line for line in terminal.splitlines() if "**Diagnostic:**" in line)
    assert "line one ADG Executive Brief Final disposition" in diagnostic


def test_validator_rejects_extra_gate_fields_and_bundle_publishes_no_report_aliases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result, artifacts, sqlite_path, _gate_results = _emit_success(tmp_path, monkeypatch)
    assert not (artifacts / "adg_bcg_adapter_latest.json").exists()
    assert not (artifacts / "adg_bcg_executive_summary_latest.json").exists()
    payload = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    payload["gates"][0]["unexpected"] = True
    result.manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    valid, reason = validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=artifacts,
        run_id=RUN_ID,
        sqlite_path=sqlite_path,
    )
    assert not valid
    assert "gate row invalid" in reason
