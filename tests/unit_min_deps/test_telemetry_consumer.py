"""Unit tests for system_learning.engines.telemetry_consumer."""

import pytest

from system_learning.engines.telemetry_consumer import (
    TelemetryConsumerError,
    consume_telemetry,
)

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake TelemetryStore
# =============================================================================


class FakeTelemetryStore:
    """In-memory fake telemetry store for testing."""

    def __init__(self, events: list[tuple[int, str, bytes]]):
        self._events = events

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        """Read events within window."""
        # Filter events within window
        filtered = [
            (ts, kind, payload)
            for ts, kind, payload in self._events
            if window_start_utc <= ts < window_end_utc
        ]
        return tuple(filtered)


# =============================================================================
# Tests
# =============================================================================


class TestTelemetryConsumer:
    def test_deterministic_slice_id_across_two_calls(self):
        """Same backing data produces identical slice_id across two calls."""
        events = [
            (1700000000, "metric", b"cpu=50"),
            (1700000100, "metric", b"mem=1000"),
            (1700000200, "error", b"timeout"),
        ]
        store = FakeTelemetryStore(events)

        slice1 = consume_telemetry(store, 1700000000, 1700000300)
        slice2 = consume_telemetry(store, 1700000000, 1700000300)

        assert slice1.slice_id == slice2.slice_id
        assert slice1.slice_hash == slice2.slice_hash
        assert slice1.slice_id == slice1.slice_hash

    def test_sorting_stable_and_canonical(self):
        """Events are sorted deterministically by (ts_utc, kind, payload_hash)."""
        # Create events in non-canonical order
        events = [
            (1700000200, "error", b"timeout"),
            (1700000000, "metric", b"cpu=50"),
            (1700000100, "metric", b"mem=1000"),
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700000000, 1700000300)

        # Events should be sorted by ts_utc
        assert len(slice_obj.events) == 3
        assert slice_obj.events[0].ts_utc == 1700000000
        assert slice_obj.events[1].ts_utc == 1700000100
        assert slice_obj.events[2].ts_utc == 1700000200

    def test_invalid_window_rejected(self):
        """Invalid window (start >= end) raises TelemetryConsumerError."""
        store = FakeTelemetryStore([])

        with pytest.raises(TelemetryConsumerError, match="Invalid window"):
            consume_telemetry(store, 1700003600, 1700000000)

    def test_empty_window_produces_empty_slice(self):
        """Empty window produces slice with no events."""
        events = [
            (1700000000, "metric", b"cpu=50"),
        ]
        store = FakeTelemetryStore(events)

        # Window that excludes all events
        slice_obj = consume_telemetry(store, 1700010000, 1700020000)

        assert len(slice_obj.events) == 0

    def test_window_filtering(self):
        """Events outside window are excluded."""
        events = [
            (1700000000, "metric", b"cpu=50"),  # Before window
            (1700001000, "metric", b"mem=1000"),  # In window
            (1700002000, "error", b"timeout"),  # In window
            (1700005000, "metric", b"cpu=60"),  # After window
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700001000, 1700003000)

        # Only 2 events should be in slice
        assert len(slice_obj.events) == 2
        assert slice_obj.events[0].ts_utc == 1700001000
        assert slice_obj.events[1].ts_utc == 1700002000

    def test_payload_hash_computed(self):
        """payload_hash is SHA-256 of payload bytes."""
        events = [
            (1700000000, "metric", b"test_payload"),
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700000000, 1700001000)

        # payload_hash should be a valid SHA-256 hex digest
        assert len(slice_obj.events) == 1
        payload_hash = slice_obj.events[0].payload_hash
        assert len(payload_hash) == 64
        assert all(c in "0123456789abcdef" for c in payload_hash)

    def test_same_timestamp_different_kind_sorted(self):
        """Events with same timestamp are sorted by kind."""
        events = [
            (1700000000, "zzz", b"payload1"),
            (1700000000, "aaa", b"payload2"),
            (1700000000, "mmm", b"payload3"),
        ]
        store = FakeTelemetryStore(events)

        slice_obj = consume_telemetry(store, 1700000000, 1700001000)

        # Should be sorted alphabetically by kind
        assert slice_obj.events[0].kind == "aaa"
        assert slice_obj.events[1].kind == "mmm"
        assert slice_obj.events[2].kind == "zzz"


class TestDeterminism:
    def test_consume_telemetry_deterministic(self):
        """consume_telemetry produces identical results across multiple calls."""
        events = [
            (1700000000, "metric", b"cpu=50"),
            (1700000100, "metric", b"mem=1000"),
            (1700000200, "error", b"timeout"),
        ]
        store = FakeTelemetryStore(events)

        slice1 = consume_telemetry(store, 1700000000, 1700000300)
        slice2 = consume_telemetry(store, 1700000000, 1700000300)
        slice3 = consume_telemetry(store, 1700000000, 1700000300)

        assert slice1.slice_id == slice2.slice_id == slice3.slice_id
        assert slice1.slice_hash == slice2.slice_hash == slice3.slice_hash
