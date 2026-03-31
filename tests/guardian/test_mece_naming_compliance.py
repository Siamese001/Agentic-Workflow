"""Test MeceNamingCompliance functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMeceNamingCompliance:
    """Test MeceNamingCompliance functionality."""

    def test_mece_naming_compliance_imports(self):
        """Test mece_naming_compliance module imports."""
        from agentic_core import mece_naming_compliance
        assert mece_naming_compliance is not None

    def test_mece_naming_compliance_class(self):
        """Test MeceNamingCompliance class exists."""
        from agentic_core import MeceNamingCompliance
        assert MeceNamingCompliance is not None

    def test_mece_naming_compliance_callable(self):
        """Test mece_naming_compliance functions are callable."""
        from agentic_core import validate_mece_naming_compliance
        assert callable(validate_mece_naming_compliance)
