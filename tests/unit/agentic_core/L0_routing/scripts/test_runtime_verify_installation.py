"""Test RuntimeVerifyInstallation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRuntimeVerifyInstallation:
    """Test RuntimeVerifyInstallation functionality."""

    def test_runtime_verify_installation_imports(self):
        """Test runtime_verify_installation module imports."""
        from agentic_core import runtime_verify_installation
        assert runtime_verify_installation is not None

    def test_runtime_verify_installation_class(self):
        """Test RuntimeVerifyInstallation class exists."""
        from agentic_core import RuntimeVerifyInstallation
        assert RuntimeVerifyInstallation is not None

    def test_runtime_verify_installation_callable(self):
        """Test runtime_verify_installation functions are callable."""
        from agentic_core import validate_runtime_verify_installation
        assert callable(validate_runtime_verify_installation)
