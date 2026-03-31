"""Test ADG residual gaps functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgResidualGaps:
    """Test ADG residual gaps functionality."""

    def test_residual_gaps_imports(self):
        """Test residual gaps module imports."""
        from tools.adg import identify_guardrail_gaps
        assert identify_guardrail_gaps is not None

    def test_gap_analysis_function_exists(self):
        """Test gap analysis function exists."""
        from tools.adg.identify_guardrail_gaps import analyze_gaps
        assert callable(analyze_gaps)

    def test_gap_reporting_exists(self):
        """Test gap reporting exists."""
        from tools.adg.identify_guardrail_gaps import report_gaps
        assert callable(report_gaps)
