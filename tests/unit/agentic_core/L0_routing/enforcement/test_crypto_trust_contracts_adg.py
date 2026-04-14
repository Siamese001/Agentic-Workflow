"""Runtime-hardened tests for crypto trust contract helpers."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


class TestCryptoTrustContracts:
    def test_hash_artifact_canonical_is_deterministic(self, enforcement_package):
        hash1 = enforcement_package.hash_artifact_canonical(b"test data")
        hash2 = enforcement_package.hash_artifact_canonical(b"test data")

        assert hash1 is not None
        assert hash1 == hash2

    def test_signing_error_class_is_available(self, enforcement_package):
        assert enforcement_package.SigningError is not None

    def test_exception_types_initialize(self, enforcement_package):
        assert isinstance(enforcement_package.SigningError(), Exception)
        assert isinstance(enforcement_package.VerificationError(), Exception)
