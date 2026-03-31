"""Test ContentRelevanceImplAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestContentRelevanceImplAdg:
    """Test ContentRelevanceImplAdg functionality."""

    def test_content_relevance_impl_adg_imports(self):
        """Test content_relevance_impl_adg module imports."""
        from agentic_core import content_relevance_impl_adg
        assert content_relevance_impl_adg is not None

    def test_content_relevance_impl_adg_class(self):
        """Test ContentRelevanceImplAdg class exists."""
        from agentic_core import ContentRelevanceImplAdg
        assert ContentRelevanceImplAdg is not None

    def test_content_relevance_impl_adg_callable(self):
        """Test content_relevance_impl_adg functions are callable."""
        from agentic_core import validate_content_relevance_impl_adg
        assert callable(validate_content_relevance_impl_adg)
