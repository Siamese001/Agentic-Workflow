"""Test ScanTestingComplianceUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestScanTestingComplianceUtil:
    """Test ScanTestingComplianceUtil functionality."""

    def test_scan_testing_compliance_util_imports(self):
        """Test scan_testing_compliance_util module imports."""
        from agentic_core import scan_testing_compliance_util

        assert scan_testing_compliance_util is not None

    def test_scan_testing_compliance_util_class(self):
        """Test ScanTestingComplianceUtil class exists."""
        from agentic_core import ScanTestingComplianceUtil

        assert ScanTestingComplianceUtil is not None

    def test_scan_testing_compliance_util_callable(self):
        """Test scan_testing_compliance_util functions are callable."""
        from agentic_core import validate_scan_testing_compliance_util

        assert callable(validate_scan_testing_compliance_util)
