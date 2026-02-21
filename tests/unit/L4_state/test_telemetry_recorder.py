"""Unit tests for TelemetryRecorder.

Phase 1 Wave 1.3 test suite. Verifies durable telemetry,
outcome logging, reconciliation, and SHA-256 immutability.
"""

import pytest

from agentic_core.L4_state.enforcement.telemetry_recorder import (
    OutcomeRecord,
    ReconResult,
    TelemetryRecorder,
)


@pytest.mark.unit
class TestTelemetryRecorder:
    def setup_method(self):
        self.recorder = TelemetryRecorder()
        self.recorder.clear()  # ensure clean state

    def test_record_returns_sha256(self):
        data = {"test": "data"}
        event_id = self.recorder.record("test_event", data, commit_tick=123)
        assert isinstance(event_id, str)
        assert len(event_id) == 64  # SHA-256 hex length

    def test_same_event_returns_same_id(self):
        data = {"test": "data"}
        id1 = self.recorder.record("test_event", data, commit_tick=123)
        id2 = self.recorder.record("test_event", data, commit_tick=123)
        assert id1 == id2

    def test_different_data_returns_different_ids(self):
        id1 = self.recorder.record("test_event", {"a": 1}, commit_tick=123)
        id2 = self.recorder.record("test_event", {"a": 2}, commit_tick=123)
        assert id1 != id2

    def test_get_events_returns_all(self):
        self.recorder.record("event1", {}, commit_tick=1)
        self.recorder.record("event2", {}, commit_tick=2)
        events = self.recorder.get_events()
        assert len(events) == 2
        assert events[0]["event_type"] == "event1"
        assert events[1]["event_type"] == "event2"

    def test_get_events_filters_by_type(self):
        self.recorder.record("event1", {}, commit_tick=1)
        self.recorder.record("event2", {}, commit_tick=2)
        events = self.recorder.get_events(event_type="event1")
        assert len(events) == 1
        assert events[0]["event_type"] == "event1"

    def test_get_events_limit(self):
        for i in range(5):
            self.recorder.record(f"event{i}", {}, commit_tick=i)
        events = self.recorder.get_events(limit=3)
        assert len(events) == 3
        # Should return last 3 events
        assert events[0]["event_type"] == "event2"
        assert events[2]["event_type"] == "event4"

    def test_log_async_requires_l2_commit_hash(self):
        record = OutcomeRecord(
            execution_latency_ms=100.0,
            outcome_accuracy=0.95,
            compute_cost_tokens=50,
            human_correction_rate=0.1,
            state_diff={},
            l2_commit_hash="",  # Empty hash
            record_hash="abc123",
        )
        with pytest.raises(ValueError, match="l2_commit_hash"):
            self.recorder.log_async(record)

    def test_log_async_stores_record(self):
        record = OutcomeRecord(
            execution_latency_ms=100.0,
            outcome_accuracy=0.95,
            compute_cost_tokens=50,
            human_correction_rate=0.1,
            state_diff={"key": "value"},
            l2_commit_hash="hash123",
            record_hash="record456",
        )
        self.recorder.log_async(record)

        events = self.recorder.get_events(event_type="outcome_record")
        assert len(events) == 1
        assert events[0]["record"]["l2_commit_hash"] == "hash123"

    def test_reconcile_detects_ghost_mutation(self):
        result = self.recorder.reconcile("hash1", "hash2")
        assert isinstance(result, ReconResult)
        assert result.ghost_mutation_detected is True
        assert "Ghost mutation detected" in result.details
        assert result.l4_state_hash == "hash1"
        assert result.actual_hash == "hash2"

    def test_reconcile_successful(self):
        result = self.recorder.reconcile("hash1", "hash1")
        assert result.ghost_mutation_detected is False
        assert "successful" in result.details

    def test_reconcile_logs_event(self):
        self.recorder.reconcile("hash1", "hash2")
        events = self.recorder.get_events(event_type="reconciliation")
        assert len(events) == 1
        assert events[0]["data"]["ghost_detected"] is True

    def test_clear_resets_all_data(self):
        self.recorder.record("test", {}, commit_tick=1)
        assert self.recorder.get_events()
        self.recorder.clear()
        assert not self.recorder.get_events()

    def test_record_includes_commit_tick(self):
        self.recorder.record("test", {}, commit_tick=42)
        events = self.recorder.get_events()
        assert events[0]["commit_tick"] == 42

    def test_record_timestamp_optional(self):
        # By default, no timestamp is included
        self.recorder.record("test", {}, commit_tick=1)
        events = self.recorder.get_events()
        assert "timestamp" not in events[0]

        # Caller can supply timestamp explicitly
        self.recorder.record("test", {}, commit_tick=2, timestamp=1234567890)
        events = self.recorder.get_events()
        assert events[1]["timestamp"] == 1234567890
