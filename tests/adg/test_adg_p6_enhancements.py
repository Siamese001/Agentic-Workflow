"""Test ADG P6 enhancements functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgP6Enhancements:
    """Test ADG P6 enhancements functionality."""

    def test_p6_enhancements_imports(self):
        """Test P6 enhancements module imports."""
        from agentic_core.adg.extraction import static_scanner
        assert static_scanner is not None

    def test_p6_test_linkage_exists(self):
        """Test P6 test execution linkage exists."""
        from agentic_core.adg.extraction.static_scanner import _TestExecutionLinkageVisitor
        assert _TestExecutionLinkageVisitor is not None

    def test_p6_violation_propagation_exists(self):
        """Test P6 violation propagation exists."""
        from agentic_core.adg.extraction.static_scanner import _propagate_violations
        assert callable(_propagate_violations)
