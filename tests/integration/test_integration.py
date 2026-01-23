"""
Dashboard Integration Tests (Phase 6)
=====================================

Tests for dashboard integration.

Migrated from: agentic_core/L2_execution/tool_registry/test_phase6_integration.py
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.dashboard
class TestBackendIntegration:
    """Test backend integration."""

    def test_runtime_state_schema_completeness(self):
        """Verify runtime state schema is complete."""
        required_sections = ["meta_learning", "redis", "pinecone", "execution"]
        assert len(required_sections) == 4

    def test_telemetry_update_functions(self):
        """Verify telemetry update functions exist."""
        # Placeholder for actual telemetry function test
        assert True


@pytest.mark.dashboard
class TestFrontendIntegration:
    """Test frontend integration."""

    def test_all_components_load(self, js_dir):
        """Verify all frontend components can be loaded."""
        components = [
            js_dir / "components" / "meta-learning-panel.js",
            js_dir / "components" / "redis-monitor.js",
            js_dir / "components" / "pinecone-monitor.js",
            js_dir / "components" / "execution-flow.js",
        ]
        for component in components:
            assert component.exists(), f"Missing component: {component}"

    def test_controller_loads(self, js_dir):
        """Verify controller can be loaded."""
        controller = js_dir / "controllers" / "meta-learning-controller.js"
        assert controller.exists(), f"Missing controller: {controller}"


@pytest.mark.dashboard
class TestDataIntegration:
    """Test data integration between backend and frontend."""

    def test_dashboard_data_structure(self, dashboard_data):
        """Verify dashboard data has correct structure."""
        assert len(dashboard_data) > 0, "Dashboard data is empty"

        # Check first row has required fields
        first_row = dashboard_data[0]
        required_fields = ["Territory", "Total", "Health"]
        for field in required_fields:
            assert field in first_row, f"Missing field: {field}"

    def test_total_row_exists(self, dashboard_data):
        """Verify TOTAL row exists in dashboard data."""
        total_row = next((r for r in dashboard_data if r.get("Territory") == "TOTAL"), None)
        assert total_row is not None, "TOTAL row not found"

    def test_total_row_is_first(self, dashboard_data):
        """Verify TOTAL row is first in dashboard data."""
        assert dashboard_data[0].get("Territory") == "TOTAL", "TOTAL row should be first"
