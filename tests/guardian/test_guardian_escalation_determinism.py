"""Test GuardianEscalationDeterminism functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianEscalationDeterminism:
    """Test GuardianEscalationDeterminism functionality."""

    def test_guardian_escalation_determinism_imports(self):
        """Test guardian_escalation_determinism module imports."""
        from agentic_core import guardian_escalation_determinism
        assert guardian_escalation_determinism is not None

    def test_guardian_escalation_determinism_class(self):
        """Test GuardianEscalationDeterminism class exists."""
        from agentic_core import GuardianEscalationDeterminism
        assert GuardianEscalationDeterminism is not None

    def test_guardian_escalation_determinism_callable(self):
        """Test guardian_escalation_determinism functions are callable."""
        from agentic_core import validate_guardian_escalation_determinism
        assert callable(validate_guardian_escalation_determinism)
