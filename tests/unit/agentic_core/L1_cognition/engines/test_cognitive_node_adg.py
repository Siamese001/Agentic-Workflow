"""Test CognitiveNodeAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCognitiveNodeAdg:
    """Test CognitiveNodeAdg functionality."""

    def test_cognitive_node_adg_imports(self):
        """Test cognitive_node_adg module imports."""
        from agentic_core import cognitive_node_adg
        assert cognitive_node_adg is not None

    def test_cognitive_node_adg_class(self):
        """Test CognitiveNodeAdg class exists."""
        from agentic_core import CognitiveNodeAdg
        assert CognitiveNodeAdg is not None

    def test_cognitive_node_adg_callable(self):
        """Test cognitive_node_adg functions are callable."""
        from agentic_core import validate_cognitive_node_adg
        assert callable(validate_cognitive_node_adg)
