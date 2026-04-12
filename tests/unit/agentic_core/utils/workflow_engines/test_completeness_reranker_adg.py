"""Test CompletenessRerankerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCompletenessRerankerAdg:
    """Test CompletenessRerankerAdg functionality."""

    def test_completeness_reranker_adg_imports(self):
        """Test completeness_reranker_adg module imports."""
        from agentic_core import completeness_reranker_adg

        assert completeness_reranker_adg is not None

    def test_completeness_reranker_adg_class(self):
        """Test CompletenessRerankerAdg class exists."""
        from agentic_core import CompletenessRerankerAdg

        assert CompletenessRerankerAdg is not None

    def test_completeness_reranker_adg_callable(self):
        """Test completeness_reranker_adg functions are callable."""
        from agentic_core import validate_completeness_reranker_adg

        assert callable(validate_completeness_reranker_adg)
