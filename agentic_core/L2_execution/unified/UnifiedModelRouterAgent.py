#!/usr/bin/env python3
"""
UnifiedModelRouterAgent - Model Routing with Cost Optimization

Phase 4 Hard Migration: Consolidates:
- DynamicModelRouterAgent (dynamic model selection)
- MultiProviderRouterAgent (multi-provider routing)
- ReasoningRouterAgent (reasoning-based routing)
- ModelRouterAgent (basic model routing)
- McpRouterAgent (MCP routing)

Features:
- Cost-optimized model selection
- Reasoning complexity detection
- Multi-provider failover
- Dynamic model switching
- Token budget management
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

Logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tiers by capability and cost."""

    ECONOMY = 0  # Low cost, basic tasks
    STANDARD = 1  # Medium cost, general tasks
    PREMIUM = 2  # High cost, complex reasoning
    FLAGSHIP = 3  # Highest cost, most capable


class TaskComplexity(Enum):
    """Task complexity levels."""

    SIMPLE = 0  # Basic Q&A, formatting
    MODERATE = 1  # Summarization, basic analysis
    COMPLEX = 2  # Multi-step reasoning, coding
    EXPERT = 3  # Advanced reasoning, research


@dataclass
class ModelConfig:
    """Configuration for a model."""

    name: str
    provider: str
    tier: ModelTier
    cost_per_1k_tokens: float
    max_tokens: int
    supports_vision: bool = False
    supports_tools: bool = True
    latency_ms: int = 500


@dataclass
class RoutingDecision:
    """Represents a routing decision."""

    model: ModelConfig
    reason: str
    complexity: TaskComplexity
    estimated_cost: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RouterConfig:
    """Configuration for the router."""

    enable_cost_optimization: bool = True
    enable_complexity_detection: bool = True
    enable_failover: bool = True
    max_cost_per_request: float = 0.10
    prefer_low_latency: bool = False
    default_tier: ModelTier = ModelTier.STANDARD


class UnifiedModelRouterAgent:
    """
    Unified model router with cost optimization.

    Consolidates:
    - DynamicModelRouterAgent
    - MultiProviderRouterAgent
    - ReasoningRouterAgent
    - ModelRouterAgent
    - McpRouterAgent

    Usage:
        router = UnifiedModelRouterAgent()

        # Route a task
        decision = router.route("Explain quantum computing")

        # Route with specific requirements
        decision = router.route("Write a complex algorithm", require_tools=True)
    """

    # Default model configurations
    DEFAULT_MODELS = [
        ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            tier=ModelTier.ECONOMY,
            cost_per_1k_tokens=0.00015,
            max_tokens=128000,
        ),
        ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier=ModelTier.STANDARD,
            cost_per_1k_tokens=0.005,
            max_tokens=128000,
            supports_vision=True,
        ),
        ModelConfig(
            name="claude-3-5-sonnet",
            provider="anthropic",
            tier=ModelTier.PREMIUM,
            cost_per_1k_tokens=0.003,
            max_tokens=200000,
            supports_vision=True,
        ),
        ModelConfig(
            name="claude-3-opus",
            provider="anthropic",
            tier=ModelTier.FLAGSHIP,
            cost_per_1k_tokens=0.015,
            max_tokens=200000,
            supports_vision=True,
        ),
        ModelConfig(
            name="o1",
            provider="openai",
            tier=ModelTier.FLAGSHIP,
            cost_per_1k_tokens=0.015,
            max_tokens=200000,
        ),
    ]

    # Complexity indicators
    COMPLEX_INDICATORS = [
        "explain",
        "analyze",
        "compare",
        "evaluate",
        "synthesize",
        "algorithm",
        "optimize",
        "debug",
        "refactor",
        "architect",
        "research",
        "investigate",
        "prove",
        "derive",
        "calculate",
    ]

    SIMPLE_INDICATORS = [
        "format",
        "list",
        "summarize",
        "translate",
        "convert",
        "extract",
        "count",
        "find",
        "replace",
        "generate",
    ]

    def __init__(
        self,
        models: list[ModelConfig] | None = None,
        config: RouterConfig | None = None,
    ):
        self.models = models or self.DEFAULT_MODELS.copy()
        self.config = config or RouterConfig()
        self._lock = threading.RLock()
        self._decisions: list[RoutingDecision] = []
        self._provider_failures: dict[str, int] = {}

        Logger.info("UnifiedModelRouterAgent initialized")

    def route(
        self,
        task: str,
        require_vision: bool = False,
        require_tools: bool = False,
        max_tokens: int | None = None,
        preferred_provider: str | None = None,
    ) -> RoutingDecision:
        """
        Route a task to the optimal model.

        Args:
            task: Task description or prompt
            require_vision: Whether vision capability is required
            require_tools: Whether tool use is required
            max_tokens: Maximum tokens needed
            preferred_provider: Preferred provider if any

        Returns:
            RoutingDecision with selected model and reasoning
        """
        with self._lock:
            # Detect task complexity
            complexity = self._detect_complexity(task)

            # Filter eligible models
            eligible = self._filter_models(
                require_vision=require_vision,
                require_tools=require_tools,
                max_tokens=max_tokens,
                preferred_provider=preferred_provider,
            )

            if not eligible:
                # Fallback to any available model
                eligible = self.models

            # Select optimal model
            model = self._select_model(eligible, complexity)

            # Estimate cost
            estimated_tokens = len(task.split()) * 1.5  # Rough estimate
            estimated_cost = (estimated_tokens / 1000) * model.cost_per_1k_tokens

            decision = RoutingDecision(
                model=model,
                reason=self._generate_reason(model, complexity),
                complexity=complexity,
                estimated_cost=estimated_cost,
            )

            self._decisions.append(decision)
            Logger.info(f"Routed to {model.name} (complexity: {complexity.name})")

            return decision

    def _detect_complexity(self, task: str) -> TaskComplexity:
        """Detect task complexity from the prompt."""
        if not self.config.enable_complexity_detection:
            return TaskComplexity.MODERATE

        task_lower = task.lower()

        # Count complexity indicators
        complex_count = sum(1 for ind in self.COMPLEX_INDICATORS if ind in task_lower)
        simple_count = sum(1 for ind in self.SIMPLE_INDICATORS if ind in task_lower)

        # Check for code-related tasks
        if any(kw in task_lower for kw in ["code", "function", "class", "debug", "refactor"]):
            complex_count += 2

        # Check for multi-step reasoning
        if any(kw in task_lower for kw in ["step by step", "first", "then", "finally"]):
            complex_count += 1

        # Determine complexity
        if complex_count >= 3:
            return TaskComplexity.EXPERT
        elif complex_count >= 2:
            return TaskComplexity.COMPLEX
        elif simple_count >= 2 or complex_count == 0:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE

    def _filter_models(
        self,
        require_vision: bool = False,
        require_tools: bool = False,
        max_tokens: int | None = None,
        preferred_provider: str | None = None,
    ) -> list[ModelConfig]:
        """Filter models by requirements."""
        eligible = []

        for model in self.models:
            # Check vision requirement
            if require_vision and not model.supports_vision:
                continue

            # Check tools requirement
            if require_tools and not model.supports_tools:
                continue

            # Check token limit
            if max_tokens and model.max_tokens < max_tokens:
                continue

            # Check provider preference
            if preferred_provider and model.provider != preferred_provider:
                continue

            # Check provider failures (failover)
            if self.config.enable_failover:
                failures = self._provider_failures.get(model.provider, 0)
                if failures >= 3:
                    continue

            eligible.append(model)

        return eligible

    def _select_model(
        self,
        eligible: list[ModelConfig],
        complexity: TaskComplexity,
    ) -> ModelConfig:
        """Select optimal model based on complexity and cost."""
        if not eligible:
            return self.models[0]  # Fallback

        # Map complexity to target tier
        tier_map = {
            TaskComplexity.SIMPLE: ModelTier.ECONOMY,
            TaskComplexity.MODERATE: ModelTier.STANDARD,
            TaskComplexity.COMPLEX: ModelTier.PREMIUM,
            TaskComplexity.EXPERT: ModelTier.FLAGSHIP,
        }

        target_tier = tier_map.get(complexity, self.config.default_tier)

        # Find best match
        best_model = None
        best_score = float("inf")

        for model in eligible:
            # Score based on tier distance and cost
            tier_distance = abs(model.tier.value - target_tier.value)
            cost_factor = model.cost_per_1k_tokens * 1000

            if self.config.prefer_low_latency:
                latency_factor = model.latency_ms / 1000
            else:
                latency_factor = 0

            score = tier_distance * 10 + cost_factor + latency_factor

            # Prefer exact tier match
            if model.tier == target_tier:
                score -= 5

            if score < best_score:
                best_score = score
                best_model = model

        return best_model or eligible[0]

    def _generate_reason(self, model: ModelConfig, complexity: TaskComplexity) -> str:
        """Generate routing reason."""
        reasons = []

        if complexity == TaskComplexity.SIMPLE:
            reasons.append("Simple task - using cost-effective model")
        elif complexity == TaskComplexity.EXPERT:
            reasons.append("Expert-level task - using flagship model")
        else:
            reasons.append(f"{complexity.name} complexity detected")

        reasons.append(f"Selected {model.name} ({model.provider})")

        if self.config.enable_cost_optimization:
            reasons.append(f"Cost: ${model.cost_per_1k_tokens}/1k tokens")

        return " | ".join(reasons)

    def report_failure(self, provider: str) -> None:
        """Report a provider failure for failover tracking."""
        with self._lock:
            self._provider_failures[provider] = self._provider_failures.get(provider, 0) + 1

    def reset_failures(self, provider: str | None = None) -> None:
        """Reset failure counts."""
        with self._lock:
            if provider:
                self._provider_failures.pop(provider, None)
            else:
                self._provider_failures.clear()

    def get_decisions(self) -> list[RoutingDecision]:
        """Get all routing decisions."""
        return self._decisions.copy()


# Factory methods for backward compatibility
def create_legacy_model_router() -> UnifiedModelRouterAgent:
    """Create basic model router."""
    return UnifiedModelRouterAgent()


def create_legacy_dynamic_router() -> UnifiedModelRouterAgent:
    """Create dynamic model router."""
    config = RouterConfig(
        enable_cost_optimization=True,
        enable_complexity_detection=True,
    )
    return UnifiedModelRouterAgent(config=config)
