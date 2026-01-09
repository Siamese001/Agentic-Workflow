# tests/unit/test_ComplianceOrchestratorAgent.py
"""Unit tests for ComplianceOrchestratorAgent."""
from __future__ import annotations
import pytest
import os


class TestComplianceOrchestratorAgent:
    """Test ComplianceOrchestratorAgent structure."""

    def test_l3_orchestration_exists(self):
        """Test L3_orchestration module exists."""
        import agentic_core.L3_orchestration
        assert agentic_core.L3_orchestration is not None

    def test_workflow_engines_importable(self):
        """Test workflow_engines directory exists."""
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'agentic_core', 'L3_orchestration', 'workflow_engines')
        assert os.path.isdir(path)
