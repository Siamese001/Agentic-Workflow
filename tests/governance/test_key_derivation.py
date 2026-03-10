"""
Tests for HMAC key derivation with versioning.

Phase 0.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.enforcement.key_derivation import (
    derive_hmac_key,
    get_kdf_salt_hash,
    get_key_version,
    verify_key_version,
)


class TestDeriveHmacKey:
    def test_returns_tuple_of_three(self) -> None:
        key, version, salt_hash = derive_hmac_key(b"master-secret")
        assert isinstance(key, bytes)
        assert isinstance(version, str)
        assert isinstance(salt_hash, str)

    def test_key_is_32_bytes(self) -> None:
        key, _, _ = derive_hmac_key(b"master-secret")
        assert len(key) == 32

    def test_deterministic_for_same_input(self) -> None:
        k1, v1, s1 = derive_hmac_key(b"same-secret")
        k2, v2, s2 = derive_hmac_key(b"same-secret")
        assert k1 == k2
        assert v1 == v2
        assert s1 == s2

    def test_different_secrets_produce_different_keys(self) -> None:
        k1, _, _ = derive_hmac_key(b"secret-a")
        k2, _, _ = derive_hmac_key(b"secret-b")
        assert k1 != k2

    def test_version_string_nonempty(self) -> None:
        _, version, _ = derive_hmac_key(b"s")
        assert version

    def test_salt_hash_is_64_chars(self) -> None:
        _, _, salt_hash = derive_hmac_key(b"s")
        assert len(salt_hash) == 64
        assert all(c in "0123456789abcdef" for c in salt_hash)


class TestGetKeyVersion:
    def test_returns_string(self) -> None:
        assert isinstance(get_key_version(), str)

    def test_nonempty(self) -> None:
        assert get_key_version()


class TestVerifyKeyVersion:
    def test_current_version_valid(self) -> None:
        current = get_key_version()
        assert verify_key_version(current) is True

    def test_wrong_version_invalid(self) -> None:
        assert verify_key_version("99999") is False

    def test_empty_string_invalid(self) -> None:
        assert verify_key_version("") is False


class TestGetKdfSaltHash:
    def test_is_hex_64(self) -> None:
        h = get_kdf_salt_hash()
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_stable_across_calls(self) -> None:
        assert get_kdf_salt_hash() == get_kdf_salt_hash()
