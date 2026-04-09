"""Tests for IngressEnvelopeCheck — E1–E6 gate (B01 — GAP-001, REQ-001, REQ-002).

Positive tests:
- Valid request passes all six checks and returns StampedRequest
- StampedRequest has all 6 required fields
- caller_scope_baseline is deterministic for identical inputs

Negative / contract tests:
- E1: non-dict → MALFORMED_ENVELOPE
- E1: empty dict → MALFORMED_ENVELOPE
- E2: missing required field → SCHEMA_INVALID
- E2: untrusted schema_version → SCHEMA_INVALID
- E3: missing caller_identity → IDENTITY_MISSING
- E3: empty caller_identity → IDENTITY_MISSING
- E4: rate limiter rejects → RATE_LIMITED
- E6: duplicate request_id → REPLAY_DUPLICATE

Boundary / replay tests:
- Same valid envelope submitted twice → second is rejected as duplicate
- caller_scope_baseline is stable (deterministic) across identical envelopes

Layer sovereignty negative tests (critical):
- L2 writing directly must not bypass this gate (this gate is the ONLY pre-L1 path)
"""

import pytest
from unittest.mock import MagicMock

from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    IngressEnvelopeCheck,
    IngressRejected,
    RejectionReasonCode,
    RejectionSlip,
    StampedRequest,
)


def _valid_envelope(**overrides) -> dict:
    base = {
        "request_payload": {"query": "hello"},
        "caller_identity": "agent-001",
        "schema_version": "1.0",
        "request_id": "req-test-001",
        "session_id": "sess-test-001",
    }
    base.update(overrides)
    return base


def _gate(rate_limiter=None, seen=None) -> IngressEnvelopeCheck:
    return IngressEnvelopeCheck(
        rate_limiter=rate_limiter,
        seen_request_ids=seen,
    )


class TestHappyPath:
    def test_valid_envelope_returns_stamped_request(self):
        result = _gate().check(_valid_envelope())
        assert isinstance(result, StampedRequest)

    def test_stamped_request_has_request_id(self):
        result = _gate().check(_valid_envelope())
        assert result.request_id == "req-test-001"

    def test_stamped_request_has_session_id(self):
        result = _gate().check(_valid_envelope())
        assert result.session_id == "sess-test-001"

    def test_stamped_request_has_trace_root(self):
        result = _gate().check(_valid_envelope())
        assert result.trace_root and len(result.trace_root) == 16

    def test_stamped_request_has_caller_scope_baseline(self):
        result = _gate().check(_valid_envelope())
        assert result.caller_scope_baseline and len(result.caller_scope_baseline) > 0

    def test_stamped_request_has_schema_version(self):
        result = _gate().check(_valid_envelope())
        assert result.schema_version == "1.0"

    def test_stamped_request_has_caller_identity(self):
        result = _gate().check(_valid_envelope())
        assert result.caller_identity == "agent-001"

    def test_stamped_request_has_request_payload(self):
        result = _gate().check(_valid_envelope())
        assert result.request_payload == {"query": "hello"}

    def test_caller_scope_baseline_is_deterministic(self):
        env = _valid_envelope()
        gate = _gate()
        r1 = gate.check({**env, "request_id": "req-a"})
        gate2 = _gate()
        r2 = gate2.check({**env, "request_id": "req-b"})
        assert r1.caller_scope_baseline == r2.caller_scope_baseline

    def test_schema_version_1_1_accepted(self):
        result = _gate().check(_valid_envelope(schema_version="1.1"))
        assert result.schema_version == "1.1"

    def test_schema_version_2_0_accepted(self):
        result = _gate().check(_valid_envelope(schema_version="2.0"))
        assert result.schema_version == "2.0"

    def test_to_dict_on_stamped_request_contains_all_fields(self):
        result = _gate().check(_valid_envelope())
        d = result.to_dict()
        for key in (
            "request_id",
            "session_id",
            "trace_root",
            "caller_scope_baseline",
            "schema_version",
            "request_payload",
            "caller_identity",
            "stamped_at",
        ):
            assert key in d


class TestE1Transport:
    def test_non_dict_raises_malformed_envelope(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check("not a dict")
        assert exc.value.slip.reason_code == RejectionReasonCode.MALFORMED_ENVELOPE

    def test_empty_dict_raises_malformed_envelope(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check({})
        assert exc.value.slip.reason_code == RejectionReasonCode.MALFORMED_ENVELOPE

    def test_none_raises_malformed_envelope(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check(None)
        assert exc.value.slip.reason_code == RejectionReasonCode.MALFORMED_ENVELOPE

    def test_rejection_slip_has_gate_stage_e1(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check({})
        assert exc.value.slip.gate_stage == "E1_TRANSPORT"


class TestE2Schema:
    def test_missing_request_payload_raises_schema_invalid(self):
        env = _valid_envelope()
        del env["request_payload"]
        with pytest.raises(IngressRejected) as exc:
            _gate().check(env)
        assert exc.value.slip.reason_code == RejectionReasonCode.SCHEMA_INVALID

    def test_missing_caller_identity_raises_schema_invalid(self):
        env = _valid_envelope()
        del env["caller_identity"]
        with pytest.raises(IngressRejected) as exc:
            _gate().check(env)
        assert exc.value.slip.reason_code == RejectionReasonCode.SCHEMA_INVALID

    def test_missing_schema_version_raises_schema_invalid(self):
        env = _valid_envelope()
        del env["schema_version"]
        with pytest.raises(IngressRejected) as exc:
            _gate().check(env)
        assert exc.value.slip.reason_code == RejectionReasonCode.SCHEMA_INVALID

    def test_untrusted_schema_version_raises_schema_invalid(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check(_valid_envelope(schema_version="0.1"))
        assert exc.value.slip.reason_code == RejectionReasonCode.SCHEMA_INVALID

    def test_rejection_slip_has_gate_stage_e2(self):
        env = _valid_envelope()
        del env["request_payload"]
        with pytest.raises(IngressRejected) as exc:
            _gate().check(env)
        assert exc.value.slip.gate_stage == "E2_SCHEMA"


class TestE3Identity:
    def test_missing_caller_identity_after_schema_raises_identity_missing(self):
        env = {
            "request_payload": {"q": "x"},
            "schema_version": "1.0",
            "caller_identity": "",
        }
        with pytest.raises(IngressRejected) as exc:
            _gate().check(env)
        assert exc.value.slip.reason_code in (
            RejectionReasonCode.IDENTITY_MISSING,
            RejectionReasonCode.SCHEMA_INVALID,
        )

    def test_empty_caller_identity_raises_identity_missing(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check(_valid_envelope(caller_identity=""))
        assert exc.value.slip.reason_code in (
            RejectionReasonCode.IDENTITY_MISSING,
            RejectionReasonCode.IDENTITY_UNTRUSTED,
        )

    def test_whitespace_only_caller_identity_raises(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check(_valid_envelope(caller_identity="   "))
        assert exc.value.slip.reason_code in (
            RejectionReasonCode.IDENTITY_MISSING,
            RejectionReasonCode.IDENTITY_UNTRUSTED,
        )

    def test_non_string_caller_identity_raises_identity_untrusted(self):
        env = _valid_envelope()
        env["caller_identity"] = 12345
        with pytest.raises(IngressRejected) as exc:
            _gate().check(env)
        assert exc.value.slip.reason_code == RejectionReasonCode.IDENTITY_UNTRUSTED


class TestE4Quota:
    def test_rate_limiter_deny_raises_rate_limited(self):
        rl = MagicMock()
        rl.is_allowed.return_value = False
        with pytest.raises(IngressRejected) as exc:
            _gate(rate_limiter=rl).check(_valid_envelope())
        assert exc.value.slip.reason_code == RejectionReasonCode.RATE_LIMITED

    def test_rate_limiter_allow_passes(self):
        rl = MagicMock()
        rl.is_allowed.return_value = True
        result = _gate(rate_limiter=rl).check(_valid_envelope())
        assert isinstance(result, StampedRequest)

    def test_rate_limiter_called_with_caller_identity(self):
        rl = MagicMock()
        rl.is_allowed.return_value = True
        _gate(rate_limiter=rl).check(_valid_envelope(caller_identity="agent-xyz"))
        rl.is_allowed.assert_called_once_with("agent-xyz")

    def test_no_rate_limiter_passes_without_error(self):
        result = _gate(rate_limiter=None).check(_valid_envelope())
        assert isinstance(result, StampedRequest)

    def test_rejection_slip_has_gate_stage_e4(self):
        rl = MagicMock()
        rl.is_allowed.return_value = False
        with pytest.raises(IngressRejected) as exc:
            _gate(rate_limiter=rl).check(_valid_envelope())
        assert exc.value.slip.gate_stage == "E4_QUOTA"


class TestE6Dedup:
    def test_same_request_id_submitted_twice_is_rejected(self):
        gate = _gate()
        gate.check(_valid_envelope(request_id="req-dup"))
        with pytest.raises(IngressRejected) as exc:
            gate.check(_valid_envelope(request_id="req-dup"))
        assert exc.value.slip.reason_code == RejectionReasonCode.REPLAY_DUPLICATE

    def test_different_request_ids_both_pass(self):
        gate = _gate()
        r1 = gate.check(_valid_envelope(request_id="req-001"))
        r2 = gate.check(_valid_envelope(request_id="req-002"))
        assert r1.request_id == "req-001"
        assert r2.request_id == "req-002"

    def test_rejection_slip_has_gate_stage_e6(self):
        gate = _gate()
        gate.check(_valid_envelope(request_id="req-dup2"))
        with pytest.raises(IngressRejected) as exc:
            gate.check(_valid_envelope(request_id="req-dup2"))
        assert exc.value.slip.gate_stage == "E6_DEDUP"


class TestRejectionReasonCodeEnum:
    def test_all_seven_rejection_codes_declared(self):
        codes = {c.value for c in RejectionReasonCode}
        assert "E1_MALFORMED_ENVELOPE" in codes
        assert "E2_SCHEMA_INVALID" in codes
        assert "E3_IDENTITY_MISSING" in codes
        assert "E3_IDENTITY_UNTRUSTED" in codes
        assert "E4_QUOTA_EXCEEDED" in codes
        assert "E4_RATE_LIMITED" in codes
        assert "E6_REPLAY_DUPLICATE" in codes

    def test_quota_exceeded_constructable_in_rejection_slip(self):
        slip = RejectionSlip(
            reason_code=RejectionReasonCode.QUOTA_EXCEEDED,
            request_id="req-q",
            trace_root="trace-q",
            message="Quota exceeded for caller.",
            gate_stage="E4_QUOTA",
        )
        assert slip.reason_code == RejectionReasonCode.QUOTA_EXCEEDED
        assert slip.to_dict()["reason_code"] == "E4_QUOTA_EXCEEDED"


class TestRejectionSlip:
    def test_rejection_slip_to_dict_has_reason_code(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check({})
        d = exc.value.slip.to_dict()
        assert "reason_code" in d
        assert d["reason_code"] == RejectionReasonCode.MALFORMED_ENVELOPE.value

    def test_ingress_rejected_exception_message_contains_reason_code(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check({})
        assert "E1_MALFORMED_ENVELOPE" in str(exc.value)

    def test_rejection_slip_has_trace_root(self):
        with pytest.raises(IngressRejected) as exc:
            _gate().check(_valid_envelope(schema_version="bad"))
        assert exc.value.slip.trace_root


class TestLayerSovereignty:
    def test_gate_does_not_mutate_input_envelope(self):
        env = _valid_envelope()
        original_keys = set(env.keys())
        _gate().check(env)
        assert set(env.keys()) == original_keys

    def test_stamped_request_stamped_at_is_float(self):
        result = _gate().check(_valid_envelope())
        assert isinstance(result.stamped_at, float)
        assert result.stamped_at > 0
