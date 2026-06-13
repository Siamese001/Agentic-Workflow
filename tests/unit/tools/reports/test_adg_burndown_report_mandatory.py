"""Mandatory ADG burndown markdown emit."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.reports.adg_burndown_report import (
    BURNDOWN_REPORT_OUTPUTS,
    emit_mandatory_adg_burndown_report,
    render,
)
from tools.reports.gate_signal_catalog import (
    display_verdict,
    display_verdict_sub,
    needs_fix,
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
    text = out_a.read_text(encoding="utf-8")
    assert "## 1. ADG Status By Band" in text
    assert "## 2. ADG CI Gates" in text
    assert text.index("## 1. ADG Status By Band") < text.index("## 2. ADG CI Gates")


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


def test_render_track_inventory_vs_ratchet_floor(tmp_path: Path) -> None:
    """848 inventory vs 2792 floor — same TRACK verdict, different Sub."""
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    gate.write_text(
        json.dumps(
            {
                "overall_exit_code": 0,
                "timestamp": "2026-05-25T00:00:00Z",
                "summary": {"block_pass": 1},
                "gates": [
                    {
                        "gate_id": "3_write_sovereignty",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "pass",
                        "status": "warn",
                        "violation_count": 848,
                        "owner": "adg_gates",
                        "exit_code": 0,
                    },
                    {
                        "gate_id": "G_REACH_l0_reachability",
                        "band": "P0",
                        "enforcement": "ratchet",
                        "classification": "pass",
                        "violation_count": 2792,
                        "baseline_count": 2792,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    burndown.write_text(
        json.dumps({"schema_version": "2.2", "p0_clean": True, "summary": {}}),
        encoding="utf-8",
    )
    md = render(gate, burndown)
    assert "| TRACK | inventory | 848 |" in md
    assert "| TRACK | floor | 2792 |" in md
    assert "| FIX |" not in md.split("3_write_sovereignty")[1][:80]


def test_render_fix_cluster_for_blocked_gate(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    gate.write_text(
        json.dumps(
            {
                "overall_exit_code": 1,
                "timestamp": "2026-05-25T00:00:00Z",
                "summary": {},
                "gates": [
                    {
                        "gate_id": "10_infra_wiring",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "blocked",
                        "violation_count": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    burndown.write_text(json.dumps({"schema_version": "2.2", "summary": {}}), encoding="utf-8")
    md = render(gate, burndown)
    assert "| FIX | block | 2 |" in md
    assert "### Fix now" in md


def test_verdict_three_clusters_mece() -> None:
    cases: list[tuple[dict, str, str]] = [
        ({"classification": "blocked", "violation_count": 1, "enforcement": "block"}, "FIX", "block"),
        ({"classification": "regressed", "violation_count": 10, "enforcement": "ratchet", "baseline_count": 5}, "FIX", "regr"),
        ({"classification": "seed_missing", "violation_count": 0, "enforcement": "ratchet"}, "FIX", "seed"),
        ({"classification": "pass", "violation_count": 0, "enforcement": "block"}, "CLEAR", "—"),
        ({"classification": "pass", "violation_count": 3, "enforcement": "warn"}, "TRACK", "advis"),
        (
            {"classification": "pass", "violation_count": 2792, "enforcement": "ratchet", "baseline_count": 2792},
            "TRACK",
            "floor",
        ),
        (
            {
                "classification": "pass",
                "violation_count": 848,
                "enforcement": "block",
                "status": "warn",
                "owner": "adg_gates",
                "exit_code": 0,
            },
            "TRACK",
            "inventory",
        ),
    ]
    clusters = {display_verdict(g) for g, c, _s in cases}
    assert clusters == {"FIX", "TRACK", "CLEAR"}
    for g, cluster, sub in cases:
        assert display_verdict(g) == cluster
        assert display_verdict_sub(g) == sub
    assert needs_fix({"classification": "blocked", "violation_count": 1, "enforcement": "block"})


def test_render_includes_cluster_glossary(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    gate.write_text(
        json.dumps(
            {"overall_exit_code": 0, "timestamp": "2026-05-25T00:00:00Z", "summary": {}, "gates": []}
        ),
        encoding="utf-8",
    )
    burndown.write_text(json.dumps({"schema_version": "2.2", "summary": {}}), encoding="utf-8")
    md = render(gate, burndown)
    assert "## Verdict glossary" in md
    assert "**FIX**" in md and "**TRACK**" in md
    assert "| Verdict | You need to… | Sub (detail) |" in md
    assert "## 2. ADG CI Gates" in md


def test_render_orders_p0_p3_then_adg_ci_then_severity_inventory(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    gate.write_text(
        json.dumps(
            {
                "overall_exit_code": 0,
                "timestamp": "2026-05-25T00:00:00Z",
                "summary": {},
                "gates": [
                    {
                        "gate_id": "G_REACH_l0_reachability",
                        "band": "P0",
                        "enforcement": "ratchet",
                        "classification": "pass",
                        "violation_count": 2792,
                        "baseline_count": 2792,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    burndown.write_text(json.dumps({"schema_version": "2.2", "summary": {}}), encoding="utf-8")

    md = render(gate, burndown)

    assert "Backlog rows are summed gate `violation_count`; guardian gross/net math is only in Severity Inventory." in md
    assert "| Band | Status | Fix now | Tracked backlog | Read it as | Next move |" in md
    assert "| P0 | PASS | 0 | 1 gate / 2,792 rows | green; tracked backlog | work ranked queue; do not treat as new failures |" in md
    assert "Allowed Floor" in md
    assert "| Gate ID | CI Band | Enforcement | Action | Sub | Rows | Allowed Floor | Signal | Next Best Action |" in md
    assert "| `G_REACH_l0_reachability` | P0 | ratchet | TRACK | floor | 2792 | 2792 |" in md
    assert md.index("## 1. ADG Status By Band") < md.index("## 2. ADG CI Gates")
    assert md.index("## 2. ADG CI Gates") < md.index("## 3. Severity Inventory Burndown")


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
