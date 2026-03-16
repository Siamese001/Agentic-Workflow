"""Routing configuration schema for multi-provider fallback.

Defines the structure for routing tiers and provider fallback chains.

Phase 2 - Resilient Routing Layer
"""

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "routing_tier_config", "p0_governance")
_emit_reads_policy_state("p0", "routing_tier_config", "policy_binding")
_emit_snapshots_state("p0", "routing_tier_config", "state_snapshot")
emit_replay_key("p0", "routing_tier_config")
emit_determinism_digest("p0", "routing_tier_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class RoutingTier(str, Enum):
    """Predefined routing tiers for different use cases."""

    REASONING = "reasoning_tier"
    SPEED = "speed_tier"
    COST_OPTIMIZED = "cost_optimized_tier"
    BALANCED = "balanced_tier"


@dataclass
class RouteConfig:
    """configuration for a routing tier.

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
    fallback_providers: list[Provider]
    timeout_ms: int = 60000
    model_overrides: dict | None = None

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

    def get_all_providers(self) -> list[Provider]:
        """Get all providers in order (primary + fallbacks)."""
        return [self.primary_provider] + self.fallback_providers

    def get_model_for_provider(self, provider: Provider) -> str | None:
        """Get model override for a specific provider."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RouteConfig.get_model_for_provider")

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
