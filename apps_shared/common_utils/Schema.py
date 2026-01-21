"""Routing configuration schema for multi-provider fallback.

Defines the structure for routing tiers and provider fallback chains.

Phase 2 - Resilient Routing Layer
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from runtime.shared.multi_provider_clients import Provider


class RoutingTier(str, Enum):
    """Predefined routing tiers for different use cases."""
    REASONING = "reasoning_tier"
    SPEED = "speed_tier"
    COST_OPTIMIZED = "cost_optimized_tier"
    BALANCED = "balanced_tier"


@dataclass
class RouteConfig:
    """Configuration for a routing tier.

    Defines the primary provider and fallback chain for a specific
    routing tier. The router will attempt providers in order until
    one succeeds.

    Attributes:
        tier_name: Name of the routing tier
        primary_provider: Primary provider to attempt first
        fallback_providers: Ordered list of fallback providers
        timeout_ms: Timeout for each provider attempt
        model_overrides: Optional model name overrides per provider
    """

    tier_name: str
    primary_provider: Provider
    fallback_providers: List[Provider]
    timeout_ms: int = 60000
    model_overrides: Optional[dict] = None

    def __post_init__(self):
        """Validate configuration."""
        if not self.tier_name:
            raise ValueError("tier_name cannot be empty")

        if not self.fallback_providers:
            raise ValueError("fallback_providers cannot be empty")

        # Ensure no duplicate providers in the chain
        all_providers = [self.primary_provider] + self.fallback_providers
        if len(all_providers) != len(set(all_providers)):
            raise ValueError("Duplicate providers in routing chain")

        if self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")

    def get_all_providers(self) -> List[Provider]:
        """Get all providers in order (primary + fallbacks)."""
        return [self.primary_provider] + self.fallback_providers

    def get_model_for_provider(self, provider: Provider) -> Optional[str]:
        """Get model override for a specific provider."""
        if self.model_overrides:
            return self.model_overrides.get(provider.value)
        return None


# Default routing configurations
DEFAULT_ROUTING_CONFIGS = {
    RoutingTier.REASONING: RouteConfig(
        tier_name=RoutingTier.REASONING.value,
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.ANTHROPIC, Provider.GOOGLE],
        timeout_ms=120000,  # 2 minutes for reasoning tasks
        model_overrides={
            Provider.OPENAI.value: "gpt-4o-2024-08-06",
            Provider.ANTHROPIC.value: "claude-3-5-sonnet-20241022",
            Provider.GOOGLE.value: "gemini-2.5-flash",
        },
    ),
    RoutingTier.SPEED: RouteConfig(
        tier_name=RoutingTier.SPEED.value,
        primary_provider=Provider.GOOGLE,
        fallback_providers=[Provider.OPENAI, Provider.ANTHROPIC],
        timeout_ms=30000,  # 30 seconds for speed tasks
        model_overrides={
            Provider.GOOGLE.value: "gemini-2.5-flash",
            Provider.OPENAI.value: "gpt-4o-mini",
            Provider.ANTHROPIC.value: "claude-3-5-haiku-20241022",
        },
    ),
    RoutingTier.COST_OPTIMIZED: RouteConfig(
        tier_name=RoutingTier.COST_OPTIMIZED.value,
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.GOOGLE, Provider.ANTHROPIC],
        timeout_ms=60000,
        model_overrides={
            Provider.OPENAI.value: "gpt-4o-mini",
            Provider.GOOGLE.value: "gemini-2.5-flash",
            Provider.ANTHROPIC.value: "claude-3-5-haiku-20241022",
        },
    ),
    RoutingTier.BALANCED: RouteConfig(
        tier_name=RoutingTier.BALANCED.value,
        primary_provider=Provider.ANTHROPIC,
        fallback_providers=[Provider.OPENAI, Provider.GOOGLE],
        timeout_ms=60000,
        model_overrides={
            Provider.ANTHROPIC.value: "claude-3-5-sonnet-20241022",
            Provider.OPENAI.value: "gpt-4o-2024-08-06",
            Provider.GOOGLE.value: "gemini-2.5-flash",
        },
    ),
}
