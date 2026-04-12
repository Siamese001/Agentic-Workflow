"""Test BudgetEnforcerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBudgetEnforcerAdg:
    """Test BudgetEnforcerAdg functionality."""

    def test_budget_enforcer_adg_imports(self):
        """Test budget_enforcer_adg module imports."""
        from agentic_core import budget_enforcer_adg

        assert budget_enforcer_adg is not None

    def test_budget_enforcer_adg_class(self):
        """Test BudgetEnforcerAdg class exists."""
        from agentic_core import BudgetEnforcerAdg

        assert BudgetEnforcerAdg is not None

    def test_budget_enforcer_adg_callable(self):
        """Test budget_enforcer_adg functions are callable."""
        from agentic_core import validate_budget_enforcer_adg

        assert callable(validate_budget_enforcer_adg)
