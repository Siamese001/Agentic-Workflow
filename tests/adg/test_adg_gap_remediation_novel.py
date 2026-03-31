"""Test ADG gap remediation novel functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgGapRemediationNovel:
    """Test ADG gap remediation novel functionality."""

    def test_gap_remediation_novel_imports(self):
        """Test gap remediation novel module imports."""
        from tools.adg import identify_guardrail_gaps
        assert identify_guardrail_gaps is not None

    def test_novel_gap_detection(self):
        """Test novel gap detection function."""
        from tools.adg.identify_guardrail_gaps import detect_novel_gaps
        assert callable(detect_novel_gaps)

    def test_novel_gap_remediation(self):
        """Test novel gap remediation function."""
        from tools.adg.identify_guardrail_gaps import remediate_novel_gaps
        assert callable(remediate_novel_gaps)
