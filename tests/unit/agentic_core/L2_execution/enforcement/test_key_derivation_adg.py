"""ADG-driven tests for L2_execution/enforcement/key_derivation.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.key_derivation import (
    derive_hmac_key,
    _CURRENT_KEY_VERSION,
    _KDF_SALT,
)


class TestDeriveHmacKey:
    def test_callable(self):
        assert callable(derive_hmac_key)

    def test_returns_tuple(self):
        result = derive_hmac_key(b"master-secret-bytes")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_key_bytes_non_empty(self):
        key, version, salt_hash = derive_hmac_key(b"test-secret")
        assert len(key) > 0
        assert isinstance(key, bytes)

    def test_version_string(self):
        _, version, _ = derive_hmac_key(b"test-secret")
        assert isinstance(version, str)
        assert version == _CURRENT_KEY_VERSION

    def test_salt_hash_hex_string(self):
        _, _, salt_hash = derive_hmac_key(b"test-secret")
        assert isinstance(salt_hash, str)
        int(salt_hash, 16)

    def test_deterministic(self):
        r1 = derive_hmac_key(b"same-secret")
        r2 = derive_hmac_key(b"same-secret")
        assert r1 == r2

    def test_kdf_salt_is_bytes(self):
        assert isinstance(_KDF_SALT, bytes)
