# Model routing for L3 orchestration layer
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ModelChoice:
    """Choice of model for execution"""
    provider: str
    model_name: str
    cost_tier: str = "medium"
    estimated_cost: float = 0.001
    latency_ms: int = 500
    metadata: Dict[str, Any] = None
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RoutingContext:
    """Context for model routing decisions"""
    agent_id: str
    task_type: str
    execution_profile: Optional[Any] = None
    metadata: Dict[str, Any] = None
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

def select_model(ctx: RoutingContext, requested_model: Optional[str] = None, execution_profile: Optional[Any] = None) -> ModelChoice:
    """Select a model based on routing context"""
    if requested_model:
        if "claude" in requested_model.lower():
            return ModelChoice(provider="anthropic", model_name=requested_model)
        elif "gpt" in requested_model.lower():
            return ModelChoice(provider="openai", model_name=requested_model)
    
    # Default selection
    return ModelChoice(provider="anthropic", model_name="claude-haiku-4-5-20251001")

def choose_provider_and_model(ctx: RoutingContext, requested_model: Optional[str] = None) -> ModelChoice:
    """Choose provider and model for given context"""
    return select_model(ctx, requested_model)

def enforce_budget(choice: ModelChoice, profile: Any) -> ModelChoice:
    """Enforce budget constraints on model choice"""
    # Stub implementation - downgrade high cost models if needed
    if choice.cost_tier == "high" and hasattr(profile, 'budget_limit'):
        if profile.budget_limit < choice.estimated_cost:
            # Downgrade to medium tier
            return ModelChoice(
                provider=choice.provider,
                model_name="claude-haiku-4-5-20251001",
                cost_tier="medium",
                estimated_cost=0.001,
                latency_ms=300
            )
    return choice
