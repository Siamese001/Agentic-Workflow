"""Behavioral tests for ``agentic_core.L0_routing.enforcement.policy_hash_enforcer``.

Covers L0 routing InstructionPacket policy hash enforcement (Gap 2):
- PolicyHashViolation inherits from RuntimeError, carries packet_id + policy_id.
- PolicyHashEnforcer construction validates non-empty active_merkle_root and mode.
- validate(): missing/empty hash → fail reason "absent"; mismatch → "mismatch"; match → pass.
- HMAC-safe compare (constant-time) used for match.
- Active root normalised (stripped + lowercased).
- enforce() in HARD_FAIL mode raises; in LOG_ONLY mode does not raise.
- derive_root() produces canonical SHA-256 over sorted-key JSON.
- format() produces a human-readable PASS/FAIL summary.
"""

from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

import pytest

from agentic_core.L0_routing.enforcement.policy_hash_enforcer import (
    PolicyHashEnforcer,
    PolicyHashValidationResult,
    PolicyHashViolation,
)


_ACTIVE = "abc123" * 8  # 48 hex chars


# ---- PolicyHashViolation ------------------------------------------------

class TestPolicyHashViolation:
    def test_is_runtime_error(self) -> None:
        assert issubclass(PolicyHashViolation, RuntimeError)

    def test_fields(self) -> None:
        exc = PolicyHashViolation("boom", packet_id="pkt-1")
        assert exc.reason == "boom"
        assert exc.packet_id == "pkt-1"
        assert exc.policy_id == "L0-POL-HASH-001"
        assert "pkt-1" in str(exc)
        assert "boom" in str(exc)


# ---- Construction / validation ------------------------------------------

class TestConstruction:
    def test_valid(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE)
        assert e.active_merkle_root == _ACTIVE.lower()

    def test_empty_root_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            PolicyHashEnforcer(active_merkle_root="")

    def test_whitespace_root_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            PolicyHashEnforcer(active_merkle_root="   ")

    def test_root_normalised_strip_lower(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root="  ABCDEF  ")
        assert e.active_merkle_root == "abcdef"

    def test_invalid_mode_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unknown mode"):
            PolicyHashEnforcer(active_merkle_root=_ACTIVE, mode="ASSERT")

    @pytest.mark.parametrize("mode", ["HARD_FAIL", "LOG_ONLY"])
    def test_valid_modes(self, mode: str) -> None:
        PolicyHashEnforcer(active_merkle_root=_ACTIVE, mode=mode)


# ---- validate() ---------------------------------------------------------

def _packet(policy_hash: str = _ACTIVE, instruction_id: str = "pkt-1") -> object:
    return SimpleNamespace(
        instruction_id=instruction_id,
        policy_hash=policy_hash,
    )


class TestValidate:
    def test_match_passes(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE)
        r = e.validate(_packet(_ACTIVE))
        assert r.passed is True
        assert r.policy_hash_present is True
        assert r.policy_hash_matches is True
        assert r.reason == ""

    def test_case_insensitive_match(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE.upper())
        r = e.validate(_packet(_ACTIVE.lower()))
        assert r.passed is True

    def test_missing_hash_fails(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE)
        r = e.validate(_packet(""))
        assert r.passed is False
        assert r.policy_hash_present is False
        assert r.policy_hash_matches is False
        assert "absent" in r.reason

    def test_none_hash_fails(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE)
        r = e.validate(SimpleNamespace(instruction_id="p", policy_hash=None))
        assert r.passed is False
        assert r.policy_hash_present is False

    def test_missing_attr_treated_as_empty(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE)
        r = e.validate(object())  # no instruction_id, no policy_hash
        assert r.passed is False
        assert r.packet_id == ""

    def test_mismatch_fails(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE)
        r = e.validate(_packet("deadbeef" * 8))
        assert r.passed is False
        assert r.policy_hash_present is True
        assert r.policy_hash_matches is False
        assert "mismatch" in r.reason

    def test_packet_id_captured(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE)
        r = e.validate(_packet(_ACTIVE, instruction_id="INSTR-42"))
        assert r.packet_id == "INSTR-42"


# ---- enforce() ----------------------------------------------------------

class TestEnforce:
    def test_hard_fail_raises_on_missing(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE, mode="HARD_FAIL")
        with pytest.raises(PolicyHashViolation, match="absent") as info:
            e.enforce(_packet(""))
        assert info.value.packet_id == "pkt-1"

    def test_hard_fail_raises_on_mismatch(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE, mode="HARD_FAIL")
        with pytest.raises(PolicyHashViolation, match="mismatch"):
            e.enforce(_packet("deadbeef" * 8))

    def test_hard_fail_ok_on_match(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE, mode="HARD_FAIL")
        e.enforce(_packet(_ACTIVE))  # no raise

    def test_log_only_never_raises(self) -> None:
        e = PolicyHashEnforcer(active_merkle_root=_ACTIVE, mode="LOG_ONLY")
        e.enforce(_packet(""))  # no raise
        e.enforce(_packet("deadbeef" * 8))  # no raise
        e.enforce(_packet(_ACTIVE))  # no raise


# ---- derive_root --------------------------------------------------------

class TestDeriveRoot:
    def test_sha256_of_canonical_json(self) -> None:
        config = {"b": 2, "a": 1}
        expected = hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            .encode("utf-8"),
        ).hexdigest().lower()
        assert PolicyHashEnforcer.derive_root(config) == expected

    def test_determinism_key_order_invariant(self) -> None:
        r1 = PolicyHashEnforcer.derive_root({"a": 1, "b": 2})
        r2 = PolicyHashEnforcer.derive_root({"b": 2, "a": 1})
        assert r1 == r2

    def test_different_configs_different_roots(self) -> None:
        r1 = PolicyHashEnforcer.derive_root({"a": 1})
        r2 = PolicyHashEnforcer.derive_root({"a": 2})
        assert r1 != r2

    def test_is_hex_lowercase(self) -> None:
        r = PolicyHashEnforcer.derive_root({"x": "y"})
        assert len(r) == 64
        assert r == r.lower()
        int(r, 16)  # parses as hex


# ---- format -------------------------------------------------------------

class TestResultFormat:
    def test_pass_format(self) -> None:
        r = PolicyHashValidationResult(
            passed=True, packet_id="P1",
            policy_hash_present=True, policy_hash_matches=True,
            active_root="root-hash-long-value", packet_hash="root-hash-long-value",
        )
        s = r.format()
        assert "PASS" in s
        assert "P1" in s
        assert "L0-POL-HASH-001" in s

    def test_fail_format(self) -> None:
        r = PolicyHashValidationResult(
            passed=False, packet_id="P2",
            policy_hash_present=False, policy_hash_matches=False,
            active_root="a" * 64, packet_hash="",
            reason="missing",
        )
        s = r.format()
        assert "FAIL" in s
        assert "missing" in s
