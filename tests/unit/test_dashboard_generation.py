# tests/unit/test_dashboard_generation.py
"""Unit tests for L6 Dashboard Generation."""
from __future__ import annotations
import pytest
from pathlib import Path

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


class TestDashboardStructure:
    """Test dashboard module structure."""

    def test_dashboards_module_exists(self):
        """Test dashboards module can be imported."""
        import agentic_core.L6_observability.dashboards
        assert agentic_core.L6_observability.dashboards is not None

    def test_data_generator_exists(self):
        """Test data_generator.py exists."""
        path = Path(__file__).parent.parent.parent / AGENTIC_CORE_DIR / 'L6_observability' / 'dashboards' / 'data_generator.py'
        assert path.exists()
