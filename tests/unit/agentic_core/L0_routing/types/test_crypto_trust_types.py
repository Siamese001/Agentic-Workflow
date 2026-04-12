"""Test CryptoTrustTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCryptoTrustTypes:
    """Test CryptoTrustTypes functionality."""

    def test_crypto_trust_types_imports(self):
        """Test crypto_trust_types module imports."""
        from agentic_core import crypto_trust_types

        assert crypto_trust_types is not None

    def test_crypto_trust_types_class(self):
        """Test CryptoTrustTypes class exists."""
        from agentic_core import CryptoTrustTypes

        assert CryptoTrustTypes is not None

    def test_crypto_trust_types_callable(self):
        """Test crypto_trust_types functions are callable."""
        from agentic_core import validate_crypto_trust_types

        assert callable(validate_crypto_trust_types)
