"""Test EmbeddingInputGuardAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEmbeddingInputGuardAdg:
    """Test EmbeddingInputGuardAdg functionality."""

    def test_embedding_input_guard_adg_imports(self):
        """Test embedding_input_guard_adg module imports."""
        from agentic_core import embedding_input_guard_adg

        assert embedding_input_guard_adg is not None

    def test_embedding_input_guard_adg_class(self):
        """Test EmbeddingInputGuardAdg class exists."""
        from agentic_core import EmbeddingInputGuardAdg

        assert EmbeddingInputGuardAdg is not None

    def test_embedding_input_guard_adg_callable(self):
        """Test embedding_input_guard_adg functions are callable."""
        from agentic_core import validate_embedding_input_guard_adg

        assert callable(validate_embedding_input_guard_adg)
