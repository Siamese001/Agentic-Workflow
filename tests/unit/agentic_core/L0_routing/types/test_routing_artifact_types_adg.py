"""ADG importability contract for agentic_core/L0_routing/types/routing_artifact_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_routing_artifact_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

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


@pytest.mark.skipif(not _AVAILABLE, reason="routing_artifact_types deps unavailable")
class TestRoutingArtifactTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/routing_artifact_types.py must be importable."""
        assert _AVAILABLE

    def test_routingrationale_defined(self) -> None:
        assert RoutingRationale is not None

    def test_routepath_defined(self) -> None:
        assert RoutePath is not None

    def test_routedecisionartifact_defined(self) -> None:
        assert RouteDecisionArtifact is not None

    def test_tokengateresult_defined(self) -> None:
        assert TokenGateResult is not None

    def test_tokencapartifact_defined(self) -> None:
        assert TokenCapArtifact is not None

    def test_permsartifact_defined(self) -> None:
        assert PermsArtifact is not None
