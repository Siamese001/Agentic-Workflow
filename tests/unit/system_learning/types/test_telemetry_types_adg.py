"""ADG-driven tests for system_learning/types/telemetry_types.py — fan_in=1."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_telemetry_types_adg")
_emit_applies_guardrail("p0", "test_telemetry_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_telemetry_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_telemetry_types_adg", "state_snapshot")
emit_replay_key("p0", "test_telemetry_types_adg")
emit_determinism_digest("p0", "test_telemetry_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
