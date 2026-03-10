"""
Unit tests for L6 Observability Vigilance Dispatcher - pure event dispatch.
"""

import pytest

from agentic_core.L6_observability.engines.vigilance_dispatcher import (
    VigilanceDispatcher,
    VigilanceEventArtifact,
    to_meta_payload,
)


@pytest.mark.unit
class TestVigilanceEventArtifact:
    """Test VigilanceEventArtifact dataclass and signal normalization."""

    def test_create_with_normalized_signals(self):
        """Test create normalizes signals to sorted unique."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123",
            signals=("signal3", "signal1", "signal2", "signal1"),  # duplicate and unsorted
            summary="Test event",
        )

        assert artifact.trace_id == "trace123"
        assert artifact.signals == ("signal1", "signal2", "signal3")  # sorted unique
        assert artifact.summary == "Test event"

    def test_signals_empty_tuple(self):
        """Test empty signals tuple remains empty."""
        artifact = VigilanceEventArtifact.create(trace_id="trace123", signals=(), summary="Empty signals")

        assert artifact.signals == ()

    def test_signals_single_element(self):
        """Test single signal remains unchanged."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1",), summary="Single signal"
        )

        assert artifact.signals == ("signal1",)

    def test_signals_already_sorted_unique(self):
        """Test already sorted unique signals remain unchanged."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2", "signal3"), summary="Already sorted"
        )

        assert artifact.signals == ("signal1", "signal2", "signal3")

    def test_signals_with_duplicates(self):
        """Test duplicate signals are removed."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123",
            signals=("signal1", "signal2", "signal1", "signal3", "signal2"),
            summary="With duplicates",
        )

        assert artifact.signals == ("signal1", "signal2", "signal3")

    def test_artifact_immutability(self):
        """Test artifact is immutable."""
        artifact = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Test"
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            artifact.trace_id = "changed"

        with pytest.raises(AttributeError):
            artifact.signals = ("changed",)

        with pytest.raises(AttributeError):
            artifact.summary = "changed"


@pytest.mark.unit
class TestVigilanceDispatcher:
    """Test VigilanceDispatcher pure dispatch behavior."""

    def test_dispatch_calls_enqueue_fn_once(self):
        """Test dispatch calls enqueue_fn exactly once with same object."""
        dispatcher = VigilanceDispatcher()
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Test event"
        )

        # Track calls to enqueue_fn
        calls = []

        def mock_enqueue_fn(artifact):
            calls.append(artifact)

        dispatcher.dispatch(event=event, enqueue_fn=mock_enqueue_fn)

        assert len(calls) == 1
        assert calls[0] is event  # Same object reference

    def test_dispatch_no_branching_logic(self):
        """Test dispatch has no branching logic - always calls enqueue."""
        dispatcher = VigilanceDispatcher()

        # Test with different event types
        events = [
            VigilanceEventArtifact.create("trace1", (), "empty"),
            VigilanceEventArtifact.create("trace2", ("signal1",), "single"),
            VigilanceEventArtifact.create("trace3", ("signal1", "signal2"), "multiple"),
        ]

        for event in events:
            calls = []

            def mock_enqueue_fn(artifact):
                calls.append(artifact)

            dispatcher.dispatch(event=event, enqueue_fn=mock_enqueue_fn)

            # Should always call enqueue exactly once
            assert len(calls) == 1
            assert calls[0] is event

    def test_dispatch_no_state_mutation(self):
        """Test dispatch does not mutate state or event."""
        dispatcher = VigilanceDispatcher()
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Original"
        )

        # Snapshot original state
        original_trace = event.trace_id
        original_signals = event.signals
        original_summary = event.summary

        def mock_enqueue_fn(artifact):
            # Verify event hasn't changed during dispatch
            assert artifact.trace_id == original_trace
            assert artifact.signals == original_signals
            assert artifact.summary == original_summary

        dispatcher.dispatch(event=event, enqueue_fn=mock_enqueue_fn)

        # Verify event unchanged after dispatch
        assert event.trace_id == original_trace
        assert event.signals == original_signals
        assert event.summary == original_summary


@pytest.mark.unit
class TestToMetaPayload:
    """Test to_meta_payload conversion function."""

    def test_adapter_output_stable_and_deterministic(self):
        """Test adapter output is stable and deterministic."""
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2", "signal3"), summary="Test event"
        )

        payload1 = to_meta_payload(event)
        payload2 = to_meta_payload(event)

        assert payload1 == payload2
        assert payload1 == {
            "trace_id": "trace123",
            "signals": ["signal1", "signal2", "signal3"],
            "summary": "Test event",
        }

    def test_adapter_no_mutation_of_event(self):
        """Test adapter does not mutate the event."""
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2"), summary="Original"
        )

        original_event = event

        payload = to_meta_payload(event)

        # Event should be unchanged
        assert event is original_event
        assert event.trace_id == "trace123"
        assert event.signals == ("signal1", "signal2")
        assert event.summary == "Original"

        # Payload should have converted tuple to list
        assert payload["signals"] == ["signal1", "signal2"]
        assert isinstance(payload["signals"], list)

    def test_adapter_with_empty_signals(self):
        """Test adapter with empty signals."""
        event = VigilanceEventArtifact.create(trace_id="trace123", signals=(), summary="Empty signals")

        payload = to_meta_payload(event)

        assert payload == {"trace_id": "trace123", "signals": [], "summary": "Empty signals"}

    def test_adapter_signals_order_matches_event(self):
        """Test signals list order matches event.signals (already sorted)."""
        event = VigilanceEventArtifact.create(
            trace_id="trace123", signals=("signal1", "signal2", "signal3"), summary="Ordered signals"
        )

        payload = to_meta_payload(event)

        # Order should match event.signals
        assert payload["signals"] == ["signal1", "signal2", "signal3"]
        assert list(event.signals) == payload["signals"]
