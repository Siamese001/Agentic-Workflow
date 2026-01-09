# tests/unit/test_dashboard_generation.py
"""Unit tests for L6 Dashboard Generation."""
from __future__ import annotations
import pytest
from pathlib import Path


class TestDashboardStructure:
    """Test dashboard module structure."""

    def test_dashboards_module_exists(self):
        """Test dashboards module can be imported."""
        import agentic_core.L6_observability.dashboards
        assert agentic_core.L6_observability.dashboards is not None

    def test_data_generator_exists(self):
        """Test data_generator.py exists."""
        path = Path(__file__).parent.parent.parent / 'agentic_core' / 'L6_observability' / 'dashboards' / 'data_generator.py'
        assert path.exists()
