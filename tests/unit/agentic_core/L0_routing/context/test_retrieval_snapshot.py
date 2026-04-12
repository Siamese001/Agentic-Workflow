"""Test RetrievalSnapshot functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRetrievalSnapshot:
    """Test RetrievalSnapshot functionality."""

    def test_retrieval_snapshot_imports(self):
        """Test retrieval_snapshot module imports."""
        from agentic_core import retrieval_snapshot

        assert retrieval_snapshot is not None

    def test_retrieval_snapshot_class(self):
        """Test RetrievalSnapshot class exists."""
        from agentic_core import RetrievalSnapshot

        assert RetrievalSnapshot is not None

    def test_retrieval_snapshot_callable(self):
        """Test retrieval_snapshot functions are callable."""
        from agentic_core import validate_retrieval_snapshot

        assert callable(validate_retrieval_snapshot)
