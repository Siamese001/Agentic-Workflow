"""Test GuardianArchitectureGovernance functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianArchitectureGovernance:
    """Test GuardianArchitectureGovernance functionality."""

    def test_guardian_architecture_governance_imports(self):
        """Test guardian_architecture_governance module imports."""
        from agentic_core import guardian_architecture_governance
        assert guardian_architecture_governance is not None

    def test_guardian_architecture_governance_class(self):
        """Test GuardianArchitectureGovernance class exists."""
        from agentic_core import GuardianArchitectureGovernance
        assert GuardianArchitectureGovernance is not None

    def test_guardian_architecture_governance_callable(self):
        """Test guardian_architecture_governance functions are callable."""
        from agentic_core import validate_guardian_architecture_governance
        assert callable(validate_guardian_architecture_governance)
