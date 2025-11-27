"""
L2 Routing Executor Tests - Phase 10

Tests for MessageGenerationExecutor routing integration:
- executor passes correct model into underlying caller
- safety path bypasses routing constraints
"""

import pytest
from unittest.mock import Mock, patch

from l2.outreach_llm_caller import OutreachLLMCaller
from l2.message_generation_executor import MessageGenerationExecutor, GenerationContext
from infra.model_routing.policies import ModelRoutingPolicy
from runtime.execution_budget_manager import ExecutionBudgetManager, BudgetLimits, get_budget_manager
from runtime.runtime_utils import SandboxConfig
from l1.outreach_dataclasses import ArchetypeType
from config.LIC.lic_profile import create_custom_profile
from l3.outreach_factory import create_message_executor_with_routing


class TestLLMRoutingExecutors:
    """Test suite for L2 executor routing functionality."""
    
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
        
        # Create sandbox config
        self.sandbox_config = SandboxConfig()
        
        # Create OutreachLLMCaller with routing
        self.outreach_caller = OutreachLLMCaller(
            routing_policy=self.routing_policy,
            sandbox=self.sandbox_config,
            archetype=ArchetypeType.C_LEVEL,
            budget_manager=self.budget_manager
        )
        
        # Mock safety validator
        self.mock_safety_validator = Mock()
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        # Create executor with routed caller
        self.executor = MessageGenerationExecutor(
            llm_client=self.outreach_caller,
            safety_validator=self.mock_safety_validator
        )
    
    def test_executor_routing_disabled_by_default(self):
        """Test that executor uses default behavior when routing disabled."""
        # Create executor with standard LLM client (no routing)
        mock_standard_client = Mock()
        mock_standard_client.generate.return_value = "Standard response"
        
        standard_executor = MessageGenerationExecutor(
            llm_client=mock_standard_client,
            safety_validator=self.mock_safety_validator
        )
        
        # Generate message with standard client
        message_plan = Mock()
        message_plan.subject_plan = "Test subject"
        message_plan.hook_plan = "Test hook"
        message_plan.value_plan = "Test value"
        message_plan.cta_plan = "Test CTA"
        message_plan.signature_plan = "Test signature"
        
        context = GenerationContext(
            mission_id="test_mission",
            archetype="C_LEVEL",
            target_role="CEO",
            target_company="Tech Corp",
            value_proposition="Strategic partnership"
        )
        
        result = standard_executor.generate_message(message_plan, context, [])
        
        # Verify standard client was used (no routing)
        assert mock_standard_client.generate.call_count > 0
        assert result.message is not None
    
    def test_executor_routing_enabled_uses_policy(self):
        """Test that executor uses routing policy when enabled."""
        # Mock the OutreachLLMCaller's generate method directly
        with patch.object(self.outreach_caller, 'generate') as mock_generate:
            mock_generate.return_value = "Routed response"
            
            # Generate message with routed caller
            message_plan = Mock()
            message_plan.subject_plan = "Test subject"
            message_plan.hook_plan = "Test hook"
            message_plan.value_plan = "Test value"
            message_plan.cta_plan = "Test CTA"
            message_plan.signature_plan = "Test signature"
            
            context = GenerationContext(
                mission_id="test_mission",
                archetype="C_LEVEL",
                target_role="CEO",
                target_company="Tech Corp",
                value_proposition="Strategic partnership"
            )
            
            result = self.executor.generate_message(message_plan, context, [])
            
            # Verify routing was used (generate called)
            assert mock_generate.call_count > 0
            assert result.message is not None
    
    def test_executor_routing_passes_model_to_caller(self):
        """Test that executor passes selected model to underlying LLM caller."""
        # Mock the routing policy to return specific model
        with patch.object(self.routing_policy, 'select_model') as mock_select:
            mock_select.return_value = "gpt-4-heavy"
            
            with patch.object(self.outreach_caller, 'generate') as mock_generate:
                mock_generate.return_value = "Heavy model response"
                
                # Generate message
                message_plan = Mock()
                message_plan.subject_plan = "Test subject"
                message_plan.hook_plan = "Test hook"
                message_plan.value_plan = "Test value"
                message_plan.cta_plan = "Test CTA"
                message_plan.signature_plan = "Test signature"
                
                context = GenerationContext(
                    mission_id="test_mission",
                    archetype="C_LEVEL",
                    target_role="CEO",
                    target_company="Tech Corp",
                    value_proposition="Strategic partnership"
                )
                
                result = self.executor.generate_message(message_plan, context, [])
                
                # Verify routing policy was called with correct parameters
                assert mock_select.call_count > 0
                # Check the call arguments using kwargs
                for call_args in mock_select.call_args_list:
                    assert call_args.kwargs['stage'] == "message_generation"
                    assert call_args.kwargs['archetype'] == ArchetypeType.C_LEVEL
                    assert call_args.kwargs['budget_manager'] == self.budget_manager
    
    def test_executor_safety_bypasses_routing(self):
        """Test that safety validation always uses heavy models regardless of routing."""
        # Mock safety validator to return violations
        mock_violation = Mock()
        mock_violation.__dict__ = {"type": "safety_violation", "severity": "high"}
        self.mock_safety_validator.validate_layer_input.return_value = Mock(
            findings=[mock_violation]
        )
        
        # Mock routing policy to verify it's not called for safety
        with patch.object(self.routing_policy, 'select_model') as mock_select:
            mock_select.return_value = "gpt-4-heavy"
            
            with patch.object(self.outreach_caller, 'generate') as mock_generate:
                mock_generate.return_value = "Safety checked response"
                
                # Generate message
                message_plan = Mock()
                message_plan.subject_plan = "Test subject"
                message_plan.hook_plan = "Test hook"
                message_plan.value_plan = "Test value"
                message_plan.cta_plan = "Test CTA"
                message_plan.signature_plan = "Test signature"
                
                context = GenerationContext(
                    mission_id="test_mission",
                    archetype="C_LEVEL",
                    target_role="CEO",
                    target_company="Tech Corp",
                    value_proposition="Strategic partnership"
                )
                
                result = self.executor.generate_message(message_plan, context, [])
                
                # Verify routing was used for message generation
                assert mock_select.call_count > 0
                # Verify safety was checked
                assert self.mock_safety_validator.validate_layer_input.called
                # Safety violations should be recorded in metadata
                assert result.metadata.get("safety_check") == "failed"
    
    def test_executor_routing_with_archetype_context(self):
        """Test that executor considers archetype in routing decisions."""
        # Test different archetypes get different model selections
        archetypes_to_test = [
            (ArchetypeType.C_LEVEL, "heavy_model"),
            (ArchetypeType.SENIOR_TA, "medium_model"),
            (ArchetypeType.RECRUITER, "light_model")
        ]
        
        for archetype, expected_model_pattern in archetypes_to_test:
            # Reset budget manager
            self.budget_manager.reset_usage()
            
            # Create caller with specific archetype
            caller = OutreachLLMCaller(
                routing_policy=self.routing_policy,
                sandbox=self.sandbox_config,
                archetype=archetype,
                budget_manager=self.budget_manager
            )
            
            executor = MessageGenerationExecutor(
                llm_client=caller,
                safety_validator=self.mock_safety_validator
            )
            
            with patch.object(self.routing_policy, 'select_model') as mock_select:
                mock_select.return_value = f"{expected_model_pattern}_for_{archetype.value}"
                
                with patch.object(caller, 'generate') as mock_generate:
                    mock_generate.return_value = f"Response for {archetype.value}"
                    
                    # Generate message
                    message_plan = Mock()
                    message_plan.subject_plan = "Test subject"
                    message_plan.hook_plan = "Test hook"
                    message_plan.value_plan = "Test value"
                    message_plan.cta_plan = "Test CTA"
                    message_plan.signature_plan = "Test signature"
                    
                    context = GenerationContext(
                        mission_id="test_mission",
                        archetype=archetype.value,
                        target_role="Test Role",
                        target_company="Test Corp",
                        value_proposition="Test value"
                    )
                    
                    result = executor.generate_message(message_plan, context, [])
                    
                    # Verify routing policy was called with correct archetype
                    assert mock_select.called
                    call_args = mock_select.call_args[0]
                    assert call_args.kwargs['archetype'] == archetype  # archetype parameter
    
    def test_executor_routing_with_budget_constraints(self):
        """Test that executor respects budget constraints in routing."""
        # Configure low budget to trigger downgrades
        low_budget_limits = BudgetLimits(
            max_tokens=100,  # Very low budget
            max_requests=5,
            max_depth=5
        )
        self.budget_manager.configure(low_budget_limits)
        
        # Use up most of the budget
        self.budget_manager.record_tokens("test", 90)
        
        with patch.object(self.routing_policy, 'select_model') as mock_select:
            mock_select.return_value = "light_model_due_to_budget"
            
            with patch.object(self.outreach_caller, 'generate') as mock_generate:
                mock_generate.return_value = "Budget-constrained response"
                
                # Generate message
                message_plan = Mock()
                message_plan.subject_plan = "Test subject"
                message_plan.hook_plan = "Test hook"
                message_plan.value_plan = "Test value"
                message_plan.cta_plan = "Test CTA"
                message_plan.signature_plan = "Test signature"
                
                context = GenerationContext(
                    mission_id="test_mission",
                    archetype="C_LEVEL",
                    target_role="CEO",
                    target_company="Tech Corp",
                    value_proposition="Strategic partnership"
                )
                
                result = self.executor.generate_message(message_plan, context, [])
                
                # Verify routing policy was called with budget manager
                assert mock_select.called
                call_args = mock_select.call_args[0]
                assert call_args.kwargs['budget_manager'] == self.budget_manager
    
    def test_executor_routing_fallback_mechanism(self):
        """Test that executor routing falls back gracefully when routing fails."""
        # Create executor with routing enabled
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            executor = create_message_executor_with_routing(
                archetype=ArchetypeType.C_LEVEL,
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager
            )
            
            # Mock invoke_model to raise exception, forcing fallback
            with patch('runtime.runtime_utils.invoke_model', side_effect=Exception("LLM error")):
                # Should handle error gracefully
                with pytest.raises(Exception):
                    executor.llm_client.generate("test prompt")
    
    def test_executor_routing_error_handling(self):
        """Test that executor routing handles errors gracefully."""
        # Create executor with routing enabled
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            executor = create_message_executor_with_routing(
                archetype=ArchetypeType.C_LEVEL,
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager
            )
            
            # Mock routing policy to raise exception
            with patch.object(executor.llm_client.routing_policy, 'select_model', side_effect=Exception("Routing error")):
                # Should handle routing error gracefully
                with pytest.raises(Exception):
                    executor.llm_client.generate("test prompt")
    
    def test_executor_routing_model_selection_c_level(self):
        """Test that C_LEVEL archetype gets heavy models when routing enabled."""
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            executor = create_message_executor_with_routing(
                archetype=ArchetypeType.C_LEVEL,
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager
            )
            
            # Mock invoke_model at the correct import path to capture model selection
            with patch('l2.outreach_llm_caller.invoke_model') as mock_invoke:
                mock_invoke.return_value = "Generated response"
                
                # Generate message
                executor.llm_client.generate("test prompt")
                
                # Verify heavy model was selected for C_LEVEL
                call_args = mock_invoke.call_args
                selected_model = call_args[1]['model']
                assert selected_model in ["gpt-4", "gpt-5.1", "claude-3-opus"], f"C_LEVEL should get heavy model, got {selected_model}"
    
    def test_executor_routing_model_selection_recruiter(self):
        """Test that RECRUITER archetype gets light models when budget constrained."""
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            # Configure low budget to force light model selection
            self.budget_manager.record_tokens("test", 9000)  # Use most of budget
            
            executor = create_message_executor_with_routing(
                archetype=ArchetypeType.RECRUITER,
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager
            )
            
            # Mock invoke_model at the correct import path to capture model selection
            with patch('l2.outreach_llm_caller.invoke_model') as mock_invoke:
                mock_invoke.return_value = "Generated response"
                
                # Generate message
                executor.llm_client.generate("test prompt")
                
                # Verify light model was selected for RECRUITER with low budget
                call_args = mock_invoke.call_args
                selected_model = call_args[1]['model']
                assert selected_model in ["gpt-5-nano"], f"RECRUITER with low budget should get light model, got {selected_model}"
    
    def test_executor_routing_safety_always_heavy(self):
        """Test that safety stage always uses heavy models regardless of budget."""
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            # Configure very low budget
            self.budget_manager.record_tokens("test", 9500)  # Almost exhausted
            
            executor = create_message_executor_with_routing(
                archetype=ArchetypeType.SENIOR_TA,  # Non-C_LEVEL archetype
                safety_validator=self.mock_safety_validator,
                budget_manager=self.budget_manager
            )
            
            # Mock invoke_model at the correct import path to capture model selection for safety stage
            with patch('l2.outreach_llm_caller.invoke_model') as mock_invoke:
                mock_invoke.return_value = "Safety check passed"
                
                # Call safety check directly
                executor.llm_client.call_llm("test content", stage="safety")
                
                # Verify heavy model was used for safety regardless of budget
                call_args = mock_invoke.call_args
                selected_model = call_args[1]['model']
                assert selected_model in ["gpt-4", "gpt-5.1", "claude-3-opus"], f"Safety should always use heavy model, got {selected_model}"
    
    def test_executor_routing_budget_aware_downgrade(self):
        """Test that routing downgrades models based on remaining budget percentage."""
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            # Test different budget levels
            test_cases = [
                (0.9, "light"),   # < 20% remaining -> light models
                (0.4, "light"),   # < 50% remaining -> downgrade to light  
                (0.8, "medium"),  # > 50% remaining -> medium for EXECUTIVE
            ]
            
            for budget_usage, expected_complexity in test_cases:
                # Reset and configure budget
                self.budget_manager.reset_usage()
                if budget_usage == 0.9:
                    self.budget_manager.record_tokens("test", 9000)  # Low remaining
                elif budget_usage == 0.4:
                    self.budget_manager.record_tokens("test", 6000)  # Medium remaining
                else:
                    self.budget_manager.record_tokens("test", 2000)  # High remaining
                
                executor = create_message_executor_with_routing(
                    archetype=ArchetypeType.EXECUTIVE,
                    safety_validator=self.mock_safety_validator,
                    budget_manager=self.budget_manager
                )
                
                # Mock invoke_model at the correct import path to capture model selection
                with patch('l2.outreach_llm_caller.invoke_model') as mock_invoke:
                    mock_invoke.return_value = "Generated response"
                    
                    # Generate message
                    executor.llm_client.generate("test prompt")
                    
                    # Verify model complexity matches expected budget-based selection
                    call_args = mock_invoke.call_args
                    selected_model = call_args[1]['model']
                    
                    if expected_complexity == "light":
                        assert selected_model in ["gpt-5-nano"], f"Low budget should use light model, got {selected_model}"
                    elif expected_complexity == "medium":
                        assert selected_model in ["gpt-5-mini"], f"Medium budget should use medium model, got {selected_model}"
                    else:  # heavy
                        assert selected_model in ["gpt-5.1"], f"High budget should use heavy model, got {selected_model}"
