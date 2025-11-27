"""
Basic routing policy tests for model selection based on archetype and budget.

Tests the core routing logic without complex budget constraints to ensure
C-Level gets highest-quality models while other archetypes get appropriate models.
"""

import pytest
from unittest.mock import Mock

from infra.model_routing.policies import ModelRoutingPolicy
from l1.outreach_dataclasses import ArchetypeType
from runtime.execution_budget_manager import ExecutionBudgetManager, BudgetLimits


class TestRoutingPolicyBasic:
    """Test suite for basic model routing policy behavior."""
    
    def setup_method(self):
        """Setup test environment with routing policy and mock budget manager."""
        # Create routing policy with default model tiers
        self.routing_policy = ModelRoutingPolicy()
        
        # Create mock budget manager with unlimited budget for basic tests
        self.mock_budget_manager = Mock(spec=ExecutionBudgetManager)
        self.mock_budget_manager.check_budget.return_value = True
        self.mock_budget_manager.current_usage.return_value = {
            "tokens_remaining": 1000000,
            "requests_remaining": 1000,
            "budget_exceeded": {
                "tokens": False,
                "requests": False,
                "depth": False,
                "concurrent": False
            }
        }
    
    def test_c_level_chooses_high_quality(self):
        """Test that C-Level archetype selects highest-quality models."""
        stage = "message_generation"
        archetype = ArchetypeType.C_LEVEL
        
        # Should select heavy models for C-Level
        selected_model = self.routing_policy.select_model(
            stage=stage,
            archetype=archetype,
            budget_manager=self.mock_budget_manager
        )
        
        # Should return a high-quality model (heavy tier)
        assert selected_model in [
            "gpt-5.1",
            "claude-opus-4-1-20250805", 
            "gemini-3-pro-preview"
        ], f"Expected heavy model for C-Level, got {selected_model}"
    
    def test_executive_chooses_balanced_model(self):
        """Test that Executive archetype selects balanced models."""
        stage = "message_generation"
        archetype = ArchetypeType.EXECUTIVE
        
        selected_model = self.routing_policy.select_model(
            stage=stage,
            archetype=archetype,
            budget_manager=self.mock_budget_manager
        )
        
        # Should return a balanced model (medium tier)
        assert selected_model in [
            "gpt-5-mini",
            "claude-sonnet-4-5-20250929",
            "gemini-2.5-flash"
        ], f"Expected medium model for Executive, got {selected_model}"
    
    def test_ta_chooses_cost_effective_model(self):
        """Test that Senior_TA archetype selects cost-effective models."""
        stage = "message_generation"
        archetype = ArchetypeType.SENIOR_TA
        
        selected_model = self.routing_policy.select_model(
            stage=stage,
            archetype=archetype,
            budget_manager=self.mock_budget_manager
        )
        
        # Should return a cost-effective model (light tier)
        assert selected_model in [
            "gpt-5-nano",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-flash-lite"
        ], f"Expected light model for Senior_TA, got {selected_model}"
    
    def test_recruiter_chooses_cost_effective_model(self):
        """Test that Recruiter archetype selects cost-effective models."""
        stage = "message_generation"
        archetype = ArchetypeType.RECRUITER
        
        selected_model = self.routing_policy.select_model(
            stage=stage,
            archetype=archetype,
            budget_manager=self.mock_budget_manager
        )
        
        # Should return a cost-effective model (light tier)
        assert selected_model in [
            "gpt-5-nano",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-flash-lite"
        ], f"Expected light model for Recruiter, got {selected_model}"
    
    def test_research_stage_uses_appropriate_models(self):
        """Test that research stages use archetype-based model selection."""
        # Research should respect archetype complexity like other stages
        expected_models = {
            ArchetypeType.C_LEVEL: [
                "gpt-5.1",
                "claude-opus-4-1-20250805", 
                "gemini-3-pro-preview"
            ],
            ArchetypeType.EXECUTIVE: [
                "gpt-5-mini",
                "claude-sonnet-4-5-20250929",
                "gemini-2.5-flash"
            ],
            ArchetypeType.SENIOR_TA: [
                "gpt-5-nano",
                "claude-haiku-4-5-20251001",
                "gemini-2.5-flash-lite"
            ],
            ArchetypeType.RECRUITER: [
                "gpt-5-nano",
                "claude-haiku-4-5-20251001",
                "gemini-2.5-flash-lite"
            ]
        }
        
        for archetype, expected_model_list in expected_models.items():
            selected_model = self.routing_policy.select_model(
                stage="research",
                archetype=archetype,
                budget_manager=self.mock_budget_manager
            )
            
            assert selected_model in expected_model_list, f"Expected {expected_model_list} for {archetype} research, got {selected_model}"
    
    def test_safety_stage_always_uses_high_quality(self):
        """Test that safety stages always use high-quality models regardless of archetype."""
        for archetype in ArchetypeType:
            selected_model = self.routing_policy.select_model(
                stage="safety",
                archetype=archetype,
                budget_manager=self.mock_budget_manager
            )
            
            # Safety should always use heavy models
            assert selected_model in [
                "gpt-5.1",
                "claude-opus-4-1-20250805",
                "gemini-3-pro-preview"
            ], f"Expected heavy model for safety, got {selected_model}"
    
    def test_unknown_stage_defaults_to_medium(self):
        """Test that unknown stages default to medium models."""
        selected_model = self.routing_policy.select_model(
            stage="unknown_stage",
            archetype=ArchetypeType.C_LEVEL,
            budget_manager=self.mock_budget_manager
        )
        
        # Should default to medium model
        assert selected_model in [
            "gpt-5-mini",
            "claude-sonnet-4-5-20250929",
            "gemini-2.5-flash"
        ], f"Expected medium model for unknown stage, got {selected_model}"
    
    def test_model_selection_consistency(self):
        """Test that model selection is consistent for same inputs."""
        stage = "message_generation"
        archetype = ArchetypeType.EXECUTIVE
        
        # Multiple calls should return same model
        model1 = self.routing_policy.select_model(stage, archetype, self.mock_budget_manager)
        model2 = self.routing_policy.select_model(stage, archetype, self.mock_budget_manager)
        
        assert model1 == model2, "Model selection should be deterministic"
