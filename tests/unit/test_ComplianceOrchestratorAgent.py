# tests/unit/test_ComplianceOrchestratorAgent.py
"""Unit tests for ComplianceOrchestratorAgent."""
from __future__ import annotations
import pytest
import os

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


class TestComplianceOrchestratorAgent:
    """Test ComplianceOrchestratorAgent structure."""

    def test_l3_orchestration_exists(self):
        """Test L3_orchestration module exists."""
        import agentic_core.L3_orchestration
        assert agentic_core.L3_orchestration is not None

    def test_workflow_engines_importable(self):
        """Test workflow_engines directory exists."""
        path = os.path.join(os.path.dirname(__file__), '..', '..', AGENTIC_CORE_DIR, 'L3_orchestration', 'workflow_engines')
        assert os.path.isdir(path)
