"""Test StateTransactionTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStateTransactionTypesAdg:
    """Test StateTransactionTypesAdg functionality."""

    def test_state_transaction_types_adg_imports(self):
        """Test state_transaction_types_adg module imports."""
        from agentic_core import state_transaction_types_adg
        assert state_transaction_types_adg is not None

    def test_state_transaction_types_adg_class(self):
        """Test StateTransactionTypesAdg class exists."""
        from agentic_core import StateTransactionTypesAdg
        assert StateTransactionTypesAdg is not None

    def test_state_transaction_types_adg_callable(self):
        """Test state_transaction_types_adg functions are callable."""
        from agentic_core import validate_state_transaction_types_adg
        assert callable(validate_state_transaction_types_adg)
