"""Test MetaLearningBridge functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningBridge:
    """Test MetaLearningBridge functionality."""

    def test_meta_learning_bridge_imports(self):
        """Test meta_learning_bridge module imports."""
        from agentic_core import meta_learning_bridge
        assert meta_learning_bridge is not None

    def test_meta_learning_bridge_class(self):
        """Test MetaLearningBridge class exists."""
        from agentic_core import MetaLearningBridge
        assert MetaLearningBridge is not None

    def test_meta_learning_bridge_callable(self):
        """Test meta_learning_bridge functions are callable."""
        from agentic_core import validate_meta_learning_bridge
        assert callable(validate_meta_learning_bridge)
