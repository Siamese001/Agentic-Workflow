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


def test_validate_trace_tree_all_none_trace_id_fails(tmp_path: Path):
    """BUG #2 REGRESSION: a trace where every span has trace_id=None
    previously passed because {None} has len=1. Must now fail explicitly."""
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": None, "layer": "U0", "trace_id": None},
            {"span_id": "s2", "parent_span_id": "s1", "layer": "L1", "trace_id": None},
        ],
    )
    v = validate_trace_tree(p)
    assert not v.ok
    assert any("trace_id" in r and "None" in r for r in v.fail_reasons)


def test_validate_trace_tree_mixed_none_and_real_trace_id_fails(tmp_path: Path):
    """BUG #2 REGRESSION: mixed None + real trace_id must fail."""
    p = tmp_path / "t.json"
    _write_trace(
        p,
        [
            {"span_id": "s1", "parent_span_id": None, "layer": "U0", "trace_id": "T1"},
            {"span_id": "s2", "parent_span_id": "s1", "layer": "L1", "trace_id": None},
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


def test_validate_artifact_inventory_uses_trusted_path_when_provided(tmp_path: Path):
    """BUG #1 REGRESSION: when a trusted packet_path is provided, the
    validator MUST hash-check against it even if the loaded packet's
    app_id has been mutated to a non-existent value."""
    # Write a real packet at a known path
    real_pkt = AppRunEvidencePacket(
        app_id="apps_real", scenario_id="s1", command="c", cwd="/", process_id=1,
        python_executable="/p", git_commit_or_snapshot_ref="x", adg_snapshot_ref="x",
        request_id="rq", session_id="ss", run_id="rn", trace_root="t", trace_id="t",
    )
    real_path = tmp_path / "contracts" / "apps_real" / "s1" / "evidence_packet.json"
    write_packet(real_pkt, real_path)

    # Now construct a "tampered" packet with a different app_id but reuse
    # the trusted path. The hash check MUST pass because the file at the
    # trusted path is unmodified.
    tampered = AppRunEvidencePacket(
        app_id="MUTATED_APP_ID", scenario_id="s1",
        command="c", cwd="/", process_id=1,
        python_executable="/p", git_commit_or_snapshot_ref="x", adg_snapshot_ref="x",
        request_id="rq", session_id="ss", run_id="rn", trace_root="t", trace_id="t",
    )
    v = validate_artifact_inventory(
        packet=tampered, export_root=tmp_path, packet_path=real_path,
    )
    # The hash check on the real (untampered) file passes
    assert v.details.get("packet_hash_ok") is True


def test_validate_artifact_inventory_legacy_path_falls_back(tmp_path: Path):
    """BUG #1 REGRESSION: when packet_path is omitted, the validator falls
    back to deriving from packet fields and signals 'trusted_path_unset'
    in any failure reason."""
    pkt = AppRunEvidencePacket(
        app_id="MUTATED", scenario_id="s1", command="c", cwd="/", process_id=1,
        python_executable="/p", git_commit_or_snapshot_ref="x", adg_snapshot_ref="x",
        request_id="rq", session_id="ss", run_id="rn", trace_root="t", trace_id="t",
        # Note: no packet at the MUTATED path
    )
    v = validate_artifact_inventory(packet=pkt, export_root=tmp_path)
    # MUTATED path doesn't exist — fail surfaces the path source
    assert not v.ok
    assert any("trusted_path_unset" in r for r in v.fail_reasons)
