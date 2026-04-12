"""Test OrderCallToActionsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestOrderCallToActionsAdg:
    """Test OrderCallToActionsAdg functionality."""

    def test_order_call_to_actions_adg_imports(self):
        """Test order_call_to_actions_adg module imports."""
        from agentic_core import order_call_to_actions_adg

        assert order_call_to_actions_adg is not None

    def test_order_call_to_actions_adg_class(self):
        """Test OrderCallToActionsAdg class exists."""
        from agentic_core import OrderCallToActionsAdg

        assert OrderCallToActionsAdg is not None

    def test_order_call_to_actions_adg_callable(self):
        """Test order_call_to_actions_adg functions are callable."""
        from agentic_core import validate_order_call_to_actions_adg

        assert callable(validate_order_call_to_actions_adg)
