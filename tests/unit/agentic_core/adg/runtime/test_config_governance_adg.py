"""Test ConfigGovernanceAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestConfigGovernanceAdg:
    """Test ConfigGovernanceAdg functionality."""

    def test_config_governance_adg_imports(self):
        """Test config_governance_adg module imports."""
        from agentic_core import config_governance_adg

        assert config_governance_adg is not None

    def test_config_governance_adg_class(self):
        """Test ConfigGovernanceAdg class exists."""
        from agentic_core import ConfigGovernanceAdg

        assert ConfigGovernanceAdg is not None

    def test_config_governance_adg_callable(self):
        """Test config_governance_adg functions are callable."""
        from agentic_core import validate_config_governance_adg

        assert callable(validate_config_governance_adg)
