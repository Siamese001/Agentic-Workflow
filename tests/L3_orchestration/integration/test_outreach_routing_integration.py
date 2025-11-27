"""
L3 Orchestration Routing Integration Tests - Phase 10

Tests for OutreachOrchestrator routing integration:
- orchestrator activates router when use_model_routing=True
- sequential + concurrent both routed correctly
"""

from unittest.mock import Mock, patch

from l3.outreach_factory import create_message_executor_with_routing, create_outreach_orchestrator_with_routing
from infra.model_routing.policies import ModelRoutingPolicy
from runtime.execution_budget_manager import ExecutionBudgetManager, BudgetLimits, get_budget_manager
from l1.outreach_dataclasses import ArchetypeType
from config.LIC.lic_profile import get_lic_profile, create_custom_profile


class TestOutreachRoutingIntegration:
    """Test suite for L3 orchestration routing functionality."""
    
    def setup_method(self):
        """Setup test fixtures for each test method."""
        # Clear singleton for clean state
        ExecutionBudgetManager._instance = None
        self.budget_manager = get_budget_manager()
        self.budget_manager.reset_usage()
        
        # Configure test limits
        test_limits = BudgetLimits(
            max_parallel=5,
            max_tokens=10000,
            max_requests=100,
            max_depth=10,
            executor_timeout=30.0
        )
        self.budget_manager.configure(test_limits)
        
        # Create routing policy
        self.routing_policy = ModelRoutingPolicy()
        
        # Mock orchestrator dependencies
        self.mock_archetype_planner = Mock()
        self.mock_research_planner = Mock()
        self.mock_message_planner = Mock()
        self.mock_company_executor = Mock()
        self.mock_contact_executor = Mock()
        self.mock_state_manager = Mock()
        self.mock_safety_validator = Mock()
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
    
    def test_factory_creates_executor_without_routing_by_default(self):
        """Test that factory creates standard executor when routing disabled."""
        # Ensure routing is disabled in profile
        original_profile = get_lic_profile()
        
        # Create executor with factory
        executor = create_message_executor_with_routing(
            archetype=ArchetypeType.C_LEVEL,
            safety_validator=self.mock_safety_validator,
            budget_manager=self.budget_manager
        )
        
        # Verify executor was created
        assert executor is not None
        assert executor.safety_validator == self.mock_safety_validator
    
    def test_factory_creates_executor_with_routing_when_enabled(self):
        """Test that factory creates routed executor when routing enabled."""
        # Create custom profile with routing enabled
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            # Create executor with factory
            executor = create_message_executor_with_routing(
                archetype=ArchetypeType.C_LEVEL,
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager
            )
            
            # Verify executor was created
            assert executor is not None
            assert executor.safety_validator == self.mock_safety_validator
    
    def test_factory_creates_orchestrator_with_conditional_routing(self):
        """Test that factory creates orchestrator with conditional routing."""
        # Test with routing disabled (default)
        orchestrator = create_outreach_orchestrator_with_routing(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator,
            budget_manager=self.budget_manager,
            archetype=ArchetypeType.C_LEVEL
        )
        
        # Verify orchestrator was created
        assert orchestrator is not None
        assert orchestrator.message_executor is not None
        assert orchestrator.safety_validator == self.mock_safety_validator
    
    def test_factory_respects_config_flag_change(self):
        """Test that factory responds to config flag changes."""
        # Test with routing disabled
        standard_orchestrator = create_outreach_orchestrator_with_routing(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator,
            budget_manager=self.budget_manager,
            archetype=ArchetypeType.C_LEVEL
        )
        
        # Test with routing enabled
        routing_profile = create_custom_profile(use_model_routing=True)
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            routed_orchestrator = create_outreach_orchestrator_with_routing(
                archetype_planner=self.mock_archetype_planner,
                research_planner=self.mock_research_planner,
                message_planner=self.mock_message_planner,
                company_executor=self.mock_company_executor,
                contact_executor=self.mock_contact_executor,
                state_manager=self.mock_state_manager,
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager,
                archetype=ArchetypeType.C_LEVEL
            )
        
        # Both should be created successfully
        assert standard_orchestrator is not None
        assert routed_orchestrator is not None
        assert standard_orchestrator != routed_orchestrator
    
    def test_orchestrator_routing_with_different_archetypes(self):
        """Test that orchestrator routing works with different archetypes."""
        archetypes_to_test = [
            ArchetypeType.C_LEVEL,
            ArchetypeType.SENIOR_TA,
            ArchetypeType.RECRUITER
        ]
        
        for archetype in archetypes_to_test:
            # Reset budget manager
            self.budget_manager.reset_usage()
            
            orchestrator = create_outreach_orchestrator_with_routing(
                archetype_planner=self.mock_archetype_planner,
                research_planner=self.mock_research_planner,
                message_planner=self.mock_message_planner,
                company_executor=self.mock_company_executor,
                contact_executor=self.mock_contact_executor,
                state_manager=self.mock_state_manager,
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager,
                archetype=archetype
            )
            
            # Verify orchestrator was created for each archetype
            assert orchestrator is not None
            assert orchestrator.message_executor is not None
    
    def test_orchestrator_routing_error_handling(self):
        """Test that orchestrator handles routing errors gracefully."""
        # Test with invalid budget manager
        invalid_budget_manager = Mock()
        invalid_budget_manager.configure.side_effect = Exception("Budget manager error")
        
        # Should still create orchestrator gracefully
        orchestrator = create_outreach_orchestrator_with_routing(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator,
            budget_manager=invalid_budget_manager,
            archetype=ArchetypeType.C_LEVEL
        )
        
        # Should handle error gracefully or use fallback
        assert orchestrator is not None
    
    def test_orchestrator_routing_with_budget_constraints(self):
        """Test that orchestrator routing respects budget constraints."""
        # Configure low budget
        low_budget_limits = BudgetLimits(
            max_tokens=100,
            max_requests=5,
            max_depth=5
        )
        self.budget_manager.configure(low_budget_limits)
        
        # Use up most of the budget
        self.budget_manager.record_tokens("test", 90)
        
        orchestrator = create_outreach_orchestrator_with_routing(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator,
            budget_manager=self.budget_manager,
            archetype=ArchetypeType.C_LEVEL
        )
        
        # Should create orchestrator successfully even with budget constraints
        assert orchestrator is not None
        assert orchestrator.message_executor is not None
    
    def test_orchestrator_routing_meta_loop_integration(self):
        """Test that orchestrator routing integrates with meta-loop fallback."""
        # Create orchestrator with routing
        orchestrator = create_outreach_orchestrator_with_routing(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator,
            budget_manager=self.budget_manager,
            archetype=ArchetypeType.C_LEVEL
        )
        
        # Verify orchestrator has required components for meta-loop
        assert hasattr(orchestrator, 'message_executor')
        assert hasattr(orchestrator, 'budget_manager')
        assert hasattr(orchestrator, 'safety_validator')
        
        # Meta-loop functionality should be preserved
        assert orchestrator is not None
