"""Tests for apps_shared.proof.proof_contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_shared.proof.proof_contracts import (
    PROOF_STATUS_FAIL,
    PROOF_STATUS_PASS,
    AppRunEvidencePacket,
    ContractRecord,
    GateVerdictRecord,
    SpanRecord,
    sha256_of,
    sha256_of_file,
    verify_packet_hash,
    write_packet,
    write_records,
)


def _make_packet(**overrides):
    base = dict(
        app_id="apps_test",
        scenario_id="t1",
        command="cmd",
        cwd="/cwd",
        process_id=1,
        python_executable="/p",
        git_commit_or_snapshot_ref="snap",
        adg_snapshot_ref="snap.sqlite",
        request_id="rq",
        session_id="sess",
        run_id="run",
        trace_root="trace",
        trace_id="trace",
    )
    base.update(overrides)
    return AppRunEvidencePacket(**base)


def test_sha256_of_is_deterministic():
    assert sha256_of({"a": 1, "b": 2}) == sha256_of({"b": 2, "a": 1})  # sorted keys


def test_sha256_of_file_matches_inline(tmp_path: Path):
    p = tmp_path / "f.bin"
    p.write_bytes(b"hello world")
    digest = sha256_of_file(p)
    assert digest == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_finalize_idempotent_under_clean_packet():
    pkt = _make_packet()
    h1 = pkt.finalize()
    h2 = pkt.finalize()
    assert h1 == h2 and pkt.packet_hash == h1


def test_packet_pass_only_after_clean():
    pkt = _make_packet()
    pkt.add_fail_reason("BAD", "x")
    assert pkt.proof_status == PROOF_STATUS_FAIL
    pkt.fail_reasons.clear()
    pkt.mark_pass_if_clean()
    assert pkt.proof_status == PROOF_STATUS_PASS


def test_write_and_verify_packet_roundtrip(tmp_path: Path):
    pkt = _make_packet()
    p = write_packet(pkt, tmp_path / "ev.json")
    ok, msg = verify_packet_hash(p)
    assert ok and msg == "ok"


def test_verify_packet_hash_detects_tamper(tmp_path: Path):
    pkt = _make_packet()
    p = write_packet(pkt, tmp_path / "ev.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    data["app_id"] = "MUTATED"  # tamper
    p.write_text(json.dumps(data, sort_keys=True, indent=2), encoding="utf-8")
    ok, msg = verify_packet_hash(p)
    assert not ok and "hash mismatch" in msg


def test_verify_packet_hash_missing_file(tmp_path: Path):
    ok, msg = verify_packet_hash(tmp_path / "does_not_exist.json")
    assert not ok and "missing" in msg


def test_verify_packet_hash_missing_field(tmp_path: Path):
    p = tmp_path / "ev.json"
    p.write_text(json.dumps({"app_id": "x"}), encoding="utf-8")
    ok, msg = verify_packet_hash(p)
    assert not ok and "no packet_hash" in msg


def test_write_records_returns_content_hash(tmp_path: Path):
    span = SpanRecord(
        trace_id="t",
        span_id="s",
        parent_span_id=None,
        layer="U0",
        name="x",
        started_at="t1",
        ended_at="t2",
        status="PASS",
    )
    h = write_records([span], tmp_path / "spans.json")
    assert len(h) == 64 and (tmp_path / "spans.json").exists()


def test_span_record_is_frozen():
    span = SpanRecord(
        trace_id="t",
        span_id="s",
        parent_span_id=None,
        layer="U0",
        name="x",
        started_at="t1",
        ended_at="t2",
        status="PASS",
    )
    with pytest.raises((AttributeError, TypeError)):
        span.span_id = "y"  # type: ignore[misc]


def test_gate_record_to_dict():
    g = GateVerdictRecord(
        gate_id="g1",
        verdict="ALLOW_FINISH",
        emitted_by_span_id="s1",
        reason_codes=("ok",),
        evidence_refs=("e",),
    )
    d = g.to_dict()
    assert d["gate_id"] == "g1" and d["verdict"] == "ALLOW_FINISH"


def test_contract_record_to_dict():
    c = ContractRecord(
        contract_kind="K",
        digest="d",
        emitted_by_span_id="s",
        payload_path="p.json",
    )
    d = c.to_dict()
    assert d["contract_kind"] == "K" and d["payload_path"] == "p.json"
