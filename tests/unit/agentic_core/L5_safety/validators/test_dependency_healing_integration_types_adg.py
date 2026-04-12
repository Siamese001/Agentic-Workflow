"""Test DependencyHealingIntegrationTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDependencyHealingIntegrationTypesAdg:
    """Test DependencyHealingIntegrationTypesAdg functionality."""

    def test_dependency_healing_integration_types_adg_imports(self):
        """Test dependency_healing_integration_types_adg module imports."""
        from agentic_core import dependency_healing_integration_types_adg

        assert dependency_healing_integration_types_adg is not None

    def test_dependency_healing_integration_types_adg_class(self):
        """Test DependencyHealingIntegrationTypesAdg class exists."""
        from agentic_core import DependencyHealingIntegrationTypesAdg

        assert DependencyHealingIntegrationTypesAdg is not None

    def test_dependency_healing_integration_types_adg_callable(self):
        """Test dependency_healing_integration_types_adg functions are callable."""
        from agentic_core import validate_dependency_healing_integration_types_adg

        assert callable(validate_dependency_healing_integration_types_adg)
