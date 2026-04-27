"""Tests for apps_shared.proof.validators — trace tree + inventory + strip."""

from __future__ import annotations

import json
from pathlib import Path

from apps_shared.proof.validators import (
    _strip_volatile,
    validate_artifact_inventory,
    validate_trace_tree,
)
from apps_shared.proof.proof_contracts import AppRunEvidencePacket, write_packet


def _write_trace(p: Path, spans: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spans), encoding="utf-8")


def test_validate_trace_tree_pass(tmp_path: Path):
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": None, "layer": "U0", "trace_id": "T"},
            {"span_id": "s2", "parent_span_id": "s1", "layer": "L1", "trace_id": "T"},
        ],
    )
    v = validate_trace_tree(p)
    assert v.ok


def test_validate_trace_tree_missing_root(tmp_path: Path):
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": "x", "layer": "U0", "trace_id": "T"},
        ],
    )
    v = validate_trace_tree(p)
    assert not v.ok and any("root" in r for r in v.fail_reasons)


def test_validate_trace_tree_two_roots(tmp_path: Path):
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": None, "layer": "U0", "trace_id": "T"},
            {"span_id": "s2", "parent_span_id": None, "layer": "L1", "trace_id": "T"},
        ],
    )
    v = validate_trace_tree(p)
    assert not v.ok


def test_validate_trace_tree_orphan(tmp_path: Path):
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": None, "layer": "U0", "trace_id": "T"},
            {"span_id": "s2", "parent_span_id": "MISSING", "layer": "L1", "trace_id": "T"},
        ],
    )
    v = validate_trace_tree(p)
    assert not v.ok and any("missing parent" in r for r in v.fail_reasons)


def test_validate_trace_tree_inconsistent_trace_id(tmp_path: Path):
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": None, "layer": "U0", "trace_id": "T"},
            {"span_id": "s2", "parent_span_id": "s1", "layer": "L1", "trace_id": "OTHER"},
        ],
    )
    v = validate_trace_tree(p)
    assert not v.ok


def test_validate_trace_tree_layer_order_violation(tmp_path: Path):
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": None, "layer": "L0", "trace_id": "T"},
            {"span_id": "s2", "parent_span_id": "s1", "layer": "U0", "trace_id": "T"},
        ],
    )
    v = validate_trace_tree(p)
    assert not v.ok


def test_validate_trace_tree_missing_file(tmp_path: Path):
    v = validate_trace_tree(tmp_path / "no.json")
    assert not v.ok and any("missing" in r for r in v.fail_reasons)


def test_validate_trace_tree_empty_list(tmp_path: Path):
    p = tmp_path / "t.json"
    p.write_text("[]", encoding="utf-8")
    v = validate_trace_tree(p)
    assert not v.ok


def test_strip_volatile_drops_timestamps_and_receipts():
    payload = {
        "stable_field": "x",
        "received_at_iso": "2026-01-01",
        "ingress_time_unix": 12345,
        "transport_receipt_ref": "tep:abc",
        "ingress_replay_seed_ref": "seed:xyz",
        "nested": {"received_at_iso": "drop_me", "kept": True},
    }
    out = _strip_volatile(payload)
    assert out == {"stable_field": "x", "nested": {"kept": True}}


def test_strip_volatile_handles_lists():
    payload = [{"received_at_iso": "x", "k": 1}, {"k": 2}]
    out = _strip_volatile(payload)
    assert out == [{"k": 1}, {"k": 2}]


def test_validate_artifact_inventory_passes(tmp_path: Path):
    # Create real files for the inventory entries
    (tmp_path / "traces").mkdir()
    span_path = tmp_path / "traces" / "apps_test_trace.json"
    span_path.write_text("[]", encoding="utf-8")

    pkt = AppRunEvidencePacket(
        app_id="apps_test",
        scenario_id="s1",
        command="c",
        cwd="/",
        process_id=1,
        python_executable="/p",
        git_commit_or_snapshot_ref="x",
        adg_snapshot_ref="x",
        request_id="rq",
        session_id="ss",
        run_id="rn",
        trace_root="t",
        trace_id="t",
        span_inventory=["traces/apps_test_trace.json"],
    )
    write_packet(pkt, tmp_path / "contracts" / "apps_test" / "s1" / "evidence_packet.json")
    v = validate_artifact_inventory(packet=pkt, export_root=tmp_path)
    assert v.ok


def test_validate_artifact_inventory_catches_missing(tmp_path: Path):
    pkt = AppRunEvidencePacket(
        app_id="apps_test",
        scenario_id="s1",
        command="c",
        cwd="/",
        process_id=1,
        python_executable="/p",
        git_commit_or_snapshot_ref="x",
        adg_snapshot_ref="x",
        request_id="rq",
        session_id="ss",
        run_id="rn",
        trace_root="t",
        trace_id="t",
        span_inventory=["traces/missing.json"],
    )
    write_packet(pkt, tmp_path / "contracts" / "apps_test" / "s1" / "evidence_packet.json")
    v = validate_artifact_inventory(packet=pkt, export_root=tmp_path)
    assert not v.ok
