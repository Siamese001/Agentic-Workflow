"""Test ScannerGovernance functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestScannerGovernance:
    """Test ScannerGovernance functionality."""

    def test_scanner_governance_imports(self):
        """Test scanner_governance module imports."""
        from agentic_core import scanner_governance
        assert scanner_governance is not None

    def test_scanner_governance_class(self):
        """Test ScannerGovernance class exists."""
        from agentic_core import ScannerGovernance
        assert ScannerGovernance is not None

    def test_scanner_governance_callable(self):
        """Test scanner_governance functions are callable."""
        from agentic_core import validate_scanner_governance
        assert callable(validate_scanner_governance)
