"""Test MetaLearningBridgeAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningBridgeAdg:
    """Test MetaLearningBridgeAdg functionality."""

    def test_meta_learning_bridge_adg_imports(self):
        """Test meta_learning_bridge_adg module imports."""
        from agentic_core import meta_learning_bridge_adg

        assert meta_learning_bridge_adg is not None

    def test_meta_learning_bridge_adg_class(self):
        """Test MetaLearningBridgeAdg class exists."""
        from agentic_core import MetaLearningBridgeAdg

        assert MetaLearningBridgeAdg is not None

    def test_meta_learning_bridge_adg_callable(self):
        """Test meta_learning_bridge_adg functions are callable."""
        from agentic_core import validate_meta_learning_bridge_adg

        assert callable(validate_meta_learning_bridge_adg)
