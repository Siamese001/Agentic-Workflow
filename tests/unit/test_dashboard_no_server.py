# tests/unit/test_dashboard_no_server.py
"""Unit tests for L6 Dashboard without server dependencies."""
from __future__ import annotations
import pytest
from pathlib import Path


class TestDashboardNoServer:
    """Test dashboard can work without external server."""

    def test_data_generator_can_be_imported(self):
        """Test DashboardDataGenerator can be imported."""
        from agentic_core.L6_observability.dashboards.data_generator import DashboardDataGenerator
        assert DashboardDataGenerator is not None

    def test_dashboards_module_importable(self):
        """Test dashboards module can be imported."""
        import agentic_core.L6_observability.dashboards
        assert agentic_core.L6_observability.dashboards is not None
