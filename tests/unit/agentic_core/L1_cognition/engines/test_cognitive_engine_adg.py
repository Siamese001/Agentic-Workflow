"""Test CognitiveEngineAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCognitiveEngineAdg:
    """Test CognitiveEngineAdg functionality."""

    def test_cognitive_engine_adg_imports(self):
        """Test cognitive_engine_adg module imports."""
        from agentic_core import cognitive_engine_adg
        assert cognitive_engine_adg is not None

    def test_cognitive_engine_adg_class(self):
        """Test CognitiveEngineAdg class exists."""
        from agentic_core import CognitiveEngineAdg
        assert CognitiveEngineAdg is not None

    def test_cognitive_engine_adg_callable(self):
        """Test cognitive_engine_adg functions are callable."""
        from agentic_core import validate_cognitive_engine_adg
        assert callable(validate_cognitive_engine_adg)
