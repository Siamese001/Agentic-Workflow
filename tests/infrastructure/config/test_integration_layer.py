"""Test IntegrationLayer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIntegrationLayer:
    """Test IntegrationLayer functionality."""

    def test_integration_layer_imports(self):
        """Test integration_layer module imports."""
        from agentic_core import integration_layer

        assert integration_layer is not None

    def test_integration_layer_class(self):
        """Test IntegrationLayer class exists."""
        from agentic_core import IntegrationLayer

        assert IntegrationLayer is not None

    def test_integration_layer_callable(self):
        """Test integration_layer functions are callable."""
        from agentic_core import validate_integration_layer

        assert callable(validate_integration_layer)
