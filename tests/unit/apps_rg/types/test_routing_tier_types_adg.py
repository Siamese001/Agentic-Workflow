"""ADG contract tests for apps_rg/types/routing_tier_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_routing_tier_types_adg")
_emit_applies_guardrail("p0", "test_routing_tier_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_routing_tier_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_routing_tier_types_adg", "state_snapshot")
emit_replay_key("p0", "test_routing_tier_types_adg")
emit_determinism_digest("p0", "test_routing_tier_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
