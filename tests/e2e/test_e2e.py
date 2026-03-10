"""
Dashboard End-to-End Tests
==========================

Comprehensive end-to-end tests for the dashboard.

Migrated from: agentic_core/L5_safety/validators/test_dashboard_end_to_end.py
"""

import sys
from pathlib import Path

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.dashboard
class TestAgentDiscovery:
    """Test agent discovery data."""

    def test_agent_discovery_file_exists(self, project_root):
        """Verify agent_discovery_full.json exists."""
        discovery_file = project_root / "agent_discovery_full.json"
        assert discovery_file.exists(), f"Missing: {discovery_file}"

    def test_agent_discovery_has_agents(self, agent_discovery_data):
        """Verify agent discovery contains agents."""
        assert len(agent_discovery_data) > 0, "No agents found in discovery"

    def test_agents_have_required_fields(self, agent_discovery_data):
        """Verify agents have required fields."""
        required_fields = ["class_name", "path", "territory"]
        for agent in agent_discovery_data[:10]:  # Check first 10
            for field in required_fields:
                assert field in agent, f"Agent missing field: {field}"


@pytest.mark.dashboard
class TestDashboardHTML:
    """Test dashboard HTML file."""

    def test_html_file_exists(self, html_file):
        """Verify dashboard HTML file exists."""
        assert html_file.exists(), f"Missing: {html_file}"

    def test_html_has_dashboard_data(self, html_content):
        """Verify HTML contains dashboard data."""
        assert "dashboardData" in html_content, "dashboardData not found in HTML"

    def test_html_has_tables(self, html_content):
        """Verify HTML contains table elements."""
        assert "<table" in html_content, "No tables found in HTML"


@pytest.mark.dashboard
class TestDashboardData:
    """Test dashboard data structure."""

    def test_dashboard_data_file_exists(self, dashboard_dir):
        """Verify dashboard_data.js exists."""
        data_file = dashboard_dir / "data" / "dashboard_data.js"
        assert data_file.exists(), f"Missing: {data_file}"

    def test_dashboard_data_is_valid_json(self, dashboard_data):
        """Verify dashboard data is valid JSON."""
        assert isinstance(dashboard_data, list), "Dashboard data should be a list"

    def test_dashboard_data_has_rows(self, dashboard_data):
        """Verify dashboard data has rows."""
        assert len(dashboard_data) > 0, "Dashboard data is empty"


@pytest.mark.dashboard
class TestDataConsistency:
    """Test data consistency between discovery and dashboard."""

    def test_total_agent_count_matches(self, agent_discovery_data, dashboard_data):
        """Verify total agent count matches between discovery and dashboard."""
        discovery_count = len(agent_discovery_data)

        total_row = next((r for r in dashboard_data if r.get("Territory") == "TOTAL"), None)
        assert total_row is not None, "TOTAL row not found"

        dashboard_count = total_row.get("Total", 0)
        assert dashboard_count == discovery_count, (
            f"Agent count mismatch: discovery={discovery_count}, dashboard={dashboard_count}"
        )


@pytest.mark.dashboard
class TestTableRendering:
    """Test table rendering elements."""

    def test_kpi_grid_exists(self, html_content):
        """Verify KPI grid container exists."""
        assert "kpiGrid" in html_content or "kpi-grid" in html_content

    def test_table_headers_exist(self, html_content):
        """Verify table headers exist."""
        assert "<th" in html_content, "No table headers found"


@pytest.mark.dashboard
class TestRowOrder:
    """Test row ordering in dashboard data."""

    def test_total_row_is_first(self, dashboard_data):
        """Verify TOTAL row is first."""
        assert dashboard_data[0].get("Territory") == "TOTAL", "TOTAL row should be first"

    def test_territories_are_sorted(self, dashboard_data):
        """Verify territories follow canonical order."""
        # Skip TOTAL row and check that L6 comes before L5, etc.
        territories = [r.get("Territory") for r in dashboard_data[1:]]

        # Basic check: L6 territories should come before L5
        l6_indices = [i for i, t in enumerate(territories) if t and "L6" in t]
        l5_indices = [i for i, t in enumerate(territories) if t and "L5" in t]

        if l6_indices and l5_indices:
            assert max(l6_indices) < min(l5_indices), "L6 territories should come before L5 territories"


@pytest.mark.dashboard
@pytest.mark.slow
@pytest.mark.playwright
class TestPlaywrightVisual:
    """Visual tests requiring Playwright."""

    def test_playwright_available(self):
        """Check if Playwright is available."""
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401

            assert True
        except ImportError:
            pytest.fail("Playwright is not installed — install it: pip install playwright && playwright install")

    def test_tables_render_in_browser(self):
        """Test that tables render correctly in browser."""
        pytest.fail("test_tables_render_in_browser is not implemented — write the test or delete it")
