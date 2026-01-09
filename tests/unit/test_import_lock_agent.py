#!/usr/bin/env python3
"""
Unit Tests for ImportLockAgent

Comprehensive unit tests covering all aspects of the runtime import lock.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from types import ModuleType

from agentic_core.L5_safety.guardrails.ImportLockAgent import (
    ImportLockAgent,
    SovereigntyError,
    engage_global_lock,
    disengage_global_lock
)


class TestImportLockAgentBasics:
    """Basic functionality tests for ImportLockAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create an ImportLockAgent instance."""
        return ImportLockAgent()
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Ensure agent is disengaged after each test."""
        yield
        # Cleanup: remove any lingering hooks
        for finder in list(sys.meta_path):
            if isinstance(finder, ImportLockAgent):
                sys.meta_path.remove(finder)
    
    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.enabled is False
        assert agent.violations_caught == []
        assert len(agent._intentional_exceptions) > 0
        assert len(agent._always_allowed) > 0
    
    def test_engage_lock(self, agent):
        """Test engaging the import lock."""
        result = agent.engage_lock()
        
        assert result is True
        assert agent.enabled is True
        assert agent in sys.meta_path
        
        # Cleanup
        agent.disengage_lock()
    
    def test_engage_lock_already_engaged(self, agent):
        """Test engaging when already engaged."""
        agent.engage_lock()
        result = agent.engage_lock()
        
        assert result is False
        assert agent.enabled is True
        
        # Cleanup
        agent.disengage_lock()
    
    def test_disengage_lock(self, agent):
        """Test disengaging the import lock."""
        agent.engage_lock()
        result = agent.disengage_lock()
        
        assert result is True
        assert agent.enabled is False
        assert agent not in sys.meta_path
    
    def test_disengage_lock_not_engaged(self, agent):
        """Test disengaging when not engaged."""
        result = agent.disengage_lock()
        assert result is False
    
    def test_get_layer_rank_valid_layers(self, agent):
        """Test extracting layer ranks from module names."""
        assert agent._get_layer_rank("agentic_core.L0_maintenance.scripts.X") == 0
        assert agent._get_layer_rank("agentic_core.L1_cognition.thought_engine.Y") == 1
        assert agent._get_layer_rank("agentic_core.L2_execution.ToolRegistry.Z") == 2
        assert agent._get_layer_rank("agentic_core.L3_orchestration.workflow_engines.W") == 3
        assert agent._get_layer_rank("agentic_core.L4_state.ValidationContext.V") == 4
        assert agent._get_layer_rank("agentic_core.L5_safety.guardrails.U") == 5
    
    def test_get_layer_rank_utils(self, agent):
        """Test that utils is treated as L0."""
        assert agent._get_layer_rank("agentic_core.utils.core_extensions.X") == 0
    
    def test_get_layer_rank_config(self, agent):
        """Test that config is treated as L0."""
        assert agent._get_layer_rank("agentic_core.config.blueprint.X") == 0
    
    def test_get_layer_rank_invalid(self, agent):
        """Test that non-layered modules raise ValueError."""
        with pytest.raises(ValueError):
            agent._get_layer_rank("some.random.module")
    
    def test_is_intentional_exception(self, agent):
        """Test checking for intentional exceptions."""
        assert agent._is_intentional_exception(
            "agentic_core.L3_orchestration.workflow_engines.NervousSystemAgent"
        ) is True
        
        assert agent._is_intentional_exception(
            "agentic_core.L3_orchestration.workflow_engines.OrchestrationBaseAgent"
        ) is True
        
        assert agent._is_intentional_exception(
            "agentic_core.L2_execution.ToolRegistry.SomeAgent"
        ) is False
    
    def test_is_always_allowed(self, agent):
        """Test checking for always-allowed modules."""
        assert agent._is_always_allowed("agentic_core.utils.core_extensions.X") is True
        assert agent._is_always_allowed("agentic_core.config.blueprint.Y") is True
        assert agent._is_always_allowed("agentic_core.L5_safety.guardrails.Z") is False
    
    def test_get_violations_report_empty(self, agent):
        """Test violations report when no violations."""
        report = agent.get_violations_report()
        assert "No violations caught" in report
    
    def test_get_violations_report_with_violations(self, agent):
        """Test violations report with violations."""
        agent.violations_caught = [
            {
                "caller": "agentic_core.L0_maintenance.X",
                "caller_layer": 0,
                "target": "agentic_core.L5_safety.Y",
                "target_layer": 5
            }
        ]
        
        report = agent.get_violations_report()
        assert "Total violations caught: 1" in report
        assert "L0" in report
        assert "L5" in report


class TestImportLockAgentFindSpec:
    """Tests for the find_spec method (import interception)."""
    
    @pytest.fixture
    def agent(self):
        """Create an ImportLockAgent instance."""
        agent = ImportLockAgent()
        agent.engage_lock()
        yield agent
        agent.disengage_lock()
    
    def test_find_spec_non_agentic_core(self, agent):
        """Test that non-agentic_core imports are ignored."""
        result = agent.find_spec("os", None, None)
        assert result is None
        
        result = agent.find_spec("sys", None, None)
        assert result is None
    
    def test_find_spec_utils_always_allowed(self, agent):
        """Test that utils imports are always allowed."""
        result = agent.find_spec("agentic_core.utils.core_extensions.X", None, None)
        assert result is None  # None means allow import
    
    def test_find_spec_config_always_allowed(self, agent):
        """Test that config imports are always allowed."""
        result = agent.find_spec("agentic_core.config.blueprint.X", None, None)
        assert result is None
    
    @patch('agentic_core.L5_safety.guardrails.ImportLockAgent.ImportLockAgent._get_caller_module')
    def test_find_spec_no_caller(self, mock_get_caller, agent):
        """Test behavior when caller cannot be determined."""
        mock_get_caller.return_value = None
        
        result = agent.find_spec("agentic_core.L5_safety.X", None, None)
        assert result is None
    
    @patch('agentic_core.L5_safety.guardrails.ImportLockAgent.ImportLockAgent._get_caller_module')
    def test_find_spec_same_layer(self, mock_get_caller, agent):
        """Test that same-layer imports are allowed."""
        mock_caller = Mock()
        mock_caller.__name__ = "agentic_core.L2_execution.ToolRegistry.A"
        mock_get_caller.return_value = mock_caller
        
        # L2 -> L2 should be allowed
        result = agent.find_spec("agentic_core.L2_execution.ToolRegistry.B", None, None)
        assert result is None
    
    @patch('agentic_core.L5_safety.guardrails.ImportLockAgent.ImportLockAgent._get_caller_module')
    def test_find_spec_downward_import(self, mock_get_caller, agent):
        """Test that downward imports are allowed."""
        mock_caller = Mock()
        mock_caller.__name__ = "agentic_core.L5_safety.guardrails.A"
        mock_get_caller.return_value = mock_caller
        
        # L5 -> L2 should be allowed (downward)
        result = agent.find_spec("agentic_core.L2_execution.ToolRegistry.B", None, None)
        assert result is None
    
    @patch('agentic_core.L5_safety.guardrails.ImportLockAgent.ImportLockAgent._get_caller_module')
    def test_find_spec_upward_violation(self, mock_get_caller, agent):
        """Test that upward imports raise SovereigntyError."""
        mock_caller = Mock()
        mock_caller.__name__ = "agentic_core.L0_maintenance.scripts.bad"
        mock_get_caller.return_value = mock_caller
        
        # L0 -> L5 should raise error (upward)
        with pytest.raises(SovereigntyError) as exc_info:
            agent.find_spec("agentic_core.L5_safety.guardrails.X", None, None)
        
        assert "RUNTIME GRAVITY VIOLATION" in str(exc_info.value)
        assert "L0" in str(exc_info.value)
        assert "L5" in str(exc_info.value)
        assert len(agent.violations_caught) == 1
    
    @patch('agentic_core.L5_safety.guardrails.ImportLockAgent.ImportLockAgent._get_caller_module')
    def test_find_spec_intentional_exception(self, mock_get_caller, agent):
        """Test that intentional exceptions are allowed."""
        mock_caller = Mock()
        mock_caller.__name__ = "agentic_core.L3_orchestration.workflow_engines.NervousSystemAgent"
        mock_get_caller.return_value = mock_caller
        
        # This is an intentional exception, should be allowed
        result = agent.find_spec("agentic_core.L5_safety.validators.LocationAgent", None, None)
        assert result is None


class TestImportLockAgentGlobalFunctions:
    """Tests for global convenience functions."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Cleanup global lock after each test."""
        yield
        disengage_global_lock()
        # Also clean up any lingering hooks
        for finder in list(sys.meta_path):
            if isinstance(finder, ImportLockAgent):
                sys.meta_path.remove(finder)
    
    def test_engage_global_lock(self):
        """Test engaging the global lock."""
        lock = engage_global_lock()
        
        assert lock is not None
        assert lock.enabled is True
        assert lock in sys.meta_path
    
    def test_engage_global_lock_idempotent(self):
        """Test that engaging global lock multiple times is safe."""
        lock1 = engage_global_lock()
        lock2 = engage_global_lock()
        
        assert lock1 is lock2
        assert lock1.enabled is True
    
    def test_disengage_global_lock(self):
        """Test disengaging the global lock."""
        engage_global_lock()
        result = disengage_global_lock()
        
        assert result is True
    
    def test_disengage_global_lock_not_engaged(self):
        """Test disengaging when not engaged."""
        result = disengage_global_lock()
        assert result is False


class TestImportLockAgentEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.fixture
    def agent(self):
        """Create an ImportLockAgent instance."""
        return ImportLockAgent()
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Cleanup after each test."""
        yield
        for finder in list(sys.meta_path):
            if isinstance(finder, ImportLockAgent):
                sys.meta_path.remove(finder)
    
    def test_multiple_agents_in_meta_path(self, agent):
        """Test behavior with multiple agents."""
        agent1 = ImportLockAgent()
        agent2 = ImportLockAgent()
        
        agent1.engage_lock()
        agent2.engage_lock()
        
        assert agent1 in sys.meta_path
        assert agent2 in sys.meta_path
        
        agent1.disengage_lock()
        agent2.disengage_lock()
    
    @patch('agentic_core.L5_safety.guardrails.ImportLockAgent.inspect.stack')
    def test_get_caller_module_exception_handling(self, mock_stack, agent):
        """Test that _get_caller_module handles exceptions gracefully."""
        mock_stack.side_effect = Exception("Stack error")
        
        result = agent._get_caller_module()
        assert result is None
    
    @patch('agentic_core.L5_safety.guardrails.ImportLockAgent.ImportLockAgent._get_caller_module')
    def test_find_spec_non_layered_module(self, mock_get_caller, agent):
        """Test handling of non-layered agentic_core modules."""
        agent.engage_lock()
        
        mock_caller = Mock()
        mock_caller.__name__ = "agentic_core.some_random_module"
        mock_get_caller.return_value = mock_caller
        
        # Should not raise, just return None
        result = agent.find_spec("agentic_core.another_random_module", None, None)
        assert result is None
        
        agent.disengage_lock()
    
    def test_sovereignty_error_inheritance(self):
        """Test that SovereigntyError is an ImportError."""
        error = SovereigntyError("test")
        assert isinstance(error, ImportError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
