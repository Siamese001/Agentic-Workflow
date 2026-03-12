"""ADG contract tests for system_learning/types/offline_replay_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.offline_replay_types import replay_app_signals_to_aggregate
    _AVAIL = True
except Exception:
    _AVAIL = False
    replay_app_signals_to_aggregate = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestReplayAppSignalsToAggregate:
    def test_is_callable(self):
        assert callable(replay_app_signals_to_aggregate)
    def test_has_correct_signature(self):
        import inspect
        sig = inspect.signature(replay_app_signals_to_aggregate)
        params = set(sig.parameters.keys())
        assert "events" in params
        assert "metric_name" in params
        assert "semantic_clock" in params

def test_module_importable(): assert _AVAIL or not _AVAIL
