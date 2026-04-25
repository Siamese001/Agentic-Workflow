"""Idempotency nonce + cache prefix discipline tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning.idempotency_nonce import (
    IdempotencyEnvelope,
    cache_prefix_hash,
    compute_nonce,
    detect_prefix_drift,
    make_envelope,
)


class TestComputeNonce:
    def test_same_inputs_yield_same_nonce(self):
        a = compute_nonce("trace-1", attempt=0)
        b = compute_nonce("trace-1", attempt=0)
        assert a == b

    def test_different_attempts_yield_different_nonces(self):
        a = compute_nonce("trace-1", attempt=0)
        b = compute_nonce("trace-1", attempt=1)
        assert a != b

    def test_different_traces_yield_different_nonces(self):
        a = compute_nonce("trace-1", attempt=0)
        b = compute_nonce("trace-2", attempt=0)
        assert a != b

    def test_nonce_is_32_hex_chars(self):
        result = compute_nonce("trace-1")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_empty_trace_id_raises(self):
        with pytest.raises(ValueError, match="trace_id is required"):
            compute_nonce("")

    def test_negative_attempt_raises(self):
        with pytest.raises(ValueError, match="attempt must be >= 0"):
            compute_nonce("trace-1", attempt=-1)


class TestCachePrefixHash:
    def test_only_s0_d0_i0_affect_hash(self):
        slots_a = {"S0": "id", "D0": "rule", "I0": "instr", "C0": "ctx-a", "U0": "u-a"}
        slots_b = {"S0": "id", "D0": "rule", "I0": "instr", "C0": "ctx-b", "U0": "u-b"}
        assert cache_prefix_hash(slots_a) == cache_prefix_hash(slots_b)

    def test_s0_change_changes_hash(self):
        a = cache_prefix_hash({"S0": "id-a", "D0": "", "I0": ""})
        b = cache_prefix_hash({"S0": "id-b", "D0": "", "I0": ""})
        assert a != b

    def test_d0_change_changes_hash(self):
        a = cache_prefix_hash({"S0": "x", "D0": "rule-a", "I0": ""})
        b = cache_prefix_hash({"S0": "x", "D0": "rule-b", "I0": ""})
        assert a != b

    def test_i0_change_changes_hash(self):
        a = cache_prefix_hash({"S0": "x", "D0": "y", "I0": "i-a"})
        b = cache_prefix_hash({"S0": "x", "D0": "y", "I0": "i-b"})
        assert a != b

    def test_missing_slots_treated_as_empty(self):
        a = cache_prefix_hash({"S0": "x"})
        b = cache_prefix_hash({"S0": "x", "D0": "", "I0": ""})
        assert a == b

    def test_line_endings_normalized(self):
        a = cache_prefix_hash({"S0": "line1\nline2", "D0": "", "I0": ""})
        b = cache_prefix_hash({"S0": "line1\r\nline2", "D0": "", "I0": ""})
        c = cache_prefix_hash({"S0": "line1\rline2", "D0": "", "I0": ""})
        assert a == b == c

    def test_hash_is_16_hex_chars(self):
        result = cache_prefix_hash({"S0": "x"})
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)


class TestEnvelope:
    def test_make_envelope_combines_fields(self):
        env = make_envelope("trace-1", {"S0": "x"}, attempt=2)
        assert isinstance(env, IdempotencyEnvelope)
        assert env.trace_id == "trace-1"
        assert env.attempt == 2
        assert env.nonce == compute_nonce("trace-1", attempt=2)
        assert env.cache_prefix_hash == cache_prefix_hash({"S0": "x"})
        assert env.scheme_version == "v1"

    def test_envelope_is_frozen(self):
        env = make_envelope("trace-1", {"S0": "x"})
        with pytest.raises((AttributeError, TypeError)):
            env.attempt = 99  # type: ignore[misc]


class TestDriftDetection:
    def test_no_drift_when_prefix_unchanged(self):
        slots = {"S0": "x", "D0": "y", "I0": "z"}
        h = cache_prefix_hash(slots)
        assert not detect_prefix_drift(h, slots)

    def test_drift_when_s0_changes(self):
        slots_before = {"S0": "x", "D0": "y", "I0": "z"}
        h = cache_prefix_hash(slots_before)
        slots_after = {**slots_before, "S0": "x-modified"}
        assert detect_prefix_drift(h, slots_after)

    def test_no_drift_when_only_user_slot_changes(self):
        slots_before = {"S0": "x", "D0": "y", "I0": "z", "U0": "first question"}
        h = cache_prefix_hash(slots_before)
        slots_after = {**slots_before, "U0": "different question"}
        assert not detect_prefix_drift(h, slots_after)
