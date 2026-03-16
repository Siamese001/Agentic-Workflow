"""ADG-driven tests for L5_safety/enforcement/AdapterBase.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_adapter_base_adg")
_emit_applies_guardrail("p0", "test_adapter_base_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_adapter_base_adg", "policy_binding")
_emit_snapshots_state("p0", "test_adapter_base_adg", "state_snapshot")
emit_replay_key("p0", "test_adapter_base_adg")
emit_determinism_digest("p0", "test_adapter_base_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.AdapterBase import AdapterContext, AdapterResult


class TestAdapterContext:
    def test_creates_with_request_id(self):
        ctx = AdapterContext(request_id="req-001")
        assert ctx.request_id == "req-001"

    def test_risk_level_default_medium(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.risk_level == "medium"

    def test_bypass_validation_default_false(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.bypass_validation is False

    def test_metadata_default_empty(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.metadata == {}

    def test_timestamp_set(self):
        ctx = AdapterContext(request_id="r")
        assert ctx.timestamp is not None


class TestAdapterResult:
    def test_creates_success(self):
        r = AdapterResult(success=True, data={"key": "val"})
        assert r.success is True
        assert r.data == {"key": "val"}

    def test_creates_failure(self):
        r = AdapterResult(success=False, error="something went wrong")
        assert r.success is False
        assert r.error == "something went wrong"

    def test_data_default_none(self):
        r = AdapterResult(success=True)
        assert r.data is None

    def test_error_default_none(self):
        r = AdapterResult(success=True)
        assert r.error is None
