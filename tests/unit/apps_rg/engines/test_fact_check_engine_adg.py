"""Test FactCheckEngineAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFactCheckEngineAdg:
    """Test FactCheckEngineAdg functionality."""

    def test_fact_check_engine_adg_imports(self):
        """Test fact_check_engine_adg module imports."""
        from agentic_core import fact_check_engine_adg
        assert fact_check_engine_adg is not None

    def test_fact_check_engine_adg_class(self):
        """Test FactCheckEngineAdg class exists."""
        from agentic_core import FactCheckEngineAdg
        assert FactCheckEngineAdg is not None

    def test_fact_check_engine_adg_callable(self):
        """Test fact_check_engine_adg functions are callable."""
        from agentic_core import validate_fact_check_engine_adg
        assert callable(validate_fact_check_engine_adg)
