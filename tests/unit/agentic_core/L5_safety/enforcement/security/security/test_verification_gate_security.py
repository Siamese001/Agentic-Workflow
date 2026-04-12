"""Test VerificationGateSecurity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVerificationGateSecurity:
    """Test VerificationGateSecurity functionality."""

    def test_verification_gate_security_imports(self):
        """Test verification_gate_security module imports."""
        from agentic_core import verification_gate_security

        assert verification_gate_security is not None

    def test_verification_gate_security_class(self):
        """Test VerificationGateSecurity class exists."""
        from agentic_core import VerificationGateSecurity

        assert VerificationGateSecurity is not None

    def test_verification_gate_security_callable(self):
        """Test verification_gate_security functions are callable."""
        from agentic_core import validate_verification_gate_security

        assert callable(validate_verification_gate_security)
