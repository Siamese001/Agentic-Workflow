"""
Budget constraint tests for model routing policy.

Tests that model selection respects budget constraints and downgrades
models appropriately when budget is limited.
"""

import pytest
from unittest.mock import Mock

from infra.model_routing.policies import ModelRoutingPolicy
from l1.outreach_dataclasses import ArchetypeType
from runtime.execution_budget_manager import ExecutionBudgetManager, BudgetLimits


class TestRoutingPolicyBudgetConstraints:
    """Test suite for budget-aware model routing behavior."""
    
    def setup_method(self):
        """Setup test environment with routing policy."""
        self.routing_policy = ModelRoutingPolicy()
    
    def create_budget_manager(self, tokens_remaining: int, tokens_total: int) -> Mock:
        """Create mock budget manager with specified token usage."""
        mock_budget_manager = Mock(spec=ExecutionBudgetManager)
        mock_budget_manager.current_usage.return_value = {
            "tokens_remaining": tokens_remaining,
            "tokens_used": tokens_total - tokens_remaining,
            "requests_remaining": 100,
            "requests_used": 0,
            "budget_exceeded": {
                "tokens": tokens_remaining < 100,
                "requests": False,
                "depth": False,
                "concurrent": False
            }
        }
        return mock_budget_manager
    
    def test_budget_forces_cheaper_model_when_low(self):
        """Test that low budget forces cheaper model selection."""
        # Simulate low budget: 10% tokens remaining
        budget_manager = self.create_budget_manager(tokens_remaining=100, tokens_total=1000)
        
        # C-Level normally gets heavy models, but with low budget should get light
        selected_model = self.routing_policy.select_model(
            stage="message_generation",
            archetype=ArchetypeType.C_LEVEL,
            budget_manager=budget_manager
        )
        
        # Should downgrade to light model when budget is low
        assert selected_model in [
            "gpt-5-nano",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-flash-lite"
        ], f"Expected light model for C-Level with low budget, got {selected_model}"
    
    def test_budget_forces_medium_model_when_medium(self):
        """Test that medium budget forces medium model selection."""
        # Simulate medium budget: 30% tokens remaining
        budget_manager = self.create_budget_manager(tokens_remaining=300, tokens_total=1000)
        
        # C-Level normally gets heavy models, but with medium budget should get medium
        selected_model = self.routing_policy.select_model(
            stage="message_generation",
            archetype=ArchetypeType.C_LEVEL,
            budget_manager=budget_manager
        )
        
        # Should downgrade to medium model when budget is medium
        assert selected_model in [
            "gpt-5-mini",
            "claude-sonnet-4-5-20250929",
            "gemini-2.5-flash"
        ], f"Expected medium model for C-Level with medium budget, got {selected_model}"
    
    def test_unlimited_budget_allows_heavy_models(self):
        """Test that unlimited budget allows heavy model selection."""
        # Simulate unlimited budget: 80% tokens remaining
        budget_manager = self.create_budget_manager(tokens_remaining=800, tokens_total=1000)
        
        # C-Level should get heavy models with good budget
        selected_model = self.routing_policy.select_model(
            stage="message_generation",
            archetype=ArchetypeType.C_LEVEL,
            budget_manager=budget_manager
        )
        
        # Should get heavy model when budget is good
        assert selected_model in [
            "gpt-5.1",
            "claude-opus-4-1-20250805",
            "gemini-3-pro-preview"
        ], f"Expected heavy model for C-Level with good budget, got {selected_model}"
    
    def test_safety_bypasses_budget_constraints(self):
        """Test that safety stages bypass budget constraints."""
        # Simulate very low budget: 5% tokens remaining
        budget_manager = self.create_budget_manager(tokens_remaining=50, tokens_total=1000)
        
        # Safety should still use heavy models regardless of budget
        selected_model = self.routing_policy.select_model(
            stage="safety",
            archetype=ArchetypeType.RECRUITER,  # Even low-value archetype
            budget_manager=budget_manager
        )
        
        # Should still get heavy model for safety
        assert selected_model in [
            "gpt-5.1",
            "claude-opus-4-1-20250805",
            "gemini-3-pro-preview"
        ], f"Expected heavy model for safety regardless of budget, got {selected_model}"
    
    def test_executive_downgraded_with_low_budget(self):
        """Test that Executive archetype gets downgraded with low budget."""
        # Simulate low budget: 15% tokens remaining
        budget_manager = self.create_budget_manager(tokens_remaining=150, tokens_total=1000)
        
        # Executive normally gets medium models, should get light with low budget
        selected_model = self.routing_policy.select_model(
            stage="message_generation",
            archetype=ArchetypeType.EXECUTIVE,
            budget_manager=budget_manager
        )
        
        # Should downgrade to light model
        assert selected_model in [
            "gpt-5-nano",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-flash-lite"
        ], f"Expected light model for Executive with low budget, got {selected_model}"
    
    def test_ta_recruiter_stay_light_with_good_budget(self):
        """Test that TA/Recruiter stay at light models even with good budget."""
        # Simulate good budget: 90% tokens remaining
        budget_manager = self.create_budget_manager(tokens_remaining=900, tokens_total=1000)
        
        # TA should stay at light models even with good budget (cost optimization)
        selected_model = self.routing_policy.select_model(
            stage="message_generation",
            archetype=ArchetypeType.SENIOR_TA,
            budget_manager=budget_manager
        )
        
        # Should still use light model for cost optimization
        assert selected_model in [
            "gpt-5-nano",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-flash-lite"
        ], f"Expected light model for TA even with good budget, got {selected_model}"
    
    def test_budget_exception_handling(self):
        """Test that budget manager exceptions are handled gracefully."""
        # Create budget manager that raises exception
        budget_manager = Mock(spec=ExecutionBudgetManager)
        budget_manager.current_usage.side_effect = Exception("Budget check failed")
        
        # Should fall back to base complexity without crashing
        selected_model = self.routing_policy.select_model(
            stage="message_generation",
            archetype=ArchetypeType.EXECUTIVE,
            budget_manager=budget_manager
        )
        
        # Should return some valid model (fallback behavior)
        assert selected_model in [
            "gpt-5-nano",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-flash-lite",
            "gpt-5-mini",
            "claude-sonnet-4-5-20250929",
            "gemini-2.5-flash",
            "gpt-5.1",
            "claude-opus-4-1-20250805",
            "gemini-3-pro-preview"
        ], f"Expected valid model fallback, got {selected_model}"
    
    def test_zero_tokens_forces_light_models(self):
        """Test that zero remaining tokens forces light models."""
        # Simulate exhausted budget: 0% tokens remaining
        budget_manager = self.create_budget_manager(tokens_remaining=0, tokens_total=1000)
        
        # Even C-Level should get light models when budget is exhausted
        selected_model = self.routing_policy.select_model(
            stage="message_generation",
            archetype=ArchetypeType.C_LEVEL,
            budget_manager=budget_manager
        )
        
        # Should force light model when budget is exhausted
        assert selected_model in [
            "gpt-5-nano",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-flash-lite"
        ], f"Expected light model for C-Level with exhausted budget, got {selected_model}"
