"""Test VoidComplianceConfig functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVoidComplianceConfig:
    """Test VoidComplianceConfig functionality."""

    def test_void_compliance_config_imports(self):
        """Test void_compliance_config module imports."""
        from agentic_core import void_compliance_config
        assert void_compliance_config is not None

    def test_void_compliance_config_class(self):
        """Test VoidComplianceConfig class exists."""
        from agentic_core import VoidComplianceConfig
        assert VoidComplianceConfig is not None

    def test_void_compliance_config_callable(self):
        """Test void_compliance_config functions are callable."""
        from agentic_core import validate_void_compliance_config
        assert callable(validate_void_compliance_config)
