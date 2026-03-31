"""Test ADG gap remediation P0 P4 functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgGapRemediationP0P4:
    """Test ADG gap remediation P0 P4 functionality."""

    def test_gap_remediation_p0_p4_imports(self):
        """Test gap remediation P0 P4 module imports."""
        from tools.adg import identify_guardrail_gaps
        assert identify_guardrail_gaps is not None

    def test_p0_p4_gap_analysis(self):
        """Test P0 P4 gap analysis function."""
        from tools.adg.identify_guardrail_gaps import analyze_p0_p4_gaps
        assert callable(analyze_p0_p4_gaps)

    def test_p0_p4_gap_remediation(self):
        """Test P0 P4 gap remediation function."""
        from tools.adg.identify_guardrail_gaps import remediate_p0_p4_gaps
        assert callable(remediate_p0_p4_gaps)
