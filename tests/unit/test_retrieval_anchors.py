"""Test RetrievalAnchors functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRetrievalAnchors:
    """Test RetrievalAnchors functionality."""

    def test_retrieval_anchors_imports(self):
        """Test retrieval_anchors module imports."""
        from agentic_core import retrieval_anchors
        assert retrieval_anchors is not None

    def test_retrieval_anchors_class(self):
        """Test RetrievalAnchors class exists."""
        from agentic_core import RetrievalAnchors
        assert RetrievalAnchors is not None

    def test_retrieval_anchors_callable(self):
        """Test retrieval_anchors functions are callable."""
        from agentic_core import validate_retrieval_anchors
        assert callable(validate_retrieval_anchors)
