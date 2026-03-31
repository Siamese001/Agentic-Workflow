"""Test SandboxEnvelopeBudget functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSandboxEnvelopeBudget:
    """Test SandboxEnvelopeBudget functionality."""

    def test_sandbox_envelope_budget_imports(self):
        """Test sandbox_envelope_budget module imports."""
        from agentic_core import sandbox_envelope_budget
        assert sandbox_envelope_budget is not None

    def test_sandbox_envelope_budget_class(self):
        """Test SandboxEnvelopeBudget class exists."""
        from agentic_core import SandboxEnvelopeBudget
        assert SandboxEnvelopeBudget is not None

    def test_sandbox_envelope_budget_callable(self):
        """Test sandbox_envelope_budget functions are callable."""
        from agentic_core import validate_sandbox_envelope_budget
        assert callable(validate_sandbox_envelope_budget)
