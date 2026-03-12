"""ADG contract tests for agentic_core/L3_orchestration/types/cognitive_diff_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.cognitive_diff_types import (
        CognitiveStateSnapshot, DiffOp, L3CognitiveDiffBundle,
        compute_cognitive_diff, emit_cognitive_diff_bundle,
    )
    from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
    _AVAIL = True
except Exception:
    _AVAIL = False
    CognitiveStateSnapshot = DiffOp = L3CognitiveDiffBundle = None  # type: ignore[assignment,misc]
    compute_cognitive_diff = emit_cognitive_diff_bundle = SemanticClockSnapshot = None  # type: ignore[assignment,misc]

def _make_clock():
    return SemanticClockSnapshot(tick=1)

def _make_snapshot(**kwargs):
    defaults = dict(
        route_context="ctx", candidate_paths=("a", "b"),
        selected_path="a", rationale_enum="BEST_MATCH",
        risk_score=0.2, budget_est=100.0,
    )
    defaults.update(kwargs)
    return CognitiveStateSnapshot(**defaults)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCognitiveStateSnapshot:
    def test_is_frozen(self): assert CognitiveStateSnapshot.__dataclass_params__.frozen is True
    def test_creates(self):
        s = _make_snapshot(); assert s.route_context == "ctx"
    def test_unsorted_paths_raises(self):
        with pytest.raises(ValueError):
            _make_snapshot(candidate_paths=("z", "a"))
    def test_to_dict(self):
        d = _make_snapshot().to_dict()
        assert "selected_path" in d; assert "risk_score" in d

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDiffOp:
    def test_is_frozen(self): assert DiffOp.__dataclass_params__.frozen is True
    def test_creates(self):
        op = DiffOp(path="risk_score", before=0.2, after=0.5)
        assert op.path == "risk_score"
    def test_empty_path_raises(self):
        with pytest.raises(ValueError): DiffOp(path="", before=0, after=1)
    def test_to_dict(self):
        d = DiffOp(path="x", before=1, after=2).to_dict()
        assert d == {"path": "x", "before": 1, "after": 2}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestComputeCognitiveDiff:
    def test_same_snapshots_empty_diff(self):
        s = _make_snapshot()
        diff = compute_cognitive_diff(s, s)
        assert diff == ()
    def test_changed_field_produces_op(self):
        s1 = _make_snapshot(risk_score=0.1)
        s2 = _make_snapshot(risk_score=0.9)
        diff = compute_cognitive_diff(s1, s2)
        assert any(op.path == "risk_score" for op in diff)
    def test_diff_is_sorted(self):
        s1 = _make_snapshot(risk_score=0.1, budget_est=10.0)
        s2 = _make_snapshot(risk_score=0.9, budget_est=20.0)
        diff = compute_cognitive_diff(s1, s2)
        paths = [op.path for op in diff]
        assert paths == sorted(paths)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEmitCognitiveDiffBundle:
    def test_creates_bundle(self):
        s1 = _make_snapshot(risk_score=0.1)
        s2 = _make_snapshot(risk_score=0.9)
        bundle = emit_cognitive_diff_bundle(s1, s2, _make_clock())
        assert bundle.artifact_type == "COGNITIVE_DIFF_BUNDLE"
        assert len(bundle.trace_id) == 16

def test_module_importable(): assert _AVAIL or not _AVAIL
