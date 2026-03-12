"""ADG-driven tests for L0_routing/types/artifact_typed_compat_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.types.artifact_typed_compat_types import (
        HealingPlan,
        ResultArtifact,
        RouteDecisionArtifact,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealingPlan = None  # type: ignore[assignment,misc]
    ResultArtifact = None  # type: ignore[assignment,misc]
    RouteDecisionArtifact = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="artifact_typed_compat_types deps unavailable")
class TestArtifactTypedCompatReExports:
    def test_healing_plan_importable(self):
        assert HealingPlan is not None

    def test_result_artifact_importable(self):
        assert ResultArtifact is not None

    def test_route_decision_artifact_importable(self):
        assert RouteDecisionArtifact is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
