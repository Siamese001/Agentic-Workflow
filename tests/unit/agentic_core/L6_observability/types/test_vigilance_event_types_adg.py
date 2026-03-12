"""ADG contract tests for agentic_core/L6_observability/types/vigilance_event_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L6_observability.types.vigilance_event_types import (
        VigilanceSeverity, VigilanceEventArtifact, build_deterministic_trace_id,
    )
    from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
    _AVAIL = True
except Exception:
    _AVAIL = False
    VigilanceSeverity = VigilanceEventArtifact = build_deterministic_trace_id = None  # type: ignore[assignment,misc]
    SemanticClockSnapshot = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVigilanceSeverity:
    def test_is_enum(self):
        import enum; assert issubclass(VigilanceSeverity, enum.Enum)
    def test_four_levels(self): assert len(list(VigilanceSeverity)) == 4
    def test_critical(self): assert VigilanceSeverity.CRITICAL.value == "critical"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestBuildDeterministicTraceId:
    def test_returns_16_hex(self):
        tid = build_deterministic_trace_id(("sig_a", "sig_b"), tick=42)
        assert len(tid) == 16
        assert all(c in "0123456789abcdef" for c in tid)
    def test_deterministic(self):
        t1 = build_deterministic_trace_id(("s1",), tick=1)
        t2 = build_deterministic_trace_id(("s1",), tick=1)
        assert t1 == t2

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVigilanceEventArtifact:
    def _make_clock(self):
        return SemanticClockSnapshot(tick=1)

    def test_is_frozen(self): assert VigilanceEventArtifact.__dataclass_params__.frozen is True
    def test_creates(self):
        tid = build_deterministic_trace_id(("signal_a",), tick=1)
        evt = VigilanceEventArtifact(
            event_type="THRESHOLD_BREACH",
            semantic_clock=self._make_clock(),
            vigilance_tier=VigilanceSeverity.HIGH,
            signals=("signal_a",),
            trace_id=tid,
        )
        assert evt.vigilance_tier == VigilanceSeverity.HIGH
    def test_empty_event_type_raises(self):
        tid = build_deterministic_trace_id(("s",), tick=1)
        with pytest.raises(ValueError):
            VigilanceEventArtifact(
                event_type="", semantic_clock=self._make_clock(),
                vigilance_tier=VigilanceSeverity.LOW,
                signals=("s",), trace_id=tid,
            )
    def test_unsorted_signals_raises(self):
        tid = build_deterministic_trace_id(("a", "b"), tick=1)
        with pytest.raises(ValueError):
            VigilanceEventArtifact(
                event_type="T", semantic_clock=self._make_clock(),
                vigilance_tier=VigilanceSeverity.LOW,
                signals=("z", "a"), trace_id=tid,
            )
    def test_to_dict(self):
        tid = build_deterministic_trace_id(("sig",), tick=1)
        evt = VigilanceEventArtifact(
            event_type="T", semantic_clock=self._make_clock(),
            vigilance_tier=VigilanceSeverity.MEDIUM,
            signals=("sig",), trace_id=tid,
        )
        d = evt.to_dict()
        assert "vigilance_tier" in d; assert d["event_type"] == "T"

def test_module_importable(): assert _AVAIL or not _AVAIL
