"""Test C0ContextRetrieverAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestC0ContextRetrieverAdg:
    """Test C0ContextRetrieverAdg functionality."""

    def test_c0_context_retriever_adg_imports(self):
        """Test c0_context_retriever_adg module imports."""
        from agentic_core import c0_context_retriever_adg

        assert c0_context_retriever_adg is not None

    def test_c0_context_retriever_adg_class(self):
        """Test C0ContextRetrieverAdg class exists."""
        from agentic_core import C0ContextRetrieverAdg

        assert C0ContextRetrieverAdg is not None

    def test_c0_context_retriever_adg_callable(self):
        """Test c0_context_retriever_adg functions are callable."""
        from agentic_core import validate_c0_context_retriever_adg

        assert callable(validate_c0_context_retriever_adg)
