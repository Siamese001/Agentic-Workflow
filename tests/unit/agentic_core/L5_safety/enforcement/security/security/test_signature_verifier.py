"""Test SignatureVerifier functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSignatureVerifier:
    """Test SignatureVerifier functionality."""

    def test_signature_verifier_imports(self):
        """Test signature_verifier module imports."""
        from agentic_core import signature_verifier
        assert signature_verifier is not None

    def test_signature_verifier_class(self):
        """Test SignatureVerifier class exists."""
        from agentic_core import SignatureVerifier
        assert SignatureVerifier is not None

    def test_signature_verifier_callable(self):
        """Test signature_verifier functions are callable."""
        from agentic_core import validate_signature_verifier
        assert callable(validate_signature_verifier)
