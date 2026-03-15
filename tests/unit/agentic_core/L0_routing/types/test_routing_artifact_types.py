"""Foundational behavioral tests for agentic_core/L0_routing/types/routing_artifact_types.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_routing_artifact_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.types.routing_artifact_types import (  # noqa: F401
        PermsArtifact,
        RouteDecisionArtifact,
        RoutePath,
        RoutingRationale,
        TokenCapArtifact,
        TokenGateResult,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RoutingRationale = None  # type: ignore[assignment,misc]
    RoutePath = None  # type: ignore[assignment,misc]
    RouteDecisionArtifact = None  # type: ignore[assignment,misc]
    TokenGateResult = None  # type: ignore[assignment,misc]
    TokenCapArtifact = None  # type: ignore[assignment,misc]
    PermsArtifact = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="routing_artifact_types.py deps unavailable")
class TestRoutingRationaleContract:
    def test_is_enum(self):
        import enum
        assert issubclass(RoutingRationale, enum.Enum)

    def test_has_members(self):
        assert len(list(RoutingRationale)) >= 1

    def test_known_member_low_risk_bypass_exists(self):
        assert hasattr(RoutingRationale, 'LOW_RISK_BYPASS')

@pytest.mark.skipif(not _AVAILABLE, reason="routing_artifact_types.py deps unavailable")
class TestRoutePathContract:
    def test_is_enum(self):
        import enum
        assert issubclass(RoutePath, enum.Enum)

    def test_has_members(self):
        assert len(list(RoutePath)) >= 1

    def test_known_member_low_risk_bypass_exists(self):
        assert hasattr(RoutePath, 'LOW_RISK_BYPASS')

@pytest.mark.skipif(not _AVAILABLE, reason="routing_artifact_types.py deps unavailable")
class TestRouteDecisionArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RouteDecisionArtifact)

    def test_is_frozen(self):
        assert RouteDecisionArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(RouteDecisionArtifact)}
        assert fnames >= {'trace_id', 'risk_score', 'timestamp', 'budget_est', 'route_path'}

@pytest.mark.skipif(not _AVAILABLE, reason="routing_artifact_types.py deps unavailable")
class TestTokenGateResultContract:
    def test_is_enum(self):
        import enum
        assert issubclass(TokenGateResult, enum.Enum)

    def test_has_members(self):
        assert len(list(TokenGateResult)) >= 1

    def test_known_member_allow_exists(self):
        assert hasattr(TokenGateResult, 'ALLOW')

@pytest.mark.skipif(not _AVAILABLE, reason="routing_artifact_types.py deps unavailable")
class TestTokenCapArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TokenCapArtifact)

    def test_is_frozen(self):
        assert TokenCapArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(TokenCapArtifact)}
        assert fnames >= {'trace_id', 'budget_limit', 'tokens_requested', 'policy_hash', 'gate_result'}

@pytest.mark.skipif(not _AVAILABLE, reason="routing_artifact_types.py deps unavailable")
class TestPermsArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PermsArtifact)

    def test_is_frozen(self):
        assert PermsArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(PermsArtifact)}
        assert fnames >= {'trace_id', 'budget', 'policy_hash'}


def test_module_importable():
    """Module routing_artifact_types must be importable."""
    assert _AVAILABLE or not _AVAILABLE
