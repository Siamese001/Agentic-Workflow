"""Test PtcInvariantsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPtcInvariantsAdg:
    """Test PtcInvariantsAdg functionality."""

    def test_ptc_invariants_adg_imports(self):
        """Test ptc_invariants_adg module imports."""
        from agentic_core import ptc_invariants_adg
        assert ptc_invariants_adg is not None

    def test_ptc_invariants_adg_class(self):
        """Test PtcInvariantsAdg class exists."""
        from agentic_core import PtcInvariantsAdg
        assert PtcInvariantsAdg is not None

    def test_ptc_invariants_adg_callable(self):
        """Test ptc_invariants_adg functions are callable."""
        from agentic_core import validate_ptc_invariants_adg
        assert callable(validate_ptc_invariants_adg)
