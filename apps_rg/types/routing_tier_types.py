"""Router schema definitions.

This module contains the configuration and type definitions
for the hardened router system.

# guardian: allow-magic-config
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoutingTier(Enum):
    """Routing tiers for different provider priorities."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


@dataclass
class RouterConfig:
    default_provider: ProviderType = ProviderType.ANTHROPIC
    fallback_enabled: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3


@dataclass
class RouteResult:
    provider_used: ProviderType
    response: str
    latency_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteConfig:
    """Configuration for a specific routing tier."""

    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout_seconds: int = 30
    retry_attempts: int = 3
    enabled: bool = True


# guardian: allow-magic-config
DEFAULT_ROUTING_CONFIGS = {
    RoutingTier.PRIMARY: RouteConfig(provider="openai", model="gpt-4", temperature=0.7, max_tokens=2048),
    RoutingTier.SECONDARY: RouteConfig(
        provider="anthropic",
        model="claude-sonnet-4-6",
        temperature=0.7,
        max_tokens=2048,
    ),
    RoutingTier.TERTIARY: RouteConfig(
        provider="google",
        model="gemini-pro",
        temperature=0.7,
        max_tokens=2048,
    ),
}
