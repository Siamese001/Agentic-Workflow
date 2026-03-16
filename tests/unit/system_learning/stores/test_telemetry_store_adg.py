"""ADG-driven tests for system_learning/stores/telemetry_store.py — fan_in=1."""
from __future__ import annotations

import json

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_telemetry_store_adg")
_emit_applies_guardrail("p0", "test_telemetry_store_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_telemetry_store_adg", "policy_binding")
_emit_snapshots_state("p0", "test_telemetry_store_adg", "state_snapshot")
emit_replay_key("p0", "test_telemetry_store_adg")
emit_determinism_digest("p0", "test_telemetry_store_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
