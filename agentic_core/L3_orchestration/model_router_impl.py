"""Implementation for model_router."""

from typing import Any, Dict, List, Optional
from .model_router_types import *

class ModelRouter:
    """Dynamic model router for cost-optimized LLM selection.
    
    Features:
    - Complexity-based routing
    - Cost optimization
    - Latency consideration
    - Capability matching
    - Budget enforcement
    """

    def __init__(self, cost_budget_per_request: Optional[float]=None, prefer_speed: bool=False, enable_logging: bool=True):
        """Initialize model router.
        
        Args:
            cost_budget_per_request: Maximum cost per request
            prefer_speed: Prefer faster models over cheaper
            enable_logging: Enable logging
        """
        self.cost_budget_per_request = cost_budget_per_request
        self.prefer_speed = prefer_speed
        self.enable_logging = enable_logging
        self._models: Dict[str, ModelConfig] = {}
        self._load_default_models()
        if self.enable_logging:
            logger.info('model_router_initialized', extra={'model_count': len(self._models), 'cost_budget': cost_budget_per_request})

    def register_model(self, model: ModelConfig) -> None:
        """Register a model configuration.
        
        Args:
            model: Model configuration
        """
        self._models[model.model_id] = model
        if self.enable_logging:
            logger.info('model_registered', extra={'model_id': model.model_id, 'tier': model.tier.value})

    def route(self, task_description: str, required_capabilities: Optional[List[str]]=None, estimated_tokens: Optional[int]=None, phase: str='think') -> RoutingDecision:
        """Route request to optimal model.
        
        Args:
            task_description: Description of the task
            required_capabilities: Required model capabilities
            estimated_tokens: Estimated token count
            phase: Execution phase (think/act/observe)
            
        Returns:
            RoutingDecision
        """
        complexity = self._assess_complexity(task_description, phase)
        candidates = self._filter_by_capabilities(required_capabilities or [])
        if self.cost_budget_per_request and estimated_tokens:
            candidates = self._filter_by_budget(candidates, estimated_tokens, self.cost_budget_per_request)
        selected = self._select_model(candidates, complexity)
        estimated_cost = 0.0
        if estimated_tokens:
            estimated_cost = estimated_tokens / 1000.0 * selected.cost_per_1k_tokens
        reasoning = self._generate_reasoning(selected, complexity, phase)
        decision = RoutingDecision(selected_model=selected, task_complexity=complexity, estimated_cost=estimated_cost, reasoning=reasoning, alternatives=candidates[:3])
        if self.enable_logging:
            logger.info('model_routed', extra={'selected_model': selected.model_id, 'complexity': complexity.value, 'phase': phase, 'estimated_cost': estimated_cost})
        return decision

    def _load_default_models(self) -> None:
        """Load default model configurations."""
        self._models['gpt-4'] = ModelConfig(model_id='gpt-4', provider='openai', tier=ModelTier.PREMIUM, cost_per_1k_tokens=0.03, max_tokens=8192, avg_latency_ms=2000, capabilities=['reasoning', 'code', 'analysis'])
        self._models['gpt-3.5-turbo'] = ModelConfig(model_id='gpt-3.5-turbo', provider='openai', tier=ModelTier.STANDARD, cost_per_1k_tokens=0.002, max_tokens=4096, avg_latency_ms=800, capabilities=['general', 'code'])
        self._models['gpt-3.5-turbo-16k'] = ModelConfig(model_id='gpt-3.5-turbo-16k', provider='openai', tier=ModelTier.FAST, cost_per_1k_tokens=0.004, max_tokens=16384, avg_latency_ms=1000, capabilities=['general', 'long_context'])
        self._models['gpt-3.5-turbo-instruct'] = ModelConfig(model_id='gpt-3.5-turbo-instruct', provider='openai', tier=ModelTier.MICRO, cost_per_1k_tokens=0.0015, max_tokens=4096, avg_latency_ms=500, capabilities=['completion'])

    def _assess_complexity(self, task_description: str, phase: str) -> TaskComplexity:
        """Assess task complexity.
        
        Args:
            task_description: Task description
            phase: Execution phase
            
        Returns:
            TaskComplexity
        """
        if phase == 'think':
            if any((kw in task_description.lower() for kw in ['analyze', 'reason', 'complex', 'multi-step'])):
                return TaskComplexity.VERY_HIGH
            elif any((kw in task_description.lower() for kw in ['plan', 'strategy', 'design'])):
                return TaskComplexity.HIGH
            else:
                return TaskComplexity.MEDIUM
        elif phase == 'act':
            if any((kw in task_description.lower() for kw in ['validate', 'check', 'verify'])):
                return TaskComplexity.LOW
            else:
                return TaskComplexity.MEDIUM
        elif phase == 'observe':
            return TaskComplexity.LOW
        return TaskComplexity.MEDIUM

    def _filter_by_capabilities(self, required_capabilities: List[str]) -> List[ModelConfig]:
        """Filter models by required capabilities.
        
        Args:
            required_capabilities: Required capabilities
            
        Returns:
            List of matching models
        """
        if not required_capabilities:
            return list(self._models.values())
        candidates = []
        for model in self._models.values():
            if all((cap in model.capabilities for cap in required_capabilities)):
                candidates.append(model)
        return candidates if candidates else list(self._models.values())

    def _filter_by_budget(self, models: List[ModelConfig], estimated_tokens: int, budget: float) -> List[ModelConfig]:
        """Filter models by cost budget.
        
        Args:
            models: Candidate models
            estimated_tokens: Estimated tokens
            budget: Cost budget
            
        Returns:
            Models within budget
        """
        within_budget = []
        for model in models:
            estimated_cost = estimated_tokens / 1000.0 * model.cost_per_1k_tokens
            if estimated_cost <= budget:
                within_budget.append(model)
        return within_budget if within_budget else models

    def _select_model(self, candidates: List[ModelConfig], complexity: TaskComplexity) -> ModelConfig:
        """Select best model from candidates.
        
        Args:
            candidates: Candidate models
            complexity: Task complexity
            
        Returns:
            Selected model
        """
        if not candidates:
            return min(self._models.values(), key=lambda m: m.cost_per_1k_tokens)
        tier_preference = {TaskComplexity.VERY_HIGH: ModelTier.PREMIUM, TaskComplexity.HIGH: ModelTier.STANDARD, TaskComplexity.MEDIUM: ModelTier.STANDARD, TaskComplexity.LOW: ModelTier.FAST, TaskComplexity.TRIVIAL: ModelTier.MICRO}
        preferred_tier = tier_preference.get(complexity, ModelTier.STANDARD)
        tier_matches = [m for m in candidates if m.tier == preferred_tier]
        if tier_matches:
            if self.prefer_speed:
                return min(tier_matches, key=lambda m: m.avg_latency_ms)
            else:
                return min(tier_matches, key=lambda m: m.cost_per_1k_tokens)
        if self.prefer_speed:
            return min(candidates, key=lambda m: m.avg_latency_ms)
        else:
            return min(candidates, key=lambda m: m.cost_per_1k_tokens)

    def _generate_reasoning(self, model: ModelConfig, complexity: TaskComplexity, phase: str) -> str:
        """Generate routing reasoning.
        
        Args:
            model: Selected model
            complexity: Task complexity
            phase: Execution phase
            
        Returns:
            Reasoning string
        """
        return f'Selected {model.model_id} ({model.tier.value}) for {phase} phase with {complexity.value} complexity. Cost: ${model.cost_per_1k_tokens}/1K tokens, Latency: ~{model.avg_latency_ms}ms'

def create_model_router(cost_budget_per_request: Optional[float]=None) -> ModelRouter:
    """Factory function to create model router.
    
    Args:
        cost_budget_per_request: Cost budget per request
        
    Returns:
        ModelRouter instance
    """
    return ModelRouter(cost_budget_per_request=cost_budget_per_request)

