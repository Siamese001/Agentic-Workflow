"""Test GuardianChangePackageActivation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianChangePackageActivation:
    """Test GuardianChangePackageActivation functionality."""

    def test_guardian_change_package_activation_imports(self):
        """Test guardian_change_package_activation module imports."""
        from agentic_core import guardian_change_package_activation
        assert guardian_change_package_activation is not None

    def test_guardian_change_package_activation_class(self):
        """Test GuardianChangePackageActivation class exists."""
        from agentic_core import GuardianChangePackageActivation
        assert GuardianChangePackageActivation is not None

    def test_guardian_change_package_activation_callable(self):
        """Test guardian_change_package_activation functions are callable."""
        from agentic_core import validate_guardian_change_package_activation
        assert callable(validate_guardian_change_package_activation)
