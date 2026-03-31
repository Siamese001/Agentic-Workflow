"""Test GovernanceEscalationContracts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGovernanceEscalationContracts:
    """Test GovernanceEscalationContracts functionality."""

    def test_governance_escalation_contracts_imports(self):
        """Test governance_escalation_contracts module imports."""
        from agentic_core import governance_escalation_contracts
        assert governance_escalation_contracts is not None

    def test_governance_escalation_contracts_class(self):
        """Test GovernanceEscalationContracts class exists."""
        from agentic_core import GovernanceEscalationContracts
        assert GovernanceEscalationContracts is not None

    def test_governance_escalation_contracts_callable(self):
        """Test governance_escalation_contracts functions are callable."""
        from agentic_core import validate_governance_escalation_contracts
        assert callable(validate_governance_escalation_contracts)
