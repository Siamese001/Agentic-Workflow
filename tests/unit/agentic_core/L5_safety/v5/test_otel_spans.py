"""Tests for `otel_spans.py` (G2 — v5 governance plane span instrumentation)."""

from __future__ import annotations

from agentic_core.L5_safety.v5 import certify_packet
from agentic_core.L5_safety.v5.otel_spans import (
    ALL_SPAN_NAMES,
    SPAN_CERTIFY_PACKET,
    SPAN_DECISION_RAIL_EMIT,
    SPAN_G0_VALIDATE,
    SPAN_G1_TRIAGE,
    SPAN_G2A_ORIGIN_TRUST,
    SPAN_REPLAY_AUDIT_SEAL,
    _clear_recorded_spans,
    emit_event,
    emit_span,
    get_recorded_spans,
)


def test_span_catalog_has_13_names() -> None:
    assert len(ALL_SPAN_NAMES) == 13
    # Every name follows the l5.governance.* convention
    for name in ALL_SPAN_NAMES:
        assert name.startswith("l5.governance."), f"{name!r} does not match prefix"


def test_emit_event_records_span() -> None:
    _clear_recorded_spans()
    emit_event(SPAN_CERTIFY_PACKET, {"actor": "test"})
    spans = get_recorded_spans()
    assert len(spans) == 1
    assert spans[0].name == SPAN_CERTIFY_PACKET
    assert spans[0].attributes["actor"] == "test"


def test_emit_span_records_then_yields() -> None:
    _clear_recorded_spans()
    with emit_span(SPAN_G0_VALIDATE, {"x": 1}):
        pass
    spans = get_recorded_spans()
    assert spans[0].name == SPAN_G0_VALIDATE
    assert spans[0].attributes["x"] == 1


def test_certify_packet_emits_lifecycle_spans() -> None:
    """End-to-end: a successful certify_packet call emits the lifecycle spans."""

    _clear_recorded_spans()
    raw = {
        "request_id": "req",
        "trace_id": "trc",
        "run_id": "run",
        "tenant_id": "ten",
        "caller_id": "cal",
        "packet_kind": "request_envelope",
        "side_effect_class": "READ",
        "origin_trust_manifest_raw": {"system_policy": ["policy.rule"]},
        "policy_hash": "ph",
        "blueprint_hash": "bh",
        "registry_digest_set": ("d1",),
        "principal_chain_id": "pri",
    }
    certify_packet(raw_packet=raw)
    span_names = {s.name for s in get_recorded_spans()}
    # The minimal happy path emits these spans (replay_audit may run twice
    # — once provisional, once final — and that's fine for the test).
    assert SPAN_CERTIFY_PACKET in span_names
    assert SPAN_G0_VALIDATE in span_names
    assert SPAN_G1_TRIAGE in span_names
    assert SPAN_G2A_ORIGIN_TRUST in span_names
    assert SPAN_REPLAY_AUDIT_SEAL in span_names
    assert SPAN_DECISION_RAIL_EMIT in span_names


def test_recorded_spans_returns_immutable_tuple() -> None:
    _clear_recorded_spans()
    emit_event("l5.governance.g0_validate")
    spans = get_recorded_spans()
    assert isinstance(spans, tuple)
