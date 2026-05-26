"""Regression tests for compact ADG burndown canvas payload (no Cursor UI required)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.reports.adg_burndown_canvas import (
    _canvas_bypassed,
    _tsx_source,
    build_canvas_payload,
)


def _write_gate_results(path: Path, *, exit_code: int = 1) -> None:
    path.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-26T10:00:00+00:00",
                "overall_exit_code": exit_code,
                "total_gates": 2,
                "summary": {
                    "block_pass": 0,
                    "block_fail": 1,
                    "ratchet_pass": 1,
                    "ratchet_regressed": 0,
                    "warn": 0,
                },
                "gates": [
                    {
                        "gate_id": "10_infra_wiring",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "blocked",
                        "violation_count": 3,
                        "gate_class": "InfraWiringGate",
                    },
                    {
                        "gate_id": "1_critical_path_integrity",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "pass",
                        "violation_count": 0,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_burndown(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "2.2",
                "p0_clean": False,
                "summary": {
                    "P0": {"label": "Critical", "gross": 3, "guardian": 0, "net": 3, "diff": 1},
                    "P1": {"label": "High", "gross": 0, "guardian": 0, "net": 0, "diff": 0},
                    "P2": {"label": "Medium", "gross": 0, "guardian": 0, "net": 0, "diff": 0},
                    "P3": {"label": "Low", "gross": 0, "guardian": 0, "net": 0, "diff": 0},
                },
            }
        ),
        encoding="utf-8",
    )


def test_build_canvas_payload_lists_only_fix_blockers(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    _write_gate_results(gate, exit_code=1)
    _write_burndown(burndown)

    payload = build_canvas_payload(gate, burndown)

    assert payload["overall_pass"] is False
    assert payload["p0_clean"] is False
    assert len(payload["bands"]) == 4
    assert payload["bands"][0][0] == "P0"
    assert len(payload["blockers"]) == 1
    assert payload["blockers"][0][0] == "10_infra_wiring"
    assert payload["blockers"][0][3] == 3
    assert payload["markdown_rel"] == "artifacts/adg/adg_burndown_report.md"


def test_tsx_source_embeds_json_without_newlines_in_data_const() -> None:
    payload = {
        "generated": "2026-05-26T10:00:00+00:00",
        "snapshot": "2026-05-26T09:00:00+00:00",
        "source": "artifacts/adg/gates.json",
        "overall_pass": True,
        "total_gates": 1,
        "summary": [1, 0, 1, 0, 0],
        "p0_clean": True,
        "bands": [["P0", "Critical", 0, 0, 0, 0]],
        "blockers": [],
        "markdown_rel": "artifacts/adg/adg_burndown_report.md",
    }
    tsx = _tsx_source(payload)
    assert "const DATA = " in tsx
    assert "AdgCiBurndownCanvas" in tsx
    assert '"overall_pass":true' in tsx.replace(" ", "")


def test_canvas_bypass_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADG_BURNDOWN_CANVAS_BYPASS", "1")
    assert _canvas_bypassed() is True
