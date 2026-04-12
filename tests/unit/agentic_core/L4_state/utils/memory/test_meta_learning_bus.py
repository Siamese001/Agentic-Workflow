"""Test MetaLearningBus functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningBus:
    """Test MetaLearningBus functionality."""

    def test_meta_learning_bus_imports(self):
        """Test meta_learning_bus module imports."""
        from agentic_core import meta_learning_bus

        assert meta_learning_bus is not None

    def test_meta_learning_bus_class(self):
        """Test MetaLearningBus class exists."""
        from agentic_core import MetaLearningBus

        assert MetaLearningBus is not None

    def test_meta_learning_bus_callable(self):
        """Test meta_learning_bus functions are callable."""
        from agentic_core import validate_meta_learning_bus

        assert callable(validate_meta_learning_bus)
