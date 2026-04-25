"""Tests for G0 entry packet validation (spec lines 21–49)."""

from __future__ import annotations

from agentic_core.L5_safety.v5 import (
    PacketKind,
    ReasonCode,
    SideEffectClass,
    validate_entry_packet,
)


def _good_packet() -> dict:
    return {
        "request_id": "req-1",
        "trace_id": "tr-1",
        "run_id": "run-1",
        "tenant_id": "tnt-1",
        "caller_id": "user-1",
        "packet_kind": "request_envelope",
        "side_effect_class": "READ",
        "principal_chain_id": "pc-1",
    }


def test_accepts_minimal_valid_packet():
    res = validate_entry_packet(_good_packet())
    assert res.accepted is True
    assert res.request is not None
    assert res.request.packet_kind == PacketKind.REQUEST_ENVELOPE
    assert res.request.side_effect_class == SideEffectClass.READ


def test_missing_required_field_rejects():
    bad = _good_packet()
    bad["request_id"] = ""
    res = validate_entry_packet(bad)
    assert res.accepted is False
    assert any(f.code == ReasonCode.MISSING_AUTHORITY for f in res.failures)


def test_unknown_packet_kind_rejects():
    bad = _good_packet()
    bad["packet_kind"] = "totally_made_up"
    res = validate_entry_packet(bad)
    assert res.accepted is False


def test_authority_without_route_hmac_rejects():
    bad = _good_packet()
    bad["requested_authority"] = ("tool:write_db",)
    bad["side_effect_class"] = "TOOL_CALL"
    bad["registry_digest_set"] = ("agent_reg:sha256:1",)
    # missing route_contract_hmac
    res = validate_entry_packet(bad)
    assert res.accepted is False
    assert any(f.code == ReasonCode.ROUTE_MISMATCH for f in res.failures)


def test_tool_call_without_registry_digest_rejects():
    bad = _good_packet()
    bad["side_effect_class"] = "TOOL_CALL"
    res = validate_entry_packet(bad)
    assert res.accepted is False
    assert any(f.code == ReasonCode.REGISTRY_MISMATCH for f in res.failures)


def test_read_only_claim_with_write_intent_rejects():
    bad = _good_packet()
    bad["side_effect_class"] = "WRITE_PROPOSAL"
    bad["registry_digest_set"] = ("d1",)
    res = validate_entry_packet(bad, declared_read_only=True)
    assert res.accepted is False
    assert any(f.code == ReasonCode.POLICY_VIOLATION for f in res.failures)


def test_origin_manifest_required_for_model_call():
    bad = _good_packet()
    bad["side_effect_class"] = "MODEL_CALL"
    bad["registry_digest_set"] = ("d1",)
    res = validate_entry_packet(bad)
    assert res.accepted is False
    assert any(f.code == ReasonCode.INJECTION_DETECTED for f in res.failures)


def test_to_dict_is_deterministic():
    res = validate_entry_packet(_good_packet())
    assert res.request is not None
    d1 = res.request.to_dict()
    d2 = res.request.to_dict()
    assert d1 == d2
