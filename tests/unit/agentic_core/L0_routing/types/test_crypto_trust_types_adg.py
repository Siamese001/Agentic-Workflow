"""Test CryptoTrustTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCryptoTrustTypesAdg:
    """Test CryptoTrustTypesAdg functionality."""

    def test_crypto_trust_types_adg_imports(self):
        """Test crypto_trust_types_adg module imports."""
        from agentic_core import crypto_trust_types_adg

        assert crypto_trust_types_adg is not None

    def test_crypto_trust_types_adg_class(self):
        """Test CryptoTrustTypesAdg class exists."""
        from agentic_core import CryptoTrustTypesAdg

        assert CryptoTrustTypesAdg is not None

    def test_crypto_trust_types_adg_callable(self):
        """Test crypto_trust_types_adg functions are callable."""
        from agentic_core import validate_crypto_trust_types_adg

        assert callable(validate_crypto_trust_types_adg)
