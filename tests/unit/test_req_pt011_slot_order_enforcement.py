"""Test ReqPt011SlotOrderEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReqPt011SlotOrderEnforcement:
    """Test ReqPt011SlotOrderEnforcement functionality."""

    def test_req_pt011_slot_order_enforcement_imports(self):
        """Test req_pt011_slot_order_enforcement module imports."""
        from agentic_core import req_pt011_slot_order_enforcement
        assert req_pt011_slot_order_enforcement is not None

    def test_req_pt011_slot_order_enforcement_class(self):
        """Test ReqPt011SlotOrderEnforcement class exists."""
        from agentic_core import ReqPt011SlotOrderEnforcement
        assert ReqPt011SlotOrderEnforcement is not None

    def test_req_pt011_slot_order_enforcement_callable(self):
        """Test req_pt011_slot_order_enforcement functions are callable."""
        from agentic_core import validate_req_pt011_slot_order_enforcement
        assert callable(validate_req_pt011_slot_order_enforcement)
