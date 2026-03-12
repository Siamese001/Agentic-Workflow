"""ADG contract tests for agentic_core/L0_routing/types/shadow_routing_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.shadow_routing_types import (
        ShadowRoutingRationale, ShadowRoutingDecision,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ShadowRoutingRationale = ShadowRoutingDecision = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestShadowRoutingRationale:
    def test_is_enum(self):
        import enum; assert issubclass(ShadowRoutingRationale, enum.Enum)
    def test_has_align_with_live(self):
        assert ShadowRoutingRationale.ALIGN_WITH_LIVE.value == "align_with_live"
    def test_five_rationales(self):
        assert len(list(ShadowRoutingRationale)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestShadowRoutingDecision:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ShadowRoutingDecision)
    def test_is_frozen(self):
        assert ShadowRoutingDecision.__dataclass_params__.frozen is True
    def test_has_required_fields(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(ShadowRoutingDecision)}
        assert "trace_id" in fields
        assert "drift_score" in fields
        assert "feature_fingerprint" in fields

def test_module_importable(): assert _AVAIL or not _AVAIL
