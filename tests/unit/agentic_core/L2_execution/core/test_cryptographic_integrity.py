"""Smoke tests for CryptographicIntegrity exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestCryptographicIntegrity:
    """Smoke tests for CryptographicIntegrity exports."""

    def test_cryptographic_integrity_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "cryptographic_integrity")
        assert module is not None

    def test_cryptographic_integrity_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "CryptographicIntegrity")
        assert klass is not None

    def test_cryptographic_integrity_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_cryptographic_integrity")
        assert callable(validator)
