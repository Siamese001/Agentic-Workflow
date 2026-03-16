"""
Unit tests for PolicyHashEnforcer (Gap 2 — policy hash at L0 routing entry).
"""

from __future__ import annotations

import hashlib
import json

import pytest

from agentic_core.L0_routing.enforcement.policy_hash_enforcer import (
    PolicyHashEnforcer,
    PolicyHashViolation,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_policy_hash_enforcer")
_emit_applies_guardrail("p0", "test_policy_hash_enforcer", "p0_governance")
_emit_snapshots_state("p0", "test_policy_hash_enforcer", "state_snapshot")
emit_replay_key("p0", "test_policy_hash_enforcer")
emit_determinism_digest("p0", "test_policy_hash_enforcer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_root(config: dict) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(canonical).hexdigest().lower()


class _FakePacket:
    def __init__(self, instruction_id: str = "test-id", policy_hash: str = "") -> None:
        self.instruction_id = instruction_id
        self.policy_hash = policy_hash


_POLICY_CONFIG = {"version": "1.0", "rules": ["deny_all_writes"]}
_ROOT = _make_root(_POLICY_CONFIG)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construction_rejects_empty_root() -> None:
    with pytest.raises(ValueError, match="non-empty active_merkle_root"):
        PolicyHashEnforcer("")


def test_construction_rejects_whitespace_root() -> None:
    with pytest.raises(ValueError, match="non-empty active_merkle_root"):
        PolicyHashEnforcer("   ")


def test_construction_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unknown mode"):
        PolicyHashEnforcer(_ROOT, mode="SOFT_FAIL")


def test_construction_stores_lowercased_root() -> None:
    enforcer = PolicyHashEnforcer(_ROOT.upper())
    assert enforcer.active_merkle_root == _ROOT.lower()


# ---------------------------------------------------------------------------
# validate() — non-raising path
# ---------------------------------------------------------------------------


def test_validate_pass_when_hash_matches() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash=_ROOT)
    result = enforcer.validate(packet)
    assert result.passed is True
    assert result.policy_hash_present is True
    assert result.policy_hash_matches is True


def test_validate_fail_when_hash_absent() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash="")
    result = enforcer.validate(packet)
    assert result.passed is False
    assert result.policy_hash_present is False
    assert "absent" in result.reason


def test_validate_fail_when_hash_wrong() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    wrong_root = "a" * 64
    packet = _FakePacket(policy_hash=wrong_root)
    result = enforcer.validate(packet)
    assert result.passed is False
    assert result.policy_hash_present is True
    assert result.policy_hash_matches is False
    assert "mismatch" in result.reason


def test_validate_accepts_uppercase_packet_hash() -> None:
    """policy_hash comparison must be case-insensitive."""
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash=_ROOT.upper())
    result = enforcer.validate(packet)
    assert result.passed is True


def test_validate_result_format_contains_status() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(instruction_id="pkt-1", policy_hash=_ROOT)
    result = enforcer.validate(packet)
    fmt = result.format()
    assert "PASS" in fmt
    assert "pkt-1" in fmt


def test_validate_missing_attribute_treated_as_empty() -> None:
    """Objects without policy_hash attribute are treated as empty."""
    enforcer = PolicyHashEnforcer(_ROOT)

    class _Bare:
        instruction_id = "bare"

    result = enforcer.validate(_Bare())
    assert result.passed is False
    assert result.policy_hash_present is False


# ---------------------------------------------------------------------------
# enforce() — raising path
# ---------------------------------------------------------------------------


def test_enforce_passes_when_hash_matches() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash=_ROOT)
    enforcer.enforce(packet)  # must not raise


def test_enforce_raises_on_missing_hash() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash="")
    with pytest.raises(PolicyHashViolation, match="absent"):
        enforcer.enforce(packet)


def test_enforce_raises_on_wrong_hash() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash="b" * 64)
    with pytest.raises(PolicyHashViolation, match="mismatch"):
        enforcer.enforce(packet)


def test_enforce_violation_carries_packet_id() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(instruction_id="my-packet", policy_hash="")
    exc = None
    try:
        enforcer.enforce(packet)
    except PolicyHashViolation as e:
        exc = e
    assert exc is not None
    assert exc.packet_id == "my-packet"


def test_enforce_log_only_does_not_raise() -> None:
    enforcer = PolicyHashEnforcer(_ROOT, mode="LOG_ONLY")
    packet = _FakePacket(policy_hash="")
    enforcer.enforce(packet)  # must not raise even with missing hash


# ---------------------------------------------------------------------------
# derive_root()
# ---------------------------------------------------------------------------


def test_derive_root_is_deterministic() -> None:
    config = {"a": 1, "b": [2, 3]}
    root1 = PolicyHashEnforcer.derive_root(config)
    root2 = PolicyHashEnforcer.derive_root(config)
    assert root1 == root2


def test_derive_root_matches_manual_sha256() -> None:
    config = {"version": "2", "rules": []}
    expected = _make_root(config)
    assert PolicyHashEnforcer.derive_root(config) == expected


def test_derive_root_is_key_order_independent() -> None:
    """derive_root uses sort_keys — dict key order must not matter."""
    config_a = {"b": 2, "a": 1}
    config_b = {"a": 1, "b": 2}
    assert PolicyHashEnforcer.derive_root(config_a) == PolicyHashEnforcer.derive_root(config_b)


def test_enforcer_works_with_derived_root() -> None:
    config = {"policy_version": "3", "deny_writes": True}
    root = PolicyHashEnforcer.derive_root(config)
    enforcer = PolicyHashEnforcer(root)
    packet = _FakePacket(policy_hash=root)
    enforcer.enforce(packet)  # must not raise
