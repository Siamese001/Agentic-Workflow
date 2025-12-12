"""Resilient routing infrastructure for multi-provider fallback.

Provides intelligent routing with automatic failover based on circuit breaker
states and provider health.

Phase 2 - Resilient Routing Layer
"""

from .schema import RouteConfig, RoutingTier
from .router import HardenedRouter, AllProvidersDownError
from .factory import get_resilient_router, reset_router

__all__ = [
    "RouteConfig",
    "RoutingTier",
    "HardenedRouter",
    "AllProvidersDownError",
    "get_resilient_router",
    "reset_router",
]
