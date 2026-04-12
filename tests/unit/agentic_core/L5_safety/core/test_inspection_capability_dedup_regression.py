"""Test InspectionCapabilityDedupRegression functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInspectionCapabilityDedupRegression:
    """Test InspectionCapabilityDedupRegression functionality."""

    def test_inspection_capability_dedup_regression_imports(self):
        """Test inspection_capability_dedup_regression module imports."""
        from agentic_core import inspection_capability_dedup_regression

        assert inspection_capability_dedup_regression is not None

    def test_inspection_capability_dedup_regression_class(self):
        """Test InspectionCapabilityDedupRegression class exists."""
        from agentic_core import InspectionCapabilityDedupRegression

        assert InspectionCapabilityDedupRegression is not None

    def test_inspection_capability_dedup_regression_callable(self):
        """Test inspection_capability_dedup_regression functions are callable."""
        from agentic_core import validate_inspection_capability_dedup_regression

        assert callable(validate_inspection_capability_dedup_regression)
