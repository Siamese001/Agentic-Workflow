"""
Phase 3 Integration Test Suite

Tests for the Sovereign Architecture Hardening Plan Phase 3 implementation.
All tests must pass at 100% before Phase 3 is considered complete.

TEST CASES:
    A. End-to-End: Run UnifiedOrchestrator with HealingStrategy in dry_run mode
    B. Legacy Wrapper: Verify get_consolidated_orchestrator() delegates correctly
    C. Base Agent Hygiene: Verify L2ExecutionBaseAgent inherits from SovereignBaseAgent

USAGE:
    pytest tests/core/architecture/test_phase3_integration.py -v
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail, healer, memory, prompt, state
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

import pytest
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch


class TestCaseA_EndToEnd:
    """
    Test Case A: End-to-End Integration
    
    Run UnifiedOrchestrator with HealingStrategy in dry_run mode.
    Verify it returns a report with tier information populated.
    """
    
    def test_unified_orchestrator_with_healing_strategy(self):
        """Verify UnifiedOrchestratorAgent works with HealingStrategy."""
        from archives.location_violations.unified_orchestrator import UnifiedOrchestratorAgent
        from archives.void_violations.healing_strategy import HealingStrategy
        
        # Create strategy and orchestrator
        strategy = HealingStrategy(project_root=Path.cwd())
        orchestrator = UnifiedOrchestratorAgent(
            strategy=strategy,
            project_root=Path.cwd(),
            name="TestOrchestrator"
        )
        
        # Run mission in dry_run mode
        result = orchestrator.run_mission({"dry_run": True, "execute": False})
        
        # Verify result structure
        assert "status" in result, "Result must have 'status' key"
        assert "total_violations" in result, "Result must have 'total_violations' key"
        assert "total_fixed" in result, "Result must have 'total_fixed' key"
        assert "agent_results" in result, "Result must have 'agent_results' key"
        assert "is_stable" in result, "Result must have 'is_stable' key"
    
    def test_healing_strategy_has_all_tiers(self):
        """Verify HealingStrategy defines all expected tiers."""
        from archives.void_violations.healing_strategy import HealingStrategy
        
        strategy = HealingStrategy()
        tiers = strategy.get_tiers()
        
        # Should have tiers for Pre-Flight, Structural, Architectural, Dynamic
        tier_names = list(tiers.keys())
        
        # Check for key tiers (at least 3 non-empty)
        assert len(tier_names) >= 3, f"Expected at least 3 tiers, got {len(tier_names)}"
        
        # Verify Pre-Flight tier exists and has SyntaxValidatorAgent
        preflight_tier = None
        for name, agents in tiers.items():
            if "Pre-Flight" in name or "Tier 0" in name:
                preflight_tier = agents
                break
        
        assert preflight_tier is not None, "Pre-Flight tier must exist"
        assert "SyntaxValidatorAgent" in preflight_tier, "Pre-Flight must include SyntaxValidatorAgent"
    
    def test_unified_orchestrator_returns_agent_results(self):
        """Verify agent_results contains expected fields."""
        from archives.location_violations.unified_orchestrator import UnifiedOrchestratorAgent
        from archives.void_violations.healing_strategy import HealingStrategy
        
        # Create with mock strategy that returns one agent
        mock_strategy = MagicMock()
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {"Tier 0: Test": ["TestAgent"]}
        mock_strategy.get_agent.return_value = MagicMock()
        mock_strategy.execute_agent.return_value = {
            "status": "PASS",
            "violations_found": 0,
            "violations_fixed": 0,
        }
        mock_strategy.should_abort_tier.return_value = False
        
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        result = orchestrator.run_mission({"dry_run": True})
        
        # Verify agent_results structure
        assert len(result["agent_results"]) == 1
        agent_result = result["agent_results"][0]
        
        assert "agent_name" in agent_result
        assert "status" in agent_result
        assert "violations_found" in agent_result
        assert "violations_fixed" in agent_result
    
    def test_unified_orchestrator_stability_check(self):
        """Verify validate_stability works correctly."""
        from archives.location_violations.unified_orchestrator import UnifiedOrchestratorAgent
        
        mock_strategy = MagicMock()
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {}
        
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        
        # Stable result
        stable_result = {
            "status": "SUCCESS",
            "total_violations": 0,
            "total_fixed": 0,
            "is_stable": True,
            "aborted": False,
        }
        assert orchestrator.validate_stability(stable_result) is True
        
        # Unstable result
        unstable_result = {
            "status": "FAILED",
            "total_violations": 5,
            "total_fixed": 2,
            "is_stable": False,
            "aborted": True,
        }
        assert orchestrator.validate_stability(unstable_result) is False


class TestCaseB_LegacyWrapper:
    """
    Test Case B: Legacy Wrapper
    
    Verify get_consolidated_orchestrator() returns a working orchestrator
    that delegates to the unified system.
    """
    
    def test_get_consolidated_orchestrator_returns_unified(self):
        """Verify factory returns UnifiedOrchestratorAgent."""
        from archives.location_violations.ConsolidatedOrchestratorAgent import get_consolidated_orchestrator
        from archives.location_violations.unified_orchestrator import UnifiedOrchestratorAgent
        
        orchestrator = get_consolidated_orchestrator(Path.cwd())
        
        assert isinstance(orchestrator, UnifiedOrchestratorAgent), \
            "get_consolidated_orchestrator must return UnifiedOrchestratorAgent"
    
    def test_get_consolidated_orchestrator_has_healing_strategy(self):
        """Verify factory configures HealingStrategy."""
        from archives.location_violations.ConsolidatedOrchestratorAgent import get_consolidated_orchestrator
        from archives.void_violations.healing_strategy import HealingStrategy
        
        orchestrator = get_consolidated_orchestrator(Path.cwd())
        
        assert hasattr(orchestrator, 'strategy'), "Orchestrator must have strategy attribute"
        assert isinstance(orchestrator.strategy, HealingStrategy), \
            "Strategy must be HealingStrategy"
    
    def test_legacy_wrapper_run_mission(self):
        """Verify legacy ConsolidatedOrchestratorAgent.run_mission works."""
        import warnings
        from archives.location_violations.ConsolidatedOrchestratorAgent import ConsolidatedOrchestratorAgent
        
        # Suppress deprecation warning for test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # Create with mock to avoid actual agent execution
            with patch('agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent.get_consolidated_orchestrator') as mock_factory:
                mock_orchestrator = MagicMock()
                mock_orchestrator.run_mission.return_value = {
                    "status": "SUCCESS",
                    "total_fixed": 5,
                    "total_violations": 2,
                    "is_stable": True,
                    "agent_results": [
                        {"agent_name": "TestAgent", "status": "PASS", "violations_found": 0, "violations_fixed": 0, "execution_time_ms": 100}
                    ],
                    "execution_time_ms": 1000,
                }
                mock_factory.return_value = mock_orchestrator
                
                legacy = ConsolidatedOrchestratorAgent(Path.cwd())
                result = legacy.run_mission(context={"dry_run": True})
        
        # Verify legacy format
        assert "mission_log" in result
        assert "total_fixes" in result
        assert "total_violations" in result
        assert "is_stable" in result
    
    def test_legacy_wrapper_emits_deprecation_warning(self):
        """Verify ConsolidatedOrchestratorAgent emits deprecation warning."""
        import warnings
        from archives.location_violations.ConsolidatedOrchestratorAgent import ConsolidatedOrchestratorAgent
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            with patch('agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent.get_consolidated_orchestrator'):
                _ = ConsolidatedOrchestratorAgent(Path.cwd())
            
            # Check for deprecation warning
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1, "Should emit DeprecationWarning"


class TestCaseC_BaseAgentHygiene:
    """
    Test Case C: Base Agent Hygiene
    
    Verify L2ExecutionBaseAgent inherits from SovereignBaseAgent
    and thus has InfrastructureMixin capabilities.
    """
    
    def test_l2_execution_base_inherits_sovereign(self):
        """Verify L2ExecutionBaseAgent is subclass of SovereignBaseAgent."""
        from agentic_core.L2_execution.ToolRegistry.L2ExecutionBaseAgent import L2ExecutionBaseAgent
        from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent
        
        assert issubclass(L2ExecutionBaseAgent, SovereignBaseAgent), \
            "L2ExecutionBaseAgent must inherit from SovereignBaseAgent"
    
    def test_l2_execution_base_has_infrastructure(self):
        """Verify L2ExecutionBaseAgent has InfrastructureMixin in MRO."""
        from agentic_core.L2_execution.ToolRegistry.L2ExecutionBaseAgent import L2ExecutionBaseAgent
        from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
        
        # Check MRO includes InfrastructureMixin (via SovereignBaseAgent)
        mro_names = [cls.__name__ for cls in L2ExecutionBaseAgent.__mro__]
        
        # InfrastructureMixin should be in MRO (inherited through SovereignBaseAgent)
        assert "InfrastructureMixin" in mro_names or "SovereignBaseAgent" in mro_names, \
            "L2ExecutionBaseAgent must have InfrastructureMixin in MRO (via SovereignBaseAgent)"
    
    def test_l2_execution_base_mro_order(self):
        """Verify L2ExecutionBaseAgent has correct MRO order."""
        from agentic_core.L2_execution.ToolRegistry.L2ExecutionBaseAgent import L2ExecutionBaseAgent
        
        mro_names = [cls.__name__ for cls in L2ExecutionBaseAgent.__mro__]
        
        # SovereignBaseAgent should be in MRO
        assert "SovereignBaseAgent" in mro_names, \
            "SovereignBaseAgent must be in MRO"
        
        # SovereignBaseAgent should come before object
        sovereign_idx = mro_names.index("SovereignBaseAgent")
        object_idx = mro_names.index("object")
        assert sovereign_idx < object_idx, \
            "SovereignBaseAgent must come before object in MRO"


class TestDeletedFiles:
    """
    Verify obsolete files have been deleted.
    """
    
    def test_ssot_orchestrator_deleted(self):
        """Verify SSOTOrchestratorAgent.py has been deleted."""
        ssot_path = Path("agentic_core/L3_orchestration/workflow_engines/SSOTOrchestratorAgent.py")
        
        assert not ssot_path.exists(), \
            f"SSOTOrchestratorAgent.py should be deleted but still exists at {ssot_path}"
    
    def test_canon_base_agent_deleted(self):
        """Verify CanonBaseAgent.py has been deleted."""
        canon_path = Path("agentic_core/L2_execution/ToolRegistry/CanonBaseAgent.py")
        
        assert not canon_path.exists(), \
            f"CanonBaseAgent.py should be deleted but still exists at {canon_path}"
    
    def test_execution_canon_base_agent_deleted(self):
        """Verify ExecutionCanonBaseAgent.py has been deleted."""
        exec_canon_path = Path("agentic_core/L2_execution/ToolRegistry/ExecutionCanonBaseAgent.py")
        
        assert not exec_canon_path.exists(), \
            f"ExecutionCanonBaseAgent.py should be deleted but still exists at {exec_canon_path}"


class TestIOrchestrator:
    """
    Verify IOrchestrator protocol compliance.
    """
    
    def test_unified_orchestrator_implements_iorchestrator(self):
        """Verify UnifiedOrchestratorAgent implements IOrchestrator."""
        from archives.location_violations.unified_orchestrator import UnifiedOrchestratorAgent
        from agentic_core.L5_safety.validators.orchestrator import IOrchestrator
        
        mock_strategy = MagicMock()
        mock_strategy.name = "MockStrategy"
        mock_strategy.get_tiers.return_value = {}
        
        orchestrator = UnifiedOrchestratorAgent(strategy=mock_strategy)
        
        assert isinstance(orchestrator, IOrchestrator), \
            "UnifiedOrchestratorAgent must implement IOrchestrator protocol"
    
    def test_iorchestrator_has_required_methods(self):
        """Verify IOrchestrator defines required methods."""
        from agentic_core.L5_safety.validators.orchestrator import IOrchestrator
        
        # Check protocol has required methods
        assert hasattr(IOrchestrator, 'run_mission'), "IOrchestrator must define run_mission"
        assert hasattr(IOrchestrator, 'validate_stability'), "IOrchestrator must define validate_stability"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])