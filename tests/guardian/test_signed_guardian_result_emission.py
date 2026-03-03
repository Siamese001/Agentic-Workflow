"""
Wave 1.5 Gate Test: Guardian results are signed when V15 is enforced.

Verifies that maybe_sign_result() produces a SignedGuardianArtifact when
V15_ENFORCEMENT=1, and passes through unsigned when V15_ENFORCEMENT=0.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    V15EnforcementError,
    maybe_sign_result,
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Ensure V15 env vars are clean before each test."""
    monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
    monkeypatch.delenv("V15_TEST_SIGNING", raising=False)


class TestSignedGuardianResultEmission:
    """§7 — Guardian results must be signed when V15 is enforced."""

    def test_enforced_with_test_signing_produces_signed_result(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        monkeypatch.setenv("V15_TEST_SIGNING", "1")

        result = GuardianResult(guardian_id="test_guardian")
        result.add_check(check_id="dummy", status="PASS", details="ok")

        signed = maybe_sign_result(result, commit_hash="abc123")

        assert signed is result, "maybe_sign_result should return the same object"
        assert signed.v15_signature, "signature must be non-empty when enforced"
        assert signed.v15_trace_id, "trace_id must be set when enforced"
        assert signed.v15_commit_hash == "abc123"

    def test_enforced_signed_result_passes_ensure_v15_signed(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        monkeypatch.setenv("V15_TEST_SIGNING", "1")

        result = GuardianResult(guardian_id="test_guardian")
        maybe_sign_result(result, commit_hash="abc123")

        # ensure_v15_signed() must not raise
        result.ensure_v15_signed()

    def test_enforced_signed_result_serializes_without_error(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        monkeypatch.setenv("V15_TEST_SIGNING", "1")

        result = GuardianResult(guardian_id="test_guardian")
        maybe_sign_result(result, commit_hash="abc123")

        # to_json() calls ensure_v15_signed() internally — must not raise
        json_str = result.to_json()
        assert '"v15_signature"' in json_str

    def test_not_enforced_returns_unsigned(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "0")

        result = GuardianResult(guardian_id="test_guardian")
        returned = maybe_sign_result(result, commit_hash="abc123")

        assert returned is result
        assert not result.v15_signature, "signature must be empty when not enforced"

    def test_not_enforced_serializes_without_error(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "0")

        result = GuardianResult(guardian_id="test_guardian")
        # to_json() must not raise when enforcement is off
        json_str = result.to_json()
        assert '"guardian_id"' in json_str

    def test_enforced_without_test_signing_raises(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        # V15_TEST_SIGNING not set — no enclave available

        result = GuardianResult(guardian_id="test_guardian")
        with pytest.raises(V15EnforcementError, match="signing enclave"):
            maybe_sign_result(result, commit_hash="abc123")

    def test_sign_preserves_trace_id_if_already_set(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        monkeypatch.setenv("V15_TEST_SIGNING", "1")

        result = GuardianResult(guardian_id="test_guardian")
        result.v15_trace_id = "pre-set-trace-id"
        maybe_sign_result(result, commit_hash="abc123")

        assert result.v15_trace_id == "pre-set-trace-id"
