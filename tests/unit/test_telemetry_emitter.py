"""
Unit tests for L1 Cognition Telemetry Emitter - write-only, ZERO-decision component.
"""

import pytest

from agentic_core.L1_cognition.telemetry.telemetry_emitter import (
    TelemetryEmitter,
    TelemetryEvent,
    compute_event_hash,
)


@pytest.mark.unit
class TestComputeEventHash:
    """Test compute_event_hash deterministic hash calculation."""

    def test_deterministic_hash_same_inputs(self):
        """Test same inputs produce identical hash."""
        details = {"key1": "value1", "key2": "value2"}

        hash1 = compute_event_hash("stage1", "kind1", 123, details)
        hash2 = compute_event_hash("stage1", "kind1", 123, details)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_different_inputs_produce_different_hashes(self):
        """Test different inputs produce different hashes."""
        details = {"key": "value"}

        hash1 = compute_event_hash("stage1", "kind1", 123, details)
        hash2 = compute_event_hash("stage2", "kind1", 123, details)  # Different stage

        assert hash1 != hash2

    def test_details_key_order_does_not_affect_hash(self):
        """Test details key order does not affect event hash."""
        details1 = {"z": "last", "a": "first", "m": "middle"}
        details2 = {"a": "first", "m": "middle", "z": "last"}

        hash1 = compute_event_hash("stage", "kind", 42, details1)
        hash2 = compute_event_hash("stage", "kind", 42, details2)

        assert hash1 == hash2


@pytest.mark.unit
class TestTelemetryEvent:
    """Test TelemetryEvent immutable dataclass."""

    def test_create_with_deterministic_event_hash(self):
        """Test event creation with deterministic hash."""
        details = {"metric": "cpu_usage", "value": 85.5}

        event = TelemetryEvent.create(
            trace_id="trace123", stage="processing", kind="metric", commit_tick=42, details=details
        )

        assert event.trace_id == "trace123"
        assert event.stage == "processing"
        assert event.kind == "metric"
        assert event.commit_tick == 42
        assert event.details == details
        assert event.event_hash is not None
        assert len(event.event_hash) == 64

    def test_determinism_same_inputs_same_hash(self):
        """Test determinism: same inputs => same event_hash."""
        details = {"action": "process", "items": 10}

        event1 = TelemetryEvent.create(
            trace_id="trace123", stage="stage1", kind="action", commit_tick=100, details=details
        )

        event2 = TelemetryEvent.create(
            trace_id="trace123", stage="stage1", kind="action", commit_tick=100, details=details
        )

        assert event1.event_hash == event2.event_hash

    def test_details_key_order_does_not_affect_event_hash(self):
        """Test details key order does not affect event hash."""
        details1 = {"z": "last", "a": "first"}
        details2 = {"a": "first", "z": "last"}

        event1 = TelemetryEvent.create(
            trace_id="trace456", stage="test", kind="order_test", commit_tick=1, details=details1
        )

        event2 = TelemetryEvent.create(
            trace_id="trace456", stage="test", kind="order_test", commit_tick=1, details=details2
        )

        assert event1.event_hash == event2.event_hash

    def test_no_mutation_details_deep_copied(self):
        """Test modifying original details dict after construction does not change stored details."""
        original_details = {"counter": 0, "status": "initial"}

        event = TelemetryEvent.create(
            trace_id="trace789", stage="mutation_test", kind="test", commit_tick=999, details=original_details
        )

        # Modify original details after event creation
        original_details["counter"] = 999
        original_details["status"] = "modified"
        original_details["new_field"] = "added"

        # Event details should remain unchanged
        assert event.details["counter"] == 0
        assert event.details["status"] == "initial"
        assert "new_field" not in event.details

    def test_event_immutability(self):
        """Test event is immutable."""
        details = {"test": "value"}
        event = TelemetryEvent.create(
            trace_id="trace", stage="stage", kind="kind", commit_tick=1, details=details
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            event.trace_id = "changed"

        with pytest.raises(AttributeError):
            event.stage = "changed"

        with pytest.raises(AttributeError):
            event.kind = "changed"

        with pytest.raises(AttributeError):
            event.commit_tick = 999

        with pytest.raises(AttributeError):
            event.details = {"changed": "value"}

        with pytest.raises(AttributeError):
            event.event_hash = "changed"


@pytest.mark.unit
class TestTelemetryEmitter:
    """Test TelemetryEmitter write-only behavior."""

    def test_emit_calls_injected_record_fn_exactly_once(self):
        """Test emit calls injected record_fn exactly once with same object."""
        emitter = TelemetryEmitter()

        details = {"metric": "test", "value": 42}
        event = TelemetryEvent.create(
            trace_id="trace123", stage="test_stage", kind="test_kind", commit_tick=1, details=details
        )

        # Track calls to record_fn
        calls = []

        def mock_record_fn(telemetry_event):
            calls.append(telemetry_event)

        emitter.emit(event=event, record_fn=mock_record_fn)

        # Should call record_fn exactly once
        assert len(calls) == 1
        assert calls[0] is event  # Same object reference

    def test_emit_performs_no_mutation(self):
        """Test emit performs no mutation of event."""
        emitter = TelemetryEmitter()

        details = {"original": "value"}
        event = TelemetryEvent.create(
            trace_id="trace456", stage="mutation_test", kind="test", commit_tick=123, details=details
        )

        # Snapshot original event
        original_hash = event.event_hash
        original_details = event.details.copy()

        def mock_record_fn(telemetry_event):
            # Verify event unchanged during emit
            assert telemetry_event.event_hash == original_hash
            assert telemetry_event.details == original_details

        emitter.emit(event=event, record_fn=mock_record_fn)

        # Verify event unchanged after emit
        assert event.event_hash == original_hash
        assert event.details == original_details

    def test_emit_no_branching_logic(self):
        """Test emit has no branching logic - always calls record_fn."""
        emitter = TelemetryEmitter()

        # Test with different event types
        events = [
            TelemetryEvent.create("trace1", "stage1", "kind1", 1, {"a": 1}),
            TelemetryEvent.create("trace2", "stage2", "kind2", 2, {"b": 2}),
            TelemetryEvent.create("trace3", "stage3", "kind3", 3, {"c": 3}),
        ]

        for event in events:
            calls = []

            def mock_record_fn(telemetry_event):
                calls.append(telemetry_event)

            emitter.emit(event=event, record_fn=mock_record_fn)

            # Should always call record_fn exactly once
            assert len(calls) == 1
            assert calls[0] is event

    def test_build_event_convenience_constructor(self):
        """Test build_event convenience constructor."""
        emitter = TelemetryEmitter()

        details = {"convenience": "test"}
        event = emitter.build_event(
            trace_id="trace789",
            stage="convenience_stage",
            kind="convenience_kind",
            commit_tick=456,
            details=details,
        )

        # Verify event properties
        assert event.trace_id == "trace789"
        assert event.stage == "convenience_stage"
        assert event.kind == "convenience_kind"
        assert event.commit_tick == 456
        assert event.details == details
        assert event.event_hash is not None
        assert len(event.event_hash) == 64

        # Verify it's a proper TelemetryEvent
        assert isinstance(event, TelemetryEvent)

    def test_build_event_equivalent_to_direct_create(self):
        """Test build_event produces same result as direct TelemetryEvent.create."""
        emitter = TelemetryEmitter()

        details = {"equivalence": "test"}

        # Create event using build_event
        event1 = emitter.build_event(
            trace_id="trace999", stage="equivalence", kind="test", commit_tick=789, details=details
        )

        # Create event using direct create
        event2 = TelemetryEvent.create(
            trace_id="trace999", stage="equivalence", kind="test", commit_tick=789, details=details
        )

        # Should be identical
        assert event1.trace_id == event2.trace_id
        assert event1.stage == event2.stage
        assert event1.kind == event2.kind
        assert event1.commit_tick == event2.commit_tick
        assert event1.details == event2.details
        assert event1.event_hash == event2.event_hash
