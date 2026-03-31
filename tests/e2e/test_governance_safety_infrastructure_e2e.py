"""Test GovernanceSafetyInfrastructureE2e functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGovernanceSafetyInfrastructureE2e:
    """Test GovernanceSafetyInfrastructureE2e functionality."""

    def test_governance_safety_infrastructure_e2e_imports(self):
        """Test governance_safety_infrastructure_e2e module imports."""
        from agentic_core import governance_safety_infrastructure_e2e
        assert governance_safety_infrastructure_e2e is not None

    def test_governance_safety_infrastructure_e2e_class(self):
        """Test GovernanceSafetyInfrastructureE2e class exists."""
        from agentic_core import GovernanceSafetyInfrastructureE2e
        assert GovernanceSafetyInfrastructureE2e is not None

    def test_governance_safety_infrastructure_e2e_callable(self):
        """Test governance_safety_infrastructure_e2e functions are callable."""
        from agentic_core import validate_governance_safety_infrastructure_e2e
        assert callable(validate_governance_safety_infrastructure_e2e)
