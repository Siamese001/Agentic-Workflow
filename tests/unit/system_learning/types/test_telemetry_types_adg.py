"""ADG-driven tests for system_learning/types/telemetry_types.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from system_learning.types.telemetry_types import TelemetryEvent, TelemetrySlice


class TestTelemetryEvent:
    def test_creates(self):
        event = TelemetryEvent(ts_utc=1000, kind="heal", payload_hash="a" * 64)
        assert event.ts_utc == 1000
        assert event.kind == "heal"

    def test_is_frozen(self):
        event = TelemetryEvent(ts_utc=1000, kind="x", payload_hash="b" * 64)
        with pytest.raises(Exception):
            event.ts_utc = 9999


class TestTelemetrySlice:
    def test_importable(self):
        assert callable(TelemetrySlice)

    def test_has_fields(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(TelemetrySlice)}
        assert "slice_id" in fields
        assert "window_start_utc" in fields
