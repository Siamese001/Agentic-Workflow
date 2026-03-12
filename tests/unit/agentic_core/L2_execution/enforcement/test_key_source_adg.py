"""ADG-driven tests for L2_execution/enforcement/key_source.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.key_source import KeySource, TestKeySource


class TestKeySourceABC:
    def test_is_abstract(self):
        import abc
        assert issubclass(KeySource, abc.ABC)

    def test_has_get_secret(self):
        assert hasattr(KeySource, "get_secret")

    def test_has_assert_key_scope(self):
        assert hasattr(KeySource, "assert_key_scope")

    def test_has_reject_expired_key(self):
        assert hasattr(KeySource, "reject_expired_key")


class TestTestKeySource:
    def test_creates(self):
        ks = TestKeySource()
        assert ks is not None

    def test_test_secret_is_bytes(self):
        assert isinstance(TestKeySource.TEST_SECRET, bytes)

    def test_get_secret_returns_bytes(self):
        ks = TestKeySource()
        secret = ks.get_secret()
        assert isinstance(secret, bytes)
        assert len(secret) > 0

    def test_assert_key_scope_valid(self):
        ks = TestKeySource()
        ks.assert_key_scope("signature")

    def test_assert_key_scope_invalid_raises(self):
        ks = TestKeySource()
        with pytest.raises((PermissionError, ValueError)):
            ks.assert_key_scope("invalid_scope")
