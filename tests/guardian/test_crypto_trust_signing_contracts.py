"""Test CryptoTrustSigningContracts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCryptoTrustSigningContracts:
    """Test CryptoTrustSigningContracts functionality."""

    def test_crypto_trust_signing_contracts_imports(self):
        """Test crypto_trust_signing_contracts module imports."""
        from agentic_core import crypto_trust_signing_contracts
        assert crypto_trust_signing_contracts is not None

    def test_crypto_trust_signing_contracts_class(self):
        """Test CryptoTrustSigningContracts class exists."""
        from agentic_core import CryptoTrustSigningContracts
        assert CryptoTrustSigningContracts is not None

    def test_crypto_trust_signing_contracts_callable(self):
        """Test crypto_trust_signing_contracts functions are callable."""
        from agentic_core import validate_crypto_trust_signing_contracts
        assert callable(validate_crypto_trust_signing_contracts)
