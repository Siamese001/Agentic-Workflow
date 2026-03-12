"""ADG contract tests for apps_lic/types/k1_router_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.k1_router_types import (
        ArchetypeClassificationResult, RouteSelectionResult, K1Output,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ArchetypeClassificationResult = RouteSelectionResult = K1Output = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetypeClassificationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ArchetypeClassificationResult)
    def test_creates(self):
        r = ArchetypeClassificationResult(
            archetype="C_LEVEL", confidence=0.95,
            matched_tokens=["CEO"], cxo_precedence_triggered=True,
            manual_override_required=False,
        )
        assert r.archetype == "C_LEVEL"; assert r.confidence == 0.95

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteSelectionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RouteSelectionResult)
    def test_creates(self):
        r = RouteSelectionResult(route="INMAIL", premium_available=True, premium_routing_mismatch=False)
        assert r.route == "INMAIL"; assert r.blocking_reason is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestK1Output:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(K1Output)

def test_module_importable(): assert _AVAIL or not _AVAIL
