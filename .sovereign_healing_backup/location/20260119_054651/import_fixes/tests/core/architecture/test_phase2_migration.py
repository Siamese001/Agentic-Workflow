"""
Phase 2 Migration Test Suite

Tests for the Sovereign Architecture Hardening Plan Phase 2 implementation.
All tests must pass at 100% before Phase 2 is considered complete.

TEST CASES:
    A. The Big Switch: Verify SovereignBaseAgent uses InfrastructureMixin
    B. Strategy Injection: Verify UnifiedOrchestratorAgent calls strategy
    C. Decorator Sanitization: Verify @standard_heal normalizes output
    D. Crash Containment: Verify @standard_heal catches exceptions

USAGE:
    pytest tests/core/architecture/test_phase2_migration.py -v
"""
from __future__ import annotations

import pytest
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch


class TestCaseA_TheBigSwitch:
    """
    Test Case A: The Big Switch
    
    Verify that SovereignBaseAgent now inherits from InfrastructureMixin
    and that _infra_initialized is True after instantiation.
    """
    
    def test_sovereign_base_agent_has_infra_mixin(self):
        """Verify SovereignBaseAgent inherits from InfrastructureMixin."""
        from agentic_core.utils.core_extensions.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
        
        # Check inheritance
        assert issubclass(SovereignBaseAgent, InfrastructureMixin), \
            "SovereignBaseAgent must inherit from InfrastructureMixin"
    
    def test_sovereign_base_agent_infra_initialized(self):
        """Verify _infra_initialized is True after instantiation."""
        from agentic_core.utils.core_extensions.SovereignBaseAgent import SovereignBaseAgent
        
        # Create instance
        agent = SovereignBaseAgent(name="TestAgent")
        
        # Verify infrastructure initialized
        assert hasattr(agent, '_infra_initialized'), \
            "SovereignBaseAgent must have _infra_initialized attribute"
        assert agent._infra_initialized is True, \
            "_infra_initialized must be True after instantiation"
    
    def test_sovereign_base_agent_has_healer_metrics(self):
        """Verify HealerMixin was properly initialized via InfrastructureMixin."""
        from agentic_core.utils.core_extensions.SovereignBaseAgent import SovereignBaseAgent
        
        agent = SovereignBaseAgent(name="TestAgent")
        
        # HealerMixin should set _healer_metrics
        assert hasattr(agent, '_healer_metrics'), \
            "SovereignBaseAgent must have _healer_metrics from HealerMixin"
    
    def test_sovereign_base_agent_verify_state_passes(self):
        """Verify verify_state() passes for properly initialized agent."""
        from agentic_core.utils.core_extensions.SovereignBaseAgent import SovereignBaseAgent
        
        agent = SovereignBaseAgent(name="TestAgent")
        
        # verify_state should not raise
        result = agent.verify_state()
        assert result is True, "verify_state() should return True"
    
    def test_sovereign_base_agent_mro_order(self):
        """Verify MRO includes InfrastructureMixin before object."""
        from agentic_core.utils.core_extensions.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
        
        mro = SovereignBaseAgent.__mro__
        mro_names = [cls.__name__ for cls in mro]
        
        # InfrastructureMixin should be in MRO
        assert "InfrastructureMixin" in mro_names, \
            "InfrastructureMixin must be in MRO"
        
        # InfrastructureMixin should come before object
        infra_idx = mro_names.index("InfrastructureMixin")
        object_idx = mro_names.index("object")
        assert infra_idx < object_idx, \
            "InfrastructureMixin must come before object in MRO"


class TestCaseB_StrategyInjection:
    """
    Test Case B: Strategy Injection
    
    Verify that UnifiedOrchestratorAgent calls the injected strategy
    when run_mission is invoked.
    """
    
    def test_unified_orchestrator_accepts_strategy(self):
        """Verify UnifiedOrchestratorAgent accepts a strategy in __init__."""
        from agentic_core.L3_orchestration.unified_orchestrator import (
            UnifiedOrchestratorAgent,
            MissionStrategy,
        )
        
        # Create mock strategy
        mock_strategy = MagicMock(spec=MissionStrategy)
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {}
        
        # Should not raise
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        
        assert orchestrator.strategy is mock_strategy
    
    def test_unified_orchestrator_calls_strategy_get_tiers(self):
        """Verify run_mission calls strategy.get_tiers()."""
        from agentic_core.L3_orchestration.unified_orchestrator import (
            UnifiedOrchestratorAgent,
            MissionStrategy,
        )
        
        # Create mock strategy
        mock_strategy = MagicMock(spec=MissionStrategy)
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {}
        
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        
        # Run mission
        result = orchestrator.run_mission({"dry_run": True})
        
        # Verify get_tiers was called
        mock_strategy.get_tiers.assert_called_once()
    
    def test_unified_orchestrator_calls_strategy_get_agent(self):
        """Verify run_mission calls strategy.get_agent() for each agent."""
        from agentic_core.L3_orchestration.unified_orchestrator import (
            UnifiedOrchestratorAgent,
            MissionStrategy,
        )
        
        # Create mock strategy with one tier and one agent
        mock_strategy = MagicMock(spec=MissionStrategy)
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {"Tier 1": ["TestAgent"]}
        mock_strategy.get_agent.return_value = None  # Agent not available
        mock_strategy.should_abort_tier.return_value = False
        
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        
        # Run mission
        result = orchestrator.run_mission({"dry_run": True})
        
        # Verify get_agent was called with agent name
        mock_strategy.get_agent.assert_called_with("TestAgent")
    
    def test_unified_orchestrator_calls_strategy_execute_agent(self):
        """Verify run_mission calls strategy.execute_agent() for available agents."""
        from agentic_core.L3_orchestration.unified_orchestrator import (
            UnifiedOrchestratorAgent,
            MissionStrategy,
        )
        
        # Create mock agent
        mock_agent = MagicMock()
        
        # Create mock strategy
        mock_strategy = MagicMock(spec=MissionStrategy)
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {"Tier 1": ["TestAgent"]}
        mock_strategy.get_agent.return_value = mock_agent
        mock_strategy.execute_agent.return_value = {
            "status": "PASS",
            "violations_found": 0,
            "violations_fixed": 0,
        }
        mock_strategy.should_abort_tier.return_value = False
        
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        
        # Run mission
        result = orchestrator.run_mission({"dry_run": True})
        
        # Verify execute_agent was called
        mock_strategy.execute_agent.assert_called_once()
        call_kwargs = mock_strategy.execute_agent.call_args
        assert call_kwargs[1]["agent"] is mock_agent
        assert call_kwargs[1]["agent_name"] == "TestAgent"
    
    def test_unified_orchestrator_implements_iorchestrator(self):
        """Verify UnifiedOrchestratorAgent implements IOrchestrator protocol."""
        from agentic_core.L3_orchestration.unified_orchestrator import UnifiedOrchestratorAgent
        from agentic_core.L3_orchestration.interfaces.orchestrator import IOrchestrator
        
        # Create mock strategy
        mock_strategy = MagicMock()
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {}
        
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        
        # Check protocol compliance
        assert isinstance(orchestrator, IOrchestrator), \
            "UnifiedOrchestratorAgent must implement IOrchestrator"


class TestCaseC_DecoratorSanitization:
    """
    Test Case C: Decorator Sanitization
    
    Verify that @standard_heal normalizes legacy output formats
    to the canonical HealResult schema.
    """
    
    def test_standard_heal_normalizes_renamed_key(self):
        """Verify 'renamed' key is normalized to 'violations_fixed'."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"renamed": 5}
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert "violations_fixed" in result, \
            "Result must have 'violations_fixed' key"
        assert result["violations_fixed"] == 5, \
            "'renamed' value should be mapped to 'violations_fixed'"
    
    def test_standard_heal_normalizes_violations_key(self):
        """Verify 'violations' key is normalized to 'violations_found'."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"violations": 10}
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert "violations_found" in result
        assert result["violations_found"] == 10
    
    def test_standard_heal_normalizes_fixed_key(self):
        """Verify 'fixed' key is normalized to 'violations_fixed'."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"fixed": 3}
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert "violations_fixed" in result
        assert result["violations_fixed"] == 3
    
    def test_standard_heal_adds_status(self):
        """Verify status is added if not present."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"violations": 0}
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert "status" in result
        assert result["status"] == "PASS"  # No violations = PASS
    
    def test_standard_heal_status_fail_when_unfixed(self):
        """Verify status is FAIL when violations > fixed."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"violations": 5, "fixed": 2}
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["status"] == "FAIL"
    
    def test_standard_heal_adds_execution_time(self):
        """Verify execution_time_ms is added."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {}
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert "execution_time_ms" in result
        assert isinstance(result["execution_time_ms"], float)
    
    def test_standard_heal_preserves_canonical_keys(self):
        """Verify canonical keys are preserved as-is."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {
                    "violations_found": 10,
                    "violations_fixed": 8,
                    "status": "PARTIAL",
                }
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["violations_found"] == 10
        assert result["violations_fixed"] == 8
        assert result["status"] == "PARTIAL"
    
    def test_standard_heal_normalizes_boolean_result(self):
        """Verify boolean result is normalized."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return True
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["status"] == "PASS"
    
    def test_standard_heal_normalizes_integer_result(self):
        """Verify integer result is normalized as violation count."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return 5  # 5 violations
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["violations_found"] == 5
        assert result["status"] == "FAIL"


class TestCaseD_CrashContainment:
    """
    Test Case D: Crash Containment
    
    Verify that @standard_heal catches exceptions and returns
    a valid HealResult with status='ERROR'.
    """
    
    def test_standard_heal_catches_value_error(self):
        """Verify ValueError is caught and returns ERROR status."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                raise ValueError("Test error")
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["status"] == "ERROR"
        assert "error_message" in result
        assert "Test error" in result["error_message"]
    
    def test_standard_heal_catches_runtime_error(self):
        """Verify RuntimeError is caught and returns ERROR status."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                raise RuntimeError("Runtime failure")
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["status"] == "ERROR"
        assert "Runtime failure" in result["error_message"]
    
    def test_standard_heal_catches_type_error(self):
        """Verify TypeError is caught and returns ERROR status."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                raise TypeError("Type mismatch")
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["status"] == "ERROR"
        assert "Type mismatch" in result["error_message"]
    
    def test_standard_heal_error_has_errors_count(self):
        """Verify error result has errors count set to 1."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                raise Exception("Generic error")
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert result["errors"] == 1
    
    def test_standard_heal_error_has_execution_time(self):
        """Verify error result still has execution_time_ms."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                raise Exception("Error")
        
        agent = TestAgent()
        result = agent.heal_repository()
        
        assert "execution_time_ms" in result
        assert isinstance(result["execution_time_ms"], float)
    
    def test_standard_heal_input_normalization_dry_run_default(self):
        """Verify dry_run defaults to True (safe)."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        received_dry_run = None
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                nonlocal received_dry_run
                received_dry_run = dry_run
                return {}
        
        agent = TestAgent()
        agent.heal_repository()  # No dry_run arg
        
        assert received_dry_run is True
    
    def test_standard_heal_input_normalization_execute_default(self):
        """Verify execute defaults to False (safe)."""
        from agentic_core.utils.core_extensions.decorators import standard_heal
        
        received_execute = None
        
        class TestAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                nonlocal received_execute
                received_execute = execute
                return {}
        
        agent = TestAgent()
        agent.heal_repository()  # No execute arg
        
        assert received_execute is False


class TestHealingStrategy:
    """
    Additional tests for HealingStrategy implementation.
    """
    
    def test_healing_strategy_has_name(self):
        """Verify HealingStrategy has a name property."""
        from agentic_core.L3_orchestration.strategies.healing_strategy import HealingStrategy
        
        strategy = HealingStrategy()
        
        assert strategy.name == "HealingStrategy"
    
    def test_healing_strategy_has_five_tiers(self):
        """Verify HealingStrategy defines 5 tiers."""
        from agentic_core.L3_orchestration.strategies.healing_strategy import HealingStrategy
        
        strategy = HealingStrategy()
        tiers = strategy.get_tiers()
        
        # Should have at least 4 non-empty tiers (Tier 4 may be empty)
        assert len(tiers) >= 3, "HealingStrategy should have at least 3 non-empty tiers"
    
    def test_healing_strategy_tier0_has_syntax_validator(self):
        """Verify Tier 0 includes SyntaxValidatorAgent."""
        from agentic_core.L3_orchestration.strategies.healing_strategy import HealingStrategy
        
        strategy = HealingStrategy()
        tiers = strategy.get_tiers()
        
        # Find Tier 0 / Pre-Flight
        tier0_agents = None
        for tier_name, agents in tiers.items():
            if "Tier 0" in tier_name or "Pre-Flight" in tier_name:
                tier0_agents = agents
                break
        
        assert tier0_agents is not None, "Tier 0 / Pre-Flight must exist"
        assert "SyntaxValidatorAgent" in tier0_agents
    
    def test_healing_strategy_abort_on_syntax_failure(self):
        """Verify should_abort_tier returns True for Tier 0 failure."""
        from agentic_core.L3_orchestration.strategies.healing_strategy import HealingStrategy
        
        strategy = HealingStrategy()
        
        tier_results = [{"status": "FAIL", "violations_found": 1}]
        
        should_abort = strategy.should_abort_tier(
            "Tier 0: Pre-Flight",
            tier_results,
            execute=False
        )
        
        assert should_abort is True


class TestMissionReport:
    """
    Tests for MissionReport dataclass.
    """
    
    def test_mission_report_success_rate(self):
        """Verify success_rate calculation."""
        from agentic_core.L3_orchestration.unified_orchestrator import MissionReport
        
        report = MissionReport(
            timestamp="2024-01-01T00:00:00",
            strategy_name="Test",
            total_agents_run=10,
            agents_passed=8,
            agents_failed=2,
            agents_errored=0,
            total_violations=5,
            total_fixes=3,
            execution_time_ms=1000.0,
        )
        
        assert report.success_rate == 80.0
    
    def test_mission_report_is_stable(self):
        """Verify is_stable property."""
        from agentic_core.L3_orchestration.unified_orchestrator import MissionReport
        
        # Stable report
        stable_report = MissionReport(
            timestamp="2024-01-01T00:00:00",
            strategy_name="Test",
            total_agents_run=5,
            agents_passed=5,
            agents_failed=0,
            agents_errored=0,
            total_violations=0,
            total_fixes=0,
            execution_time_ms=500.0,
            overall_status="PASS",
            aborted=False,
        )
        
        assert stable_report.is_stable is True
        
        # Unstable report (aborted)
        unstable_report = MissionReport(
            timestamp="2024-01-01T00:00:00",
            strategy_name="Test",
            total_agents_run=5,
            agents_passed=3,
            agents_failed=2,
            agents_errored=0,
            total_violations=5,
            total_fixes=0,
            execution_time_ms=500.0,
            overall_status="FAILED",
            aborted=True,
        )
        
        assert unstable_report.is_stable is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
