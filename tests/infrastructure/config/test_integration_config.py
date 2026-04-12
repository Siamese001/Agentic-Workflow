"""Test IntegrationConfig functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIntegrationConfig:
    """Test IntegrationConfig functionality."""

    def test_integration_config_imports(self):
        """Test integration_config module imports."""
        from agentic_core import integration_config

        assert integration_config is not None

    def test_integration_config_class(self):
        """Test IntegrationConfig class exists."""
        from agentic_core import IntegrationConfig

        assert IntegrationConfig is not None

    def test_integration_config_callable(self):
        """Test integration_config functions are callable."""
        from agentic_core import validate_integration_config

        assert callable(validate_integration_config)
