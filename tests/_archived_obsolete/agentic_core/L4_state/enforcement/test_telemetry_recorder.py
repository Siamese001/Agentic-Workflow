"""Tests for TelemetryRecorder - telemetry event recording."""
import pytest
from agentic_core.L4_state.enforcement.telemetry_recorder import TelemetryRecorder


class TestTelemetryRecorder:
    def test_init(self):
        r = TelemetryRecorder()
        assert r is not None

    def test_record_event(self):
        r = TelemetryRecorder()
        r.record(event_type="agent_start", payload={"agent_id": "a1"})
        events = r.get_events()
        assert len(events) == 1

    def test_record_multiple(self):
        r = TelemetryRecorder()
        r.record(event_type="x", payload={})
        r.record(event_type="y", payload={})
        assert len(r.get_events()) == 2

    def test_filter_by_type(self):
        r = TelemetryRecorder()
        r.record(event_type="start", payload={})
        r.record(event_type="end", payload={})
        starts = r.filter_by_type("start")
        assert len(starts) == 1

    def test_clear(self):
        r = TelemetryRecorder()
        r.record(event_type="x", payload={})
        r.clear()
        assert len(r.get_events()) == 0

    def test_export_json(self):
        r = TelemetryRecorder()
        r.record(event_type="x", payload={"k": "v"})
        data = r.export_json()
        assert isinstance(data, str)

    def test_record_with_timestamp(self):
        r = TelemetryRecorder()
        r.record(event_type="x", payload={})
        events = r.get_events()
        assert "timestamp" in events[0] or "ts" in events[0]
