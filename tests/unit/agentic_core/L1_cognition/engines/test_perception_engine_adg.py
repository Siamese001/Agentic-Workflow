"""Test PerceptionEngineAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPerceptionEngineAdg:
    """Test PerceptionEngineAdg functionality."""

    def test_perception_engine_adg_imports(self):
        """Test perception_engine_adg module imports."""
        from agentic_core import perception_engine_adg
        assert perception_engine_adg is not None

    def test_perception_engine_adg_class(self):
        """Test PerceptionEngineAdg class exists."""
        from agentic_core import PerceptionEngineAdg
        assert PerceptionEngineAdg is not None

    def test_perception_engine_adg_callable(self):
        """Test perception_engine_adg functions are callable."""
        from agentic_core import validate_perception_engine_adg
        assert callable(validate_perception_engine_adg)
