"""Regression tests for ADG burndown gate signal catalog (verdict MECE + copy SSOT)."""

from __future__ import annotations

from tools.reports.gate_signal_catalog import (
    GATE_WHAT,
    display_verdict,
    display_verdict_sub,
    format_gate_signal,
    has_backlog_findings,
    needs_fix,
    render_verdict_legend_markdown,
    verdict_rule,
    verdict_sort_key,
    what_counts,
)


def test_gate_what_covers_canonical_p0_gates() -> None:
    for gate_id in (
        "1_critical_path_integrity",
        "3_write_sovereignty",
        "10_infra_wiring",
        "G_REACH_l0_reachability",
    ):
        assert gate_id in GATE_WHAT
        assert what_counts(gate_id) == GATE_WHAT[gate_id]


def test_what_counts_derives_from_gate_class_when_unknown_id() -> None:
    text = what_counts("unknown_gate_xyz", "InfraWiringGate")
    assert "Infra" in text or "infra" in text.lower()
    assert "auto-derived" in text


def test_verdict_rule_regression_messages() -> None:
    assert "blocked" in verdict_rule(
        {"classification": "blocked", "violation_count": 2, "enforcement": "block"}
    ).lower()
    assert "baseline" in verdict_rule(
        {
            "classification": "regressed",
            "violation_count": 12,
            "enforcement": "ratchet",
            "baseline_count": 10,
        }
    )
    assert "advisory" in verdict_rule(
        {"classification": "pass", "violation_count": 5, "enforcement": "warn"}
    ).lower()


def test_format_gate_signal_includes_counts_and_sub() -> None:
    gate = {
        "gate_id": "3_write_sovereignty",
        "gate_class": "WriteSovereigntyGate",
        "classification": "pass",
        "violation_count": 848,
        "enforcement": "block",
        "status": "warn",
        "owner": "adg_gates",
        "exit_code": 0,
    }
    signal = format_gate_signal(gate)
    assert signal.startswith("Counts:")
    assert "Sub:" in signal
    assert GATE_WHAT["3_write_sovereignty"] in signal


def test_verdict_sort_key_orders_fix_before_track_before_clear() -> None:
    fix = {"classification": "blocked", "violation_count": 1, "enforcement": "block"}
    track = {
        "classification": "pass",
        "violation_count": 100,
        "enforcement": "ratchet",
        "baseline_count": 100,
    }
    clear = {"classification": "pass", "violation_count": 0, "enforcement": "block"}
    assert verdict_sort_key(fix) < verdict_sort_key(track) < verdict_sort_key(clear)


def test_has_backlog_findings_and_needs_fix_are_mutually_exclusive_for_pass() -> None:
    clear_gate = {"classification": "pass", "violation_count": 0, "enforcement": "block"}
    assert display_verdict(clear_gate) == "CLEAR"
    assert not needs_fix(clear_gate)
    assert not has_backlog_findings(clear_gate)

    track_gate = {
        "classification": "pass",
        "violation_count": 848,
        "enforcement": "block",
        "status": "warn",
        "owner": "adg_gates",
        "exit_code": 0,
    }
    assert display_verdict(track_gate) == "TRACK"
    assert display_verdict_sub(track_gate) == "inventory"
    assert has_backlog_findings(track_gate)
    assert not needs_fix(track_gate)


def test_render_verdict_legend_markdown_includes_floor_vs_inventory_note() -> None:
    md = render_verdict_legend_markdown()
    assert "## Verdict glossary" in md
    assert "floor vs inventory" in md
    assert "| **FIX** |" in md
