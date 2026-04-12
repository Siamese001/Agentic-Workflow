"""Test ChaosHealingIntegrationTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestChaosHealingIntegrationTypesAdg:
    """Test ChaosHealingIntegrationTypesAdg functionality."""

    def test_chaos_healing_integration_types_adg_imports(self):
        """Test chaos_healing_integration_types_adg module imports."""
        from agentic_core import chaos_healing_integration_types_adg

        assert chaos_healing_integration_types_adg is not None

    def test_chaos_healing_integration_types_adg_class(self):
        """Test ChaosHealingIntegrationTypesAdg class exists."""
        from agentic_core import ChaosHealingIntegrationTypesAdg

        assert ChaosHealingIntegrationTypesAdg is not None

    def test_chaos_healing_integration_types_adg_callable(self):
        """Test chaos_healing_integration_types_adg functions are callable."""
        from agentic_core import validate_chaos_healing_integration_types_adg

        assert callable(validate_chaos_healing_integration_types_adg)
