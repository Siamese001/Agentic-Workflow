"""Test RagConfig functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRagConfig:
    """Test RagConfig functionality."""

    def test_rag_config_imports(self):
        """Test rag_config module imports."""
        from agentic_core import rag_config

        assert rag_config is not None

    def test_rag_config_class(self):
        """Test RagConfig class exists."""
        from agentic_core import RagConfig

        assert RagConfig is not None

    def test_rag_config_callable(self):
        """Test rag_config functions are callable."""
        from agentic_core import validate_rag_config

        assert callable(validate_rag_config)
