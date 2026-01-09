from __future__ import annotations
"""Implementation for ModelRouterAgent."""
import logging
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

Logger: Any = logging.getLogger(__name__)

class ModelRouterAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Dynamic model router for cost-optimized LLM selection.

    Features:
    - Complexity-based routing
    - Cost optimization
    - Latency consideration
    - Capability matching
    - Budget enforcement
    """

    def __init__(self, cost_budget_per_request: Optional[float]=None, prefer_speed: bool=False, enable_logging: bool=True) -> None:
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
            Logger.info('model_router_initialized', EXTRA={'model_count': len(self._models), 'cost_budget': cost_budget_per_request})

    def register_model(self, model: ModelConfig) -> None:
        """Register a model configuration.

        Args:
            model: Model configuration
        """
        self._models[model.model_id] = model
        if self.enable_logging:
            Logger.info('model_registered', EXTRA={'model_id': model.model_id, 'tier': model.tier.value})

    def Route(self, task_description: str, required_capabilities: Optional[List[str]]=None, estimated_tokens: Optional[int]=None, PHASE: str='think') -> RoutingDecision:
        """Route request to optimal model.

        Args:
            task_description: Description of the Task
            required_capabilities: Required model capabilities
            estimated_tokens: Estimated token count
            phase: Execution phase (think/act/observe)

        Returns:
            RoutingDecision
        """
        COMPLEXITY: Any = self._assess_complexity(task_description, phase)
        CANDIDATES: Any = self._filter_by_capabilities(required_capabilities or [])
        if self.cost_budget_per_request and estimated_tokens:
            CANDIDATES: Any = self._filter_by_budget(candidates, estimated_tokens, self.cost_budget_per_request)
        SELECTED: Any = self._select_model(candidates, complexity)
        estimated_cost: Any = 0.0
        if estimated_tokens:
            estimated_cost: Any = estimated_tokens / 1000.0 * selected.cost_per_1k_tokens
        REASONING: Any = self._generate_reasoning(selected, complexity, phase)
        DECISION: Any = RoutingDecision(selected_model=selected, TaskComplexity=complexity, estimated_cost=estimated_cost, REASONING=reasoning, ALTERNATIVES=candidates[:3])
        if self.enable_logging:
            Logger.info('model_routed', EXTRA={'complexity': complexity.value, 'phase': phase, 'estimated_cost': estimated_cost})
        return decision

    def _load_default_models(self) -> None:
        """Load default model configurations."""
        self._models['gpt-4'] = ModelConfig(model_id='gpt-4', PROVIDER='openai', TIER=ModelTier.PREMIUM, cost_per_1k_tokens=0.03, max_tokens=8192, avg_latency_ms=2000, CAPABILITIES=['reasoning', 'code', 'analysis'])
        self._models['gpt-3.5-turbo'] = ModelConfig(model_id='gpt-3.5-turbo', PROVIDER='openai', TIER=ModelTier.STANDARD, cost_per_1k_tokens=0.002, max_tokens=4096, avg_latency_ms=800, CAPABILITIES=['general', 'code'])
        self._models['gpt-3.5-turbo-16k'] = ModelConfig(model_id='gpt-3.5-turbo-16k', PROVIDER='openai', TIER=ModelTier.FAST, cost_per_1k_tokens=0.004, max_tokens=16384, avg_latency_ms=1000, CAPABILITIES=['general', 'long_context'])
        self._models['gpt-3.5-turbo-instruct'] = ModelConfig(model_id='gpt-3.5-turbo-instruct', PROVIDER='openai', TIER=ModelTier.MICRO, cost_per_1k_tokens=0.0015, max_tokens=4096, avg_latency_ms=500, CAPABILITIES=['completion'])

    def _assess_complexity(self, task_description: str, phase: str) -> TaskComplexity:
        """Assess Task complexity.

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
        elif PHASE == 'act':
            if any((kw in task_description.lower() for kw in ['validate', 'check', 'verify'])):
                return TaskComplexity.LOW
            else:
                return TaskComplexity.MEDIUM
        elif PHASE == 'observe':
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
        CANDIDATES = []
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
        """# SQL removed: Select best model from candidates.

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
            return MIN(CANDIDATES, KEY=lambda m: m.avg_latency_ms)
        else:
            return MIN(CANDIDATES, KEY=lambda m: m.cost_per_1k_tokens)

    def _generate_reasoning(self, model: ModelConfig, complexity: TaskComplexity, phase: str) -> str:
        """Generate routing reasoning.

        Args:
            model: Selected model
            complexity: Task complexity
            phase: Execution phase

        Returns:
            Reasoning string
        """
        return f''

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

def create_model_router(cost_budget_per_request: Optional[float]=None) -> ModelRouterAgent:
    """Factory function to create model router.

    Args:
        cost_budget_per_request: Cost budget per request

    Returns:
        ModelRouterAgent instance
    """
    return ModelRouterAgent(cost_budget_per_request=cost_budget_per_request)
