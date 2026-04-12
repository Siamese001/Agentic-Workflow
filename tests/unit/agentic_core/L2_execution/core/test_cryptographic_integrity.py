"""Test CryptographicIntegrity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCryptographicIntegrity:
    """Test CryptographicIntegrity functionality."""

    def test_cryptographic_integrity_imports(self):
        """Test cryptographic_integrity module imports."""
        from agentic_core import cryptographic_integrity

        assert cryptographic_integrity is not None

    def test_cryptographic_integrity_class(self):
        """Test CryptographicIntegrity class exists."""
        from agentic_core import CryptographicIntegrity

        assert CryptographicIntegrity is not None

    def test_cryptographic_integrity_callable(self):
        """Test cryptographic_integrity functions are callable."""
        from agentic_core import validate_cryptographic_integrity

        assert callable(validate_cryptographic_integrity)
