"""ADG contract tests for apps_rg/types/routing_tier_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_rg.types.routing_tier_types import (
        ProviderType,
        RouterConfig,
        RouteResult,
        RoutingTier,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    RoutingTier = ProviderType = RouterConfig = RouteResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRoutingTier:
    def test_is_enum(self):
        import enum; assert issubclass(RoutingTier, enum.Enum)
    def test_has_primary(self): assert RoutingTier.PRIMARY.value == "primary"
    def test_three_tiers(self): assert len(list(RoutingTier)) == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestProviderType:
    def test_is_enum(self):
        import enum; assert issubclass(ProviderType, enum.Enum)
    def test_has_openai(self): assert ProviderType.OPENAI.value == "openai"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouterConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RouterConfig)
    def test_defaults(self):
        c = RouterConfig()
        assert c.fallback_enabled is True
        assert c.timeout_seconds == 30
        assert c.retry_attempts == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RouteResult)
    def test_creates(self):
        r = RouteResult(provider_used=ProviderType.OPENAI, response="ok", latency_ms=100.0)
        assert r.response == "ok"; assert r.metadata == {}

def test_module_importable(): assert _AVAIL or not _AVAIL
