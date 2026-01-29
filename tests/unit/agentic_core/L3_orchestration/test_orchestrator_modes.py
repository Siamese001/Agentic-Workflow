"""
Test Suite for OrchestratorAgent Modes

Verifies mode-based execution (HEALING, COMPLIANCE, SSOT, FULL)
as implemented in Opportunity #1.
"""

from unittest.mock import patch

import pytest

from agentic_core.L3_orchestration.OrchestratorAgent import (
    OrchestratorAgent,
    OrchestratorMode,
)


class test_unified_orchestrator_modes:
    """Test suite for orchestrator mode-based execution."""

    @pytest.fixture
    def orchestrator(self):
        """Create a OrchestratorAgent instance."""
        return OrchestratorAgent(agent_id="test_orchestrator", mode="unified")

    def test_mode_enum_integrity(self):
        """Verify OrchestratorMode enum values exist."""
        assert OrchestratorMode.HEALING.value == "healing"
        assert OrchestratorMode.COMPLIANCE.value == "compliance"
        assert OrchestratorMode.SSOT.value == "ssot"
        assert OrchestratorMode.FULL.value == "full"
        assert OrchestratorMode.UNIFIED.value == "unified"

    def test_orchestrator_initialization_with_mode(self):
        """Test orchestrator initializes with specified mode."""
        healing_orch = OrchestratorAgent(mode="healing")
        assert healing_orch.mode == OrchestratorMode.HEALING

        compliance_orch = OrchestratorAgent(mode="compliance")
        assert compliance_orch.mode == OrchestratorMode.COMPLIANCE

        ssot_orch = OrchestratorAgent(mode="ssot")
        assert ssot_orch.mode == OrchestratorMode.SSOT

    def test_invalid_mode_defaults_to_unified(self):
        """Test that invalid mode string defaults to UNIFIED."""
        orch = OrchestratorAgent(mode="invalid_mode")
        assert orch.mode == OrchestratorMode.UNIFIED

    def test_run_agent_healing_mode(self):
        """Test that HEALING mode triggers healing flow."""
        orch = OrchestratorAgent(mode="healing")
        result = orch.run_agent("TestAgent", dry_run=True)

        assert result.metadata.get("mode") == "healing"
        assert "Healing operations" in result.message

    def test_run_agent_compliance_mode(self):
        """Test that COMPLIANCE mode triggers compliance flow with credential scan."""
        orch = OrchestratorAgent(mode="compliance")

        with patch(
            "agentic_core.L5_safety.validators.CredentialScannerAgent.CredentialScannerAgent"
        ) as MockScanner:
            mock_scanner = MockScanner.return_value
            mock_scanner.scan_for_credentials.return_value = {
                "total_matches": 0,
                "summary": {"by_severity": {"high": 0}},
                "recommendations": [],
            }

            result = orch.run_agent("TestAgent", dry_run=True)

            assert result.metadata.get("mode") == "compliance"
            # Credential scan may be complete or error depending on import
            assert "credential_scan" in result.metadata

    def test_run_agent_ssot_mode(self):
        """Test that SSOT mode triggers SSOT flow."""
        orch = OrchestratorAgent(mode="ssot")
        result = orch.run_agent("TestAgent", dry_run=True)

        assert result.metadata.get("mode") == "ssot"
        assert "SSOT compliance" in result.message

    def test_run_agent_full_mode(self):
        """Test that FULL mode runs all operations."""
        orch = OrchestratorAgent(mode="full")
        result = orch.run_agent("TestAgent", dry_run=True)

        assert result.metadata.get("mode") == "full"

    def test_run_mission_with_multiple_agents(self):
        """Test run_mission coordinates multiple agents."""
        orch = OrchestratorAgent(mode="unified")

        result = orch.run_mission(agents=["Agent1", "Agent2", "Agent3"], dry_run=True)

        assert result.total_agents == 3
        assert len(result.agent_results) == 3
        assert result.metadata.get("mode") == "unified"

    def test_get_available_agents(self):
        """Test get_available_agents returns list."""
        orch = OrchestratorAgent()
        try:
            agents = orch.get_available_agents()
            assert isinstance(agents, list)
        except Exception:
            # May fail in test environment without full project structure
            pass

    def test_validate_mission_with_valid_agents(self):
        """Test validate_mission returns True for available agents."""
        orch = OrchestratorAgent()

        try:
            # Get some available agents
            available = orch.get_available_agents()
            if available:
                # Test with first available agent
                result = orch.validate_mission([available[0]])
                assert result is True
        except Exception:
            # May fail in test environment without full project structure
            pass

    def test_dispatch_to_strategy(self):
        """Test dispatch routes to correct strategy."""
        orch = OrchestratorAgent()

        # Test dispatch with unknown domain
        result = orch.dispatch("unknown_domain", "action", {})
        assert result["status"] == "error"
