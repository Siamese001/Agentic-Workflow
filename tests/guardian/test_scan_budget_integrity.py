"""Test ScanBudgetIntegrity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestScanBudgetIntegrity:
    """Test ScanBudgetIntegrity functionality."""

    def test_scan_budget_integrity_imports(self):
        """Test scan_budget_integrity module imports."""
        from agentic_core import scan_budget_integrity
        assert scan_budget_integrity is not None

    def test_scan_budget_integrity_class(self):
        """Test ScanBudgetIntegrity class exists."""
        from agentic_core import ScanBudgetIntegrity
        assert ScanBudgetIntegrity is not None

    def test_scan_budget_integrity_callable(self):
        """Test scan_budget_integrity functions are callable."""
        from agentic_core import validate_scan_budget_integrity
        assert callable(validate_scan_budget_integrity)
