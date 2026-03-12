"""ADG-driven tests for L2_execution/enforcement/capability_revoker.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.capability_revoker import (
    CapabilityRevoker,
    TokenRevocationError,
    VersionInvalidError,
)


class TestTokenRevocationError:
    def test_is_runtime_error(self):
        assert issubclass(TokenRevocationError, RuntimeError)


class TestVersionInvalidError:
    def test_is_runtime_error(self):
        assert issubclass(VersionInvalidError, RuntimeError)


class TestCapabilityRevoker:
    def test_creates(self):
        revoker = CapabilityRevoker()
        assert revoker is not None
        assert revoker._revoked_trace_ids == set()
        assert revoker._invalid_versions == set()

    def test_has_validate_token(self):
        assert hasattr(CapabilityRevoker, "validate_token")
