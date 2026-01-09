# tests/unit/test_convergence_loop.py
"""Unit tests for L6 Convergence Loop."""
from __future__ import annotations
import pytest
from pathlib import Path


class TestConvergenceLoopStructure:
    """Test convergence loop related modules exist."""

    def test_mission_controller_file_exists(self):
        """Test mission_controller.py exists."""
        path = Path(__file__).parent.parent.parent / 'agentic_core' / 'L3_orchestration' / 'workflow_engines' / 'mission_controller.py'
        assert path.exists()

    def test_mission_controller_convergence_file_exists(self):
        """Test mission_controller_convergence.py exists."""
        path = Path(__file__).parent.parent.parent / 'agentic_core' / 'L3_orchestration' / 'workflow_engines' / 'mission_controller_convergence.py'
        assert path.exists()

    def test_mission_orchestrator_file_exists(self):
        """Test mission_orchestrator.py exists."""
        path = Path(__file__).parent.parent.parent / 'agentic_core' / 'L3_orchestration' / 'workflow_engines' / 'mission_orchestrator.py'
        assert path.exists()
