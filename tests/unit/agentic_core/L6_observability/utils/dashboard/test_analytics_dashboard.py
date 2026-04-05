"""Test AnalyticsDashboard functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAnalyticsDashboard:
    """Test AnalyticsDashboard functionality."""

    def test_package_exports_dashboard_api(self):
        """Test the dashboard package exports the analytics dashboard API."""
        from agentic_core.L6_observability.dashboard import (
            AnalyticsDashboard,
            DashboardConfig,
            get_global_dashboard,
            start_analytics_dashboard,
            stop_analytics_dashboard,
        )

        assert AnalyticsDashboard is not None
        assert DashboardConfig is not None
        assert callable(get_global_dashboard)
        assert callable(start_analytics_dashboard)
        assert callable(stop_analytics_dashboard)

    def test_dashboard_default_state_is_deterministic(self):
        """Test the dashboard default state is stable and non-started."""
        from agentic_core.L6_observability.utils.dashboard.analytics_dashboard import (
            AnalyticsDashboard,
        )

        dashboard = AnalyticsDashboard()
        summary = dashboard.get_dashboard_summary()
        config = dashboard.export_dashboard_config()

        assert summary["dashboard_active"] is False
        assert summary["total_widgets"] >= 6
        assert summary["integrations"]["analytics_engine"] in {True, False}
        assert summary["integrations"]["observability_system"] in {True, False}
        assert summary["integrations"]["distributed_coordinator"] in {True, False}
        assert "widgets" in config
        assert len(config["widgets"]) >= 6
