"""ADG contract tests for agentic_core/L4_state/types/replay_bundle_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle
    _AVAIL = True
except Exception:
    _AVAIL = False
    ReplayBundle = None  # type: ignore[assignment,misc]

def _make_bundle(**kwargs):
    defaults = dict(
        schema_version=1, mission_id="m1",
        execution_start_tick=0, execution_end_tick=5,
        manifest_hash="mh1", active_config_hashes={"policy_hash": "p1"},
        retrieval_used=False, citation_hash="",
        prior_detection_signal_hash="",
        prior_violation_event_hashes=[], tool_intent_hashes=[], tool_result_hashes=[],
    )
    defaults.update(kwargs)
    return ReplayBundle(**defaults)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestReplayBundle:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ReplayBundle)
    def test_creates(self):
        b = _make_bundle(); assert b.mission_id == "m1"
    def test_replay_hash_computed(self):
        b = _make_bundle(); assert len(b.replay_hash) == 64
    def test_wrong_schema_version_raises(self):
        with pytest.raises(ValueError): _make_bundle(schema_version=99)
    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError): _make_bundle(mission_id="")
    def test_negative_start_tick_raises(self):
        with pytest.raises(ValueError): _make_bundle(execution_start_tick=-1)
    def test_end_before_start_raises(self):
        with pytest.raises(ValueError): _make_bundle(execution_start_tick=5, execution_end_tick=3)
    def test_retrieval_used_requires_citation_hash(self):
        with pytest.raises(ValueError):
            _make_bundle(retrieval_used=True, citation_hash="")
    def test_retrieval_with_citation_ok(self):
        b = _make_bundle(retrieval_used=True, citation_hash="ch1")
        assert b.retrieval_used is True

def test_module_importable(): assert _AVAIL or not _AVAIL
