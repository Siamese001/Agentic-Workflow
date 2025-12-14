"""Resilient routing infrastructure for multi-provider fallback.


logger = logging.getLogger(__name__)
Provides intelligent routing with automatic failover based on circuit breaker
states and provider health.

Phase 2 - Resilient Routing Layer
"""
import logging


__all__ = [
    "RouteConfig",
    "RoutingTier",
    "HardenedRouter",
    "AllProvidersDownError",
    "get_resilient_router",
    "reset_router",
]
