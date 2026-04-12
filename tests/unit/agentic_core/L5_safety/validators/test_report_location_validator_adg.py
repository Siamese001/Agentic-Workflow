"""Test ReportLocationValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReportLocationValidatorAdg:
    """Test ReportLocationValidatorAdg functionality."""

    def test_report_location_validator_adg_imports(self):
        """Test report_location_validator_adg module imports."""
        from agentic_core import report_location_validator_adg

        assert report_location_validator_adg is not None

    def test_report_location_validator_adg_class(self):
        """Test ReportLocationValidatorAdg class exists."""
        from agentic_core import ReportLocationValidatorAdg

        assert ReportLocationValidatorAdg is not None

    def test_report_location_validator_adg_callable(self):
        """Test report_location_validator_adg functions are callable."""
        from agentic_core import validate_report_location_validator_adg

        assert callable(validate_report_location_validator_adg)
