"""Test ChangeImpactEngine functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestChangeImpactEngine:
    """Test ChangeImpactEngine functionality."""

    def test_change_impact_imports(self):
        """Test change impact module imports."""
        from agentic_core import change_impact_engine
        assert change_impact_engine is not None

    def test_change_impact_engine_class(self):
        """Test change impact engine class exists."""
        from agentic_core.change_impact_engine import ChangeImpactEngine
        assert ChangeImpactEngine is not None

    def test_analyze_change_impact(self):
        """Test analyze change impact function."""
        from agentic_core.change_impact_engine import analyze_change_impact
        assert callable(analyze_change_impact)
