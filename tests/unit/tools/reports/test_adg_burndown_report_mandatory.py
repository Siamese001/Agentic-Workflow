"""Mandatory ADG burndown markdown emit."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.reports.adg_burndown_report import (
    BURNDOWN_REPORT_OUTPUTS,
    emit_mandatory_adg_burndown_report,
)


def test_emit_mandatory_writes_all_outputs(tmp_path: Path, monkeypatch) -> None:
    gate = tmp_path / "adg_gate_results_test.json"
    burndown = tmp_path / "adg_burndown_table.json"
    gate.write_text(
        json.dumps(
            {
                "overall_exit_code": 0,
                "summary": {
                    "block_pass": 1,
                    "block_fail": 0,
                    "ratchet_pass": 1,
                    "ratchet_regressed": 0,
                    "warn": 0,
                },
                "gates": [
                    {
                        "gate_id": "1_critical_path_integrity",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "pass",
                        "violation_count": 0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    burndown.write_text(
        json.dumps(
            {
                "schema_version": "2.2",
                "bands": {
                    "P0": {"gross": 0, "net": 0, "diff": 0, "guardian": 0},
                },
            }
        ),
        encoding="utf-8",
    )
    out_a = tmp_path / "a.md"
    out_b = tmp_path / "b.md"
    monkeypatch.setattr(
        "tools.reports.adg_burndown_report.BURNDOWN_REPORT_OUTPUTS",
        (out_a, out_b),
    )
    assert (
        emit_mandatory_adg_burndown_report(
            gate_results=gate, burndown=burndown, fail_closed=True, print_inline=False
        )
        == 0
    )
    assert out_a.is_file() and out_b.is_file()
    assert "Burndown by Severity Band" in out_a.read_text(encoding="utf-8")


def test_emit_prints_markdown_to_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    gate = tmp_path / "adg_gate_results_test.json"
    burndown = tmp_path / "adg_burndown_table.json"
    gate.write_text(
        json.dumps(
            {
                "overall_exit_code": 0,
                "summary": {"block_pass": 1, "block_fail": 0, "ratchet_pass": 0, "warn": 0},
                "gates": [],
            }
        ),
        encoding="utf-8",
    )
    burndown.write_text(json.dumps({"schema_version": "2.2", "bands": {}}), encoding="utf-8")
    monkeypatch.setattr("tools.reports.adg_burndown_report.BURNDOWN_REPORT_OUTPUTS", ())
    monkeypatch.delenv("ADG_BURNDOWN_INLINE_BYPASS", raising=False)
    assert emit_mandatory_adg_burndown_report(gate_results=gate, burndown=burndown) == 0
    captured = capsys.readouterr()
    assert "# ADG CI Burndown Report" in captured.out


def test_emit_fail_closed_when_gate_results_missing(tmp_path: Path) -> None:
    burndown = tmp_path / "adg_burndown_table.json"
    burndown.write_text("{}", encoding="utf-8")
    assert (
        emit_mandatory_adg_burndown_report(
            gate_results=tmp_path / "missing.json",
            burndown=burndown,
            fail_closed=True,
        )
        == 2
    )
