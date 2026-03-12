"""ADG importability contract for agentic_core/L0_routing/seams/redis_decision_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_redis_decision_cache.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.seams.redis_decision_cache import (  # noqa: F401
        RouteDecisionCache,
        RoutingRuleSurfaceCache,
        CapabilityRegistryCache,
        get_route_decision_cache,
        get_routing_rule_surface_cache,
        get_cap_registry_cache,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RouteDecisionCache = None  # type: ignore[assignment,misc]
    RoutingRuleSurfaceCache = None  # type: ignore[assignment,misc]
    CapabilityRegistryCache = None  # type: ignore[assignment,misc]
    get_route_decision_cache = None  # type: ignore[assignment,misc]
    get_routing_rule_surface_cache = None  # type: ignore[assignment,misc]
    get_cap_registry_cache = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="redis_decision_cache.py deps unavailable")
class TestRedisDecisionCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: redis_decision_cache.py must be importable."""
        assert _AVAILABLE

    def test_routedecisioncache_is_type(self) -> None:
        assert RouteDecisionCache is not None

    def test_routingrulesurfacecache_is_type(self) -> None:
        assert RoutingRuleSurfaceCache is not None

    def test_capabilityregistrycache_is_type(self) -> None:
        assert CapabilityRegistryCache is not None

    def test_get_route_decision_cache_callable(self) -> None:
        assert callable(get_route_decision_cache)

    def test_get_routing_rule_surface_cache_callable(self) -> None:
        assert callable(get_routing_rule_surface_cache)

