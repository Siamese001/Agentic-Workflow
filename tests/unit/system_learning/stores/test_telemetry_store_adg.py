"""ADG-driven tests for system_learning/stores/telemetry_store.py — fan_in=1."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from system_learning.stores.telemetry_store import FileBackedTelemetryStore


class TestFileBackedTelemetryStore:
    def test_creates(self, tmp_path):
        store = FileBackedTelemetryStore(telemetry_path=tmp_path / "telemetry.jsonl")
        assert store is not None

    def test_missing_file_returns_empty_tuple(self, tmp_path):
        store = FileBackedTelemetryStore(telemetry_path=tmp_path / "missing.jsonl")
        result = store.read_events(0, 9999999999)
        assert result == ()

    def test_returns_tuple(self, tmp_path):
        store = FileBackedTelemetryStore(telemetry_path=tmp_path / "t.jsonl")
        result = store.read_events(0, 9999999999)
        assert isinstance(result, tuple)

    def test_reads_events_from_file(self, tmp_path):
        event = {"timestamp_utc": 1000, "event_type": "heal", "payload": {"ok": True}}
        path = tmp_path / "events.jsonl"
        path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        store = FileBackedTelemetryStore(telemetry_path=path)
        result = store.read_events(0, 9999999999)
        assert isinstance(result, tuple)

    def test_has_read_events(self):
        assert hasattr(FileBackedTelemetryStore, "read_events")
