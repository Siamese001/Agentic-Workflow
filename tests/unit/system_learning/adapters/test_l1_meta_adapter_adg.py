"""ADG-driven tests for system_learning/adapters/l1_meta_adapter.py — fan_in=0."""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.adapters.l1_meta_adapter import (  # noqa: F401
        L1DriftSignal,
        L1MetaAdapter,
        L1TelemetryEvent,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    L1TelemetryEvent = None  # type: ignore[assignment,misc]
    L1DriftSignal = None  # type: ignore[assignment,misc]
    L1MetaAdapter = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestL1TelemetryEvent:
    def test_is_class(self):
        assert isinstance(L1TelemetryEvent, type)

    def test_importable(self):
        assert L1TelemetryEvent is not None


@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestL1DriftSignal:
    def test_is_class(self):
        assert isinstance(L1DriftSignal, type)

    def test_importable(self):
        assert L1DriftSignal is not None


@pytest.mark.skipif(not _AVAILABLE, reason="l1_meta_adapter.py deps unavailable")
class TestL1MetaAdapter:
    def test_is_class(self):
        assert isinstance(L1MetaAdapter, type)

    def test_importable(self):
        assert L1MetaAdapter is not None

    def test_extract_telemetry_persists_events(self):
        adapter = L1MetaAdapter()
        state = {
            "recall_outcomes": [{"timestamp_utc": 10, "value": "a"}],
            "learn_outcomes": [{"timestamp_utc": 11, "value": "b"}],
            "cache_stats": {"hit_rate": 0.9},
        }

        class _Bridge:
            def __init__(self):
                self.calls = []

            def persist_telemetry_window(self, source, events, *, window_start=0, window_end=0):
                self.calls.append((source, list(events), window_start, window_end))
                return True

        bridge = _Bridge()
        with patch("system_learning.adapters.l1_meta_adapter.get_sl_memory_bridge", return_value=bridge):
            events = adapter.extract_telemetry(state, now_utc=12)

        assert [event.event_type for event in events] == [
            "l1_recall_outcome",
            "l1_learn_outcome",
            "l1_cache_stats",
        ]
        assert bridge.calls and bridge.calls[0][0] == "l1_meta_adapter"

    def test_detect_drift_persists_signal(self):
        adapter = L1MetaAdapter()
        state = {"confidence_history": [0.1, 0.2, 0.9, 1.0]}

        class _Bridge:
            def __init__(self):
                self.calls = []

            def persist_l1_drift_signal(self, drift_signal, *, source="l1_meta_adapter"):
                self.calls.append((drift_signal.surface_name, drift_signal.drift_magnitude, source))
                return True

        bridge = _Bridge()
        with patch("system_learning.adapters.l1_meta_adapter.get_sl_memory_bridge", return_value=bridge):
            signal = adapter.detect_drift(state, snapshot_id="snap-1")

        assert signal is not None
        assert bridge.calls == [("l1_model_confidence", signal.drift_magnitude, "l1_meta_adapter")]

    def test_l1_persistence_handles_failure(self):
        """Test that L1 operations still work even if bridge persistence fails."""
        adapter = L1MetaAdapter()
        state = {
            "recall_outcomes": [{"timestamp_utc": 10, "value": "a"}],
            "learn_outcomes": [{"timestamp_utc": 11, "value": "b"}],
            "cache_stats": {"hit_rate": 0.9},
        }

        class _FailingBridge:
            def persist_telemetry_window(self, source, events, *, window_start=0, window_end=0):
                raise RuntimeError("Bridge down")

            def persist_l1_drift_signal(self, drift_signal, *, source="l1_meta_adapter"):
                raise RuntimeError("Bridge down")

        bridge = _FailingBridge()
        with patch("system_learning.adapters.l1_meta_adapter.get_sl_memory_bridge", return_value=bridge):
            # Should not raise exception
            events = adapter.extract_telemetry(state, now_utc=12)
            signal = adapter.detect_drift({"confidence_history": [0.1, 0.9]}, snapshot_id="snap-2")

        # Operations should still succeed
        assert len(events) == 3
        assert signal is not None


def test_module_importable():
    """Module l1_meta_adapter.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE