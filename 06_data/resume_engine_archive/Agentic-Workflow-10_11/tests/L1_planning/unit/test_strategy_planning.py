"""
Test Strategy Planning

Tests comprehensive strategy planning functionality for résumé improvement,
including strategy plan creation, drafting plan generation, and latent thinking planning.
"""

import pytest
from unittest.mock import Mock, patch

# Import actual strategy planning components
try:
    from l1.strategy_planning import (
        generate_latent_thinking_plan,
        StrategyPlan,
        DraftPlan,
        LatentThinkingPlan,
    )
except ImportError:
    pytest.skip("Strategy planning components not available", allow_module_level=True)

# Mark as L1 planning tests
pytestmark = [pytest.mark.l1, pytest.mark.planning, pytest.mark.strategy]


class TestStrategyPlanning:
    """Test strategy planning functionality."""
    
    def test_generate_latent_thinking_plan_basic(self):
        """Test basic latent thinking plan generation."""
        # Create inputs
        result = Mock()
        ctx = Mock()
        ctx.profile_name = "default"
        ctx.config = Mock()
        ctx.config.profile_id = "default"
        
        # Execute latent thinking planning
        plan = generate_latent_thinking_plan(result, ctx)
        
        # Validate result
        assert isinstance(plan, LatentThinkingPlan)
        assert plan.profile_name == "default"
        assert plan.reasoning_mode == "cot"
        assert plan.depth == 1
        assert isinstance(plan.trace, list)
    
    def test_generate_latent_thinking_plan_with_profile_name(self):
        """Test latent thinking plan with specific profile name."""
        # Create inputs
        result = Mock()
        ctx = Mock()
        ctx.profile_name = "senior_engineer"
        ctx.config = Mock()
        ctx.config.profile_id = "senior_engineer"
        
        # Execute latent thinking planning
        plan = generate_latent_thinking_plan(result, ctx)
        
        # Validate result
        assert isinstance(plan, LatentThinkingPlan)
        assert plan.profile_name == "senior_engineer"
        assert plan.reasoning_mode == "cot"
        assert plan.depth == 1
    
    def test_generate_latent_thinking_plan_with_config_fallback(self):
        """Test latent thinking plan falls back to config profile_id."""
        # Create inputs
        result = Mock()
        ctx = Mock()
        ctx.profile_name = None  # No profile_name attribute
        ctx.config = Mock()
        ctx.config.profile_id = "fallback_profile"
        
        # Execute latent thinking planning
        plan = generate_latent_thinking_plan(result, ctx)
        
        # Validate result
        assert isinstance(plan, LatentThinkingPlan)
        assert plan.profile_name == "fallback_profile"
        assert plan.reasoning_mode == "cot"
        assert plan.depth == 1
    
    def test_generate_latent_thinking_plan_default_fallback(self):
        """Test latent thinking plan with complete fallback to default."""
        # Create inputs with no profile information
        result = Mock()
        ctx = Mock()
        # Neither profile_name nor config.profile_id available
        delattr(ctx, 'profile_name') if hasattr(ctx, 'profile_name') else None
        ctx.config = Mock()
        delattr(ctx.config, 'profile_id') if hasattr(ctx.config, 'profile_id') else None
        
        # Execute latent thinking planning
        plan = generate_latent_thinking_plan(result, ctx)
        
        # Validate result
        assert isinstance(plan, LatentThinkingPlan)
        assert plan.profile_name == "default"
        assert plan.reasoning_mode == "cot"
        assert plan.depth == 1
    
    def test_strategy_plan_dataclass_structure(self):
        """Test StrategyPlan dataclass structure."""
        # Create a mock prompt
        prompt = Mock()
        prompt.id = "test.strategy"
        prompt.content = "Test strategy content"
        
        # Create StrategyPlan
        strategy_plan = StrategyPlan(prompt=prompt)
        
        # Validate structure
        assert hasattr(strategy_plan, 'prompt')
        assert strategy_plan.prompt == prompt
        assert isinstance(strategy_plan.prompt, Mock)
    
    def test_draft_plan_dataclass_structure(self):
        """Test DraftPlan dataclass structure."""
        # Create a mock prompt
        prompt = Mock()
        prompt.id = "test.draft"
        prompt.content = "Test draft content"
        
        # Create DraftPlan
        draft_plan = DraftPlan(prompt=prompt)
        
        # Validate structure
        assert hasattr(draft_plan, 'prompt')
        assert draft_plan.prompt == prompt
        assert isinstance(draft_plan.prompt, Mock)
    
    def test_latent_thinking_plan_dataclass_structure(self):
        """Test LatentThinkingPlan dataclass structure."""
        # Create LatentThinkingPlan
        thinking_plan = LatentThinkingPlan(
            profile_name="test_profile",
            reasoning_mode="cot",
            depth=2,
            trace=["step1", "step2"]
        )
        
        # Validate structure
        assert thinking_plan.profile_name == "test_profile"
        assert thinking_plan.reasoning_mode == "cot"
        assert thinking_plan.depth == 2
        assert thinking_plan.trace == ["step1", "step2"]
        assert isinstance(thinking_plan.trace, list)
