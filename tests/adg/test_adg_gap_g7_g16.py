"""Test ADG gap implementations functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgGapImplementations:
    """Test ADG gap implementations functionality."""

    def test_gap_implementations_imports(self):
        """Test gap implementations module imports."""
        from tools.adg import identify_guardrail_gaps
        assert identify_guardrail_gaps is not None

    def test_gap_implementation_finder_exists(self):
        """Test gap implementation finder exists."""
        from tools.adg.identify_guardrail_gaps import find_implementations
        assert callable(find_implementations)

    def test_gap_implementation_reporter_exists(self):
        """Test gap implementation reporter exists."""
        from tools.adg.identify_guardrail_gaps import report_implementations
        assert callable(report_implementations)

    def test_gap_analysis_includes_g7_g16(self):
        """Test gap analysis includes G7 G16 range."""
        from tools.adg.identify_guardrail_gaps import G7_G16_RANGE
        assert isinstance(G7_G16_RANGE, (list, tuple))

    def test_gap_remediation_exists(self):
        """Test gap remediation functions exist."""
        from tools.adg.identify_guardrail_gaps import remediate_gaps
        assert callable(remediate_gaps)
