"""Test RegistryVerification functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRegistryVerification:
    """Test RegistryVerification functionality."""

    def test_registry_verification_imports(self):
        """Test registry_verification module imports."""
        from agentic_core import registry_verification

        assert registry_verification is not None

    def test_registry_verification_class(self):
        """Test RegistryVerification class exists."""
        from agentic_core import RegistryVerification

        assert RegistryVerification is not None

    def test_registry_verification_callable(self):
        """Test registry_verification functions are callable."""
        from agentic_core import validate_registry_verification

        assert callable(validate_registry_verification)
