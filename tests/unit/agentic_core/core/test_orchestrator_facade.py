"""
Unit Tests for OrchestratorAgent Facade - Phase 3

Tests the facade conversion of OrchestratorAgent including:
- Legacy signature compatibility
- L3OrchestrationStrategy functionality
- Mode-based behavior preservation
- Mission execution compatibility
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.engine.unified_agent import OrchestrationResult


class TestL3OrchestrationStrategy:
    """Tests for L3OrchestrationStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "workflow_steps": [
                {"name": "validate", "type": "validation"},
                {"name": "process", "type": "agent_call", "agent": "test"},
            ],
            "signal_handlers": {},
        }

    @pytest.fixture
    def strategy(self, config):
        """Create L3OrchestrationStrategy instance."""
        from agentic_core.L3_orchestration.OrchestratorAgent import (
            L3OrchestrationStrategy,
        )

        return L3OrchestrationStrategy(config, mode="unified")

    def test_initialization(self, strategy):
        """Test strategy initialization."""
        assert strategy.mode == "unified"
        assert strategy.project_root is not None
        assert strategy._import_cache == {}

    @pytest.mark.asyncio
    async def test_execute_complete_workflow(self, strategy):
        """Test execute completes workflow steps."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, OrchestrationResult)
        assert result.completed is True
        assert result.stage == "process"
        assert "validation_completed" in result.signals

    @pytest.mark.asyncio
    async def test_execute_empty_workflow(self):
        """Test execute with empty workflow."""
        from agentic_core.L3_orchestration.OrchestratorAgent import (
            L3OrchestrationStrategy,
        )

        strategy = L3OrchestrationStrategy({"workflow_steps": [], "signal_handlers": {}}, mode="unified")
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, OrchestrationResult)
        assert result.stage == "not_started"

    def test_get_available_agents(self, strategy):
        """Test get_available_agents returns list."""
        with patch("agentic_core.L3_orchestration.OrchestratorAgent.get_validated_project_root") as mock_root:
            mock_root.return_value = Path.cwd()
            with patch("agentic_core.L3_orchestration.OrchestratorAgent.get_agent_paths") as mock_paths:
                mock_paths.return_value = [
                    "/path/to/TestAgent.py",
                    "/path/to/OtherAgent.py",
                ]

                agents = strategy.get_available_agents()

                assert isinstance(agents, list)
                assert "TestAgent" in agents
                assert "OtherAgent" in agents


class TestOrchestratorAgentFacade:
    """Tests for OrchestratorAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create OrchestratorAgent instance."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L3_orchestration.OrchestratorAgent import (
                OrchestratorAgent,
            )

            agent = OrchestratorAgent(mode="unified")
            return agent

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_id == "unified_orchestrator_01"
        assert agent.agent_type == "L3_Unified"
        assert agent.project_root is not None

    def test_mode_setting(self, agent):
        """Test mode is set correctly."""
        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorMode

        assert agent.mode == OrchestratorMode.UNIFIED

    def test_unified_strategy_field_exists(self, agent):
        """Test unified strategy field is initialized."""
        assert hasattr(agent, "_unified_strategy")

    def test_strategies_property(self, agent):
        """Test strategies property returns dict."""
        with patch.object(agent, "logger"):
            strategies = agent.strategies
            assert isinstance(strategies, dict)

    def test_dispatch_unknown_domain(self, agent):
        """Test dispatch with unknown domain."""
        with patch.object(agent, "logger"):
            result = agent.dispatch("unknown", "action", {})
            assert result["status"] == "error"
            assert "Unknown strategy domain" in result["message"]

    def test_heal_method(self, agent):
        """Test heal method returns proper structure."""
        violation = {"type": "test", "file": "/path/to/file.py"}

        result = agent.heal(violation)

        assert "status" in result
        assert result["status"] == "skipped"
        assert "details" in result
        assert "artifacts" in result
        assert "errors" in result


class TestOrchestratorModes:
    """Tests for orchestrator mode handling."""

    def test_all_modes_valid(self):
        """Test all modes are valid enum values."""
        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorMode

        modes = ["healing", "compliance", "ssot", "full", "unified"]
        for mode in modes:
            assert OrchestratorMode(mode) is not None

    def test_invalid_mode_defaults_to_unified(self):
        """Test invalid mode defaults to unified."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L3_orchestration.OrchestratorAgent import (
                OrchestratorAgent,
                OrchestratorMode,
            )

            agent = OrchestratorAgent(mode="invalid_mode")
            assert agent.mode == OrchestratorMode.UNIFIED


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent

        assert OrchestratorAgent is not None

    def test_factory_function_exists(self):
        """Test factory function exists."""
        from agentic_core.L3_orchestration.OrchestratorAgent import (
            get_consolidated_orchestrator,
        )

        assert callable(get_consolidated_orchestrator)

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent

        assert issubclass(OrchestratorAgent, SovereignBaseAgent)

    def test_run_mission_signature(self):
        """Test run_mission has correct signature."""
        import inspect

        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent

        sig = inspect.signature(OrchestratorAgent.run_mission)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "agents" in params
        assert "dry_run" in params
        assert "execute" in params
        assert "context" in params

    def test_run_agent_signature(self):
        """Test run_agent has correct signature."""
        import inspect

        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent

        sig = inspect.signature(OrchestratorAgent.run_agent)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "agent_name" in params
        assert "dry_run" in params
        assert "context" in params

    def test_heal_repository_signature(self):
        """Test heal_repository has correct signature."""
        import inspect

        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent

        sig = inspect.signature(OrchestratorAgent.heal_repository)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "dry_run" in params
        assert "execute" in params

    def test_dispatch_signature(self):
        """Test dispatch has correct signature."""
        import inspect

        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent

        sig = inspect.signature(OrchestratorAgent.dispatch)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "domain" in params
        assert "action" in params
        assert "payload" in params

    def test_orchestrator_mode_enum(self):
        """Test OrchestratorMode enum exists."""
        from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorMode

        assert hasattr(OrchestratorMode, "HEALING")
        assert hasattr(OrchestratorMode, "COMPLIANCE")
        assert hasattr(OrchestratorMode, "SSOT")
        assert hasattr(OrchestratorMode, "FULL")
        assert hasattr(OrchestratorMode, "UNIFIED")


class TestInterfaceTypes:
    """Tests for interface type compatibility."""

    def test_agent_result_import(self):
        """Test AgentResult can be imported."""
        from agentic_core.L3_orchestration.types import AgentResult

        assert AgentResult is not None

    def test_mission_result_import(self):
        """Test MissionResult can be imported."""
        from agentic_core.L3_orchestration.types import MissionResult

        assert MissionResult is not None

    def test_execution_context_import(self):
        """Test ExecutionContext can be imported."""
        from agentic_core.L3_orchestration.types import ExecutionContext

        assert ExecutionContext is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
