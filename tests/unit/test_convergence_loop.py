# tests/unit/test_convergence_loop.py
"""Unit tests for L6 Convergence Loop."""
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


class TestConvergenceLoopStructure:
    """Test convergence loop related modules exist."""

    def test_mission_controller_file_exists(self):
        """Test mission_controller.py exists."""
        path = Path(__file__).parent.parent.parent / AGENTIC_CORE_DIR / 'L3_orchestration' / 'workflow_engines' / 'mission_controller.py'
        assert path.exists()

    def test_mission_controller_convergence_file_exists(self):
        """Test mission_controller_convergence.py exists."""
        path = Path(__file__).parent.parent.parent / AGENTIC_CORE_DIR / 'L3_orchestration' / 'workflow_engines' / 'mission_controller_convergence.py'
        assert path.exists()

    def test_mission_orchestrator_file_exists(self):
        """Test mission_orchestrator.py exists."""
        path = Path(__file__).parent.parent.parent / AGENTIC_CORE_DIR / 'L3_orchestration' / 'workflow_engines' / 'mission_orchestrator.py'
        assert path.exists()
