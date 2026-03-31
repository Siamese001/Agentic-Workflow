"""Test SsotAlignment functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotAlignment:
    """Test SsotAlignment functionality."""

    def test_ssot_alignment_imports(self):
        """Test ssot_alignment module imports."""
        from agentic_core import ssot_alignment
        assert ssot_alignment is not None

    def test_ssot_alignment_class(self):
        """Test SsotAlignment class exists."""
        from agentic_core import SsotAlignment
        assert SsotAlignment is not None

    def test_ssot_alignment_callable(self):
        """Test ssot_alignment functions are callable."""
        from agentic_core import validate_ssot_alignment
        assert callable(validate_ssot_alignment)
