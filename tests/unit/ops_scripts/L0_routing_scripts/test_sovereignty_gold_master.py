"""Test SovereigntyGoldMaster functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereigntyGoldMaster:
    """Test SovereigntyGoldMaster functionality."""

    def test_sovereignty_gold_master_imports(self):
        """Test sovereignty_gold_master module imports."""
        from agentic_core import sovereignty_gold_master

        assert sovereignty_gold_master is not None

    def test_sovereignty_gold_master_class(self):
        """Test SovereigntyGoldMaster class exists."""
        from agentic_core import SovereigntyGoldMaster

        assert SovereigntyGoldMaster is not None

    def test_sovereignty_gold_master_callable(self):
        """Test sovereignty_gold_master functions are callable."""
        from agentic_core import validate_sovereignty_gold_master

        assert callable(validate_sovereignty_gold_master)
