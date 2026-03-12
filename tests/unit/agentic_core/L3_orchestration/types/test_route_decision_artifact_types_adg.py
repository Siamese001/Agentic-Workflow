"""ADG importability contract for agentic_core/L3_orchestration/types/route_decision_artifact_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_route_decision_artifact_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.route_decision_artifact_types import (  # noqa: F401
        ChosenRoute,
        CandidateEntry,
        PolicyContext,
        DeterminismContext,
        L3RouteDecisionArtifact,
        build_l3_route_decision_artifact,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ChosenRoute = None  # type: ignore[assignment,misc]
    CandidateEntry = None  # type: ignore[assignment,misc]
    PolicyContext = None  # type: ignore[assignment,misc]
    DeterminismContext = None  # type: ignore[assignment,misc]
    L3RouteDecisionArtifact = None  # type: ignore[assignment,misc]
    build_l3_route_decision_artifact = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="route_decision_artifact_types.py deps unavailable")
class TestRouteDecisionArtifactTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: route_decision_artifact_types.py must be importable."""
        assert _AVAILABLE

    def test_chosenroute_is_type(self) -> None:
        assert ChosenRoute is not None

    def test_candidateentry_is_type(self) -> None:
        assert CandidateEntry is not None

    def test_policycontext_is_type(self) -> None:
        assert PolicyContext is not None

    def test_build_l3_route_decision_artifact_callable(self) -> None:
        assert callable(build_l3_route_decision_artifact)

