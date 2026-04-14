"""Runtime-hardened top-level export tests for crypto trust types."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def agentic_core_package():
    return pytest.importorskip("agentic_core")


class TestExports:
    def test_module_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "crypto_trust_types", None) is not None

    def test_class_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "CryptoTrustTypes", None) is not None

    def test_validator_is_callable(self, agentic_core_package):
        validator = getattr(agentic_core_package, "validate_crypto_trust_types", None)
        assert callable(validator)
