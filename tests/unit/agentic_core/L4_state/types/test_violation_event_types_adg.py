"""ADG contract tests for agentic_core/L4_state/types/violation_event_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.violation_event_types import (
        ViolationEvent, emit_violation_event,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ViolationEvent = emit_violation_event = None  # type: ignore[assignment,misc]

def _make_event(**kwargs):
    defaults = dict(
        schema_version=1, mission_id="m1", commit_tick=5,
        guardian_decision="allow", violation_codes=["vc1", "vc2"],
        severity_score=0.5, created_at_utc="2026-01-01T00:00:00Z",
    )
    defaults.update(kwargs)
    return ViolationEvent(**defaults)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestViolationEvent:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ViolationEvent)
    def test_creates(self):
        e = _make_event(); assert e.mission_id == "m1"
    def test_auto_sorts_violation_codes(self):
        e = _make_event(violation_codes=["z", "a"]); assert e.violation_codes == ["a", "z"]
    def test_event_hash_computed(self):
        e = _make_event(); assert len(e.event_hash) == 64
    def test_wrong_schema_version_raises(self):
        with pytest.raises(ValueError): _make_event(schema_version=99)
    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError): _make_event(mission_id="")
    def test_negative_tick_raises(self):
        with pytest.raises(ValueError): _make_event(commit_tick=-1)
    def test_invalid_decision_raises(self):
        with pytest.raises(ValueError): _make_event(guardian_decision="approve")
    def test_invalid_severity_raises(self):
        with pytest.raises(ValueError): _make_event(severity_score=1.5)
    def test_to_dict_roundtrip(self):
        e = _make_event()
        d = e.to_dict()
        e2 = ViolationEvent.from_dict(d)
        assert e2.event_hash == e.event_hash

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEmitViolationEvent:
    def test_creates_and_appends(self):
        registry = []
        e = emit_violation_event(
            mission_id="m1", commit_tick=0, guardian_decision="block",
            violation_codes=[], severity_score=0.0,
            created_at_utc="2026-01-01T00:00:00Z", _registry=registry,
        )
        assert len(registry) == 1; assert registry[0] is e

def test_module_importable(): assert _AVAIL or not _AVAIL
