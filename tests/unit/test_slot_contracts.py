"""Test SlotContracts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSlotContracts:
    """Test SlotContracts functionality."""

    def test_slot_contracts_imports(self):
        """Test slot_contracts module imports."""
        from agentic_core import slot_contracts
        assert slot_contracts is not None

    def test_slot_contracts_class(self):
        """Test SlotContracts class exists."""
        from agentic_core import SlotContracts
        assert SlotContracts is not None

    def test_slot_contracts_callable(self):
        """Test slot_contracts functions are callable."""
        from agentic_core import validate_slot_contracts
        assert callable(validate_slot_contracts)
