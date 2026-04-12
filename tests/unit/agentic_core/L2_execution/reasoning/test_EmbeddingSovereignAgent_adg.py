"""Test EmbeddingsovereignagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEmbeddingsovereignagentAdg:
    """Test EmbeddingsovereignagentAdg functionality."""

    def test_EmbeddingSovereignAgent_adg_imports(self):
        """Test EmbeddingSovereignAgent_adg module imports."""
        from agentic_core import EmbeddingSovereignAgent_adg

        assert EmbeddingSovereignAgent_adg is not None

    def test_EmbeddingSovereignAgent_adg_class(self):
        """Test EmbeddingsovereignagentAdg class exists."""
        from agentic_core import EmbeddingsovereignagentAdg

        assert EmbeddingsovereignagentAdg is not None

    def test_EmbeddingSovereignAgent_adg_callable(self):
        """Test EmbeddingSovereignAgent_adg functions are callable."""
        from agentic_core import validate_EmbeddingSovereignAgent_adg

        assert callable(validate_EmbeddingSovereignAgent_adg)
