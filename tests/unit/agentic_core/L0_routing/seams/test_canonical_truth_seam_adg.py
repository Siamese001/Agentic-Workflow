"""Test CanonicalTruthSeamAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCanonicalTruthSeamAdg:
    """Test CanonicalTruthSeamAdg functionality."""

    def test_canonical_truth_seam_adg_imports(self):
        """Test canonical_truth_seam_adg module imports."""
        from agentic_core import canonical_truth_seam_adg

        assert canonical_truth_seam_adg is not None

    def test_canonical_truth_seam_adg_class(self):
        """Test CanonicalTruthSeamAdg class exists."""
        from agentic_core import CanonicalTruthSeamAdg

        assert CanonicalTruthSeamAdg is not None

    def test_canonical_truth_seam_adg_callable(self):
        """Test canonical_truth_seam_adg functions are callable."""
        from agentic_core import validate_canonical_truth_seam_adg

        assert callable(validate_canonical_truth_seam_adg)
