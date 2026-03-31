"""Test CapabilityBudgetAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCapabilityBudgetAdg:
    """Test CapabilityBudgetAdg functionality."""

    def test_capability_budget_adg_imports(self):
        """Test capability_budget_adg module imports."""
        from agentic_core import capability_budget_adg
        assert capability_budget_adg is not None

    def test_capability_budget_adg_class(self):
        """Test CapabilityBudgetAdg class exists."""
        from agentic_core import CapabilityBudgetAdg
        assert CapabilityBudgetAdg is not None

    def test_capability_budget_adg_callable(self):
        """Test capability_budget_adg functions are callable."""
        from agentic_core import validate_capability_budget_adg
        assert callable(validate_capability_budget_adg)
