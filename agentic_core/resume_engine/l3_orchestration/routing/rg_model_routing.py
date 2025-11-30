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
    # Check if profile has max_cost_tier constraint in metadata
    max_cost_tier = None
    if hasattr(profile, 'metadata') and profile.metadata:
        max_cost_tier = profile.metadata.get("max_cost_tier")

    # Downgrade high cost models if max_cost_tier is lower
    if max_cost_tier and choice.cost_tier == "high":
        if max_cost_tier == "medium":
            return ModelChoice(
                provider=choice.provider,
                model_name="gpt-4-turbo",
                cost_tier="medium",
                estimated_cost=0.002,
                latency_ms=800,
                metadata=choice.metadata.copy()
            )
        elif max_cost_tier == "low":
            return ModelChoice(
                provider=choice.provider,
                model_name="gpt-3.5-turbo",
                cost_tier="low",
                estimated_cost=0.0005,
                latency_ms=400,
                metadata=choice.metadata.copy()
            )

    return choice
