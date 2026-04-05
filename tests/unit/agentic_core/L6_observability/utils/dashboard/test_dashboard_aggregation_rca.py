"""Test DashboardAggregationRca functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDashboardAggregationRca:
    """Test DashboardAggregationRca functionality."""

    def test_dashboard_aggregation_rca_imports(self):
        """Test dashboard_aggregation_rca module imports."""
        from agentic_core import dashboard_aggregation_rca
        assert dashboard_aggregation_rca is not None

    def test_dashboard_aggregation_rca_class(self):
        """Test DashboardAggregationRca class exists."""
        from agentic_core import DashboardAggregationRca
        assert DashboardAggregationRca is not None

    def test_dashboard_aggregation_rca_callable(self):
        """Test dashboard_aggregation_rca functions are callable."""
        from agentic_core import validate_dashboard_aggregation_rca
        assert callable(validate_dashboard_aggregation_rca)
