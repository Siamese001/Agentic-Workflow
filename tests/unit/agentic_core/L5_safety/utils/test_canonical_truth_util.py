"""Test CanonicalTruthUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCanonicalTruthUtil:
    """Test CanonicalTruthUtil functionality."""

    def test_canonical_truth_util_imports(self):
        """Test canonical_truth_util module imports."""
        from agentic_core import canonical_truth_util

        assert canonical_truth_util is not None

    def test_canonical_truth_util_class(self):
        """Test CanonicalTruthUtil class exists."""
        from agentic_core import CanonicalTruthUtil

        assert CanonicalTruthUtil is not None

    def test_canonical_truth_util_callable(self):
        """Test canonical_truth_util functions are callable."""
        from agentic_core import validate_canonical_truth_util

        assert callable(validate_canonical_truth_util)
