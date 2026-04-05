"""Test GapClosureEngineAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGapClosureEngineAdg:
    """Test GapClosureEngineAdg functionality."""

    def test_gap_closure_engine_adg_imports(self):
        """Test gap_closure_engine_adg module imports."""
        from agentic_core import gap_closure_engine_adg
        assert gap_closure_engine_adg is not None

    def test_gap_closure_engine_adg_class(self):
        """Test GapClosureEngineAdg class exists."""
        from agentic_core import GapClosureEngineAdg
        assert GapClosureEngineAdg is not None

    def test_gap_closure_engine_adg_callable(self):
        """Test gap_closure_engine_adg functions are callable."""
        from agentic_core import validate_gap_closure_engine_adg
        assert callable(validate_gap_closure_engine_adg)
