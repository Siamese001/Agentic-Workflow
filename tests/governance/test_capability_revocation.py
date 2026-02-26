"""
Tests for CapabilityRevoker token revocation management.

Phase 3.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.enforcement.capability_revoker import (
    CapabilityRevoker,
    TokenRevocationError,
    VersionInvalidError,
    get_capability_revoker,
    reset_capability_revoker_for_testing,
)
from agentic_core.L2_execution.enforcement.key_derivation import get_key_version


@pytest.fixture(autouse=True)
def reset_revoker():
    reset_capability_revoker_for_testing()
    yield
    reset_capability_revoker_for_testing()


class TestCapabilityRevokerRevocation:
    def test_revoke_token_marks_as_revoked(self) -> None:
        r = CapabilityRevoker()
        r.revoke_token("trace-001")
        assert r.is_token_revoked("trace-001") is True

    def test_unrevoked_token_not_revoked(self) -> None:
        r = CapabilityRevoker()
        assert r.is_token_revoked("trace-999") is False

    def test_validate_raises_on_revoked(self) -> None:
        r = CapabilityRevoker()
        r.revoke_token("trace-abc")
        with pytest.raises(TokenRevocationError, match="trace-abc"):
            r.validate_token("trace-abc", get_key_version())

    def test_validate_passes_valid_token(self) -> None:
        r = CapabilityRevoker()
        r.validate_token("trace-ok", get_key_version())

    def test_revoked_count(self) -> None:
        r = CapabilityRevoker()
        r.revoke_token("t1")
        r.revoke_token("t2")
        assert r.revoked_count() == 2


class TestCapabilityRevokerVersionValidation:
    def test_current_version_valid(self) -> None:
        r = CapabilityRevoker()
        assert r.is_version_valid(get_key_version()) is True

    def test_wrong_version_invalid(self) -> None:
        r = CapabilityRevoker()
        assert r.is_version_valid("99") is False

    def test_invalidate_version_blocks_token(self) -> None:
        r = CapabilityRevoker()
        current = get_key_version()
        r.invalidate_version(current)
        with pytest.raises(VersionInvalidError):
            r.validate_token("any-trace", current)

    def test_invalid_version_count(self) -> None:
        r = CapabilityRevoker()
        r.invalidate_version("v-old")
        assert r.invalid_version_count() == 1

    def test_validate_raises_on_wrong_version(self) -> None:
        r = CapabilityRevoker()
        with pytest.raises(VersionInvalidError):
            r.validate_token("trace-x", "wrong-version")


class TestGetCapabilityRevokerSingleton:
    def test_returns_same_instance(self) -> None:
        a = get_capability_revoker()
        b = get_capability_revoker()
        assert a is b

    def test_reset_creates_fresh_instance(self) -> None:
        a = get_capability_revoker()
        reset_capability_revoker_for_testing()
        b = get_capability_revoker()
        assert a is not b
