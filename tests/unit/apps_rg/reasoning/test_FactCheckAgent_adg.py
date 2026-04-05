"""Test FactcheckagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFactcheckagentAdg:
    """Test FactcheckagentAdg functionality."""

    def test_FactCheckAgent_adg_imports(self):
        """Test FactCheckAgent_adg module imports."""
        from agentic_core import FactCheckAgent_adg
        assert FactCheckAgent_adg is not None

    def test_FactCheckAgent_adg_class(self):
        """Test FactcheckagentAdg class exists."""
        from agentic_core import FactcheckagentAdg
        assert FactcheckagentAdg is not None

    def test_FactCheckAgent_adg_callable(self):
        """Test FactCheckAgent_adg functions are callable."""
        from agentic_core import validate_FactCheckAgent_adg
        assert callable(validate_FactCheckAgent_adg)
