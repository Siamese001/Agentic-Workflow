"""Test RerankerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRerankerAdg:
    """Test RerankerAdg functionality."""

    def test_reranker_adg_imports(self):
        """Test reranker_adg module imports."""
        from agentic_core import reranker_adg

        assert reranker_adg is not None

    def test_reranker_adg_class(self):
        """Test RerankerAdg class exists."""
        from agentic_core import RerankerAdg

        assert RerankerAdg is not None

    def test_reranker_adg_callable(self):
        """Test reranker_adg functions are callable."""
        from agentic_core import validate_reranker_adg

        assert callable(validate_reranker_adg)
