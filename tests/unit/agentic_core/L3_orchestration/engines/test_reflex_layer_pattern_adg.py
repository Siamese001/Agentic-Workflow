"""ADG-driven tests for L3_orchestration/engines/reflex_layer_pattern.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_reflex_layer_pattern_adg")
_emit_applies_guardrail("p0", "test_reflex_layer_pattern_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_reflex_layer_pattern_adg", "policy_binding")
_emit_snapshots_state("p0", "test_reflex_layer_pattern_adg", "state_snapshot")
emit_replay_key("p0", "test_reflex_layer_pattern_adg")
emit_determinism_digest("p0", "test_reflex_layer_pattern_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L3_orchestration.engines.reflex_layer_pattern import ReflexLayer


class TestReflexLayer:
    def test_creates(self):
        rl = ReflexLayer()
        assert rl.status == "healthy"
        assert rl.reflexes == []

    def test_register_reflex(self):
        rl = ReflexLayer()
        result = rl.register_reflex("event_x", lambda: "ok")
        assert result is True
        assert len(rl.reflexes) == 1

    def test_trigger_registered_reflex(self):
        rl = ReflexLayer()
        rl.register_reflex("ping", lambda: "pong")
        result = rl.trigger_reflex("ping")
        assert result["handled"] is True
        assert result["result"] == "pong"

    def test_trigger_unregistered_returns_not_handled(self):
        rl = ReflexLayer()
        result = rl.trigger_reflex("unknown")
        assert result["handled"] is False

    def test_get_status(self):
        rl = ReflexLayer()
        status = rl.get_status()
        assert status["status"] == "healthy"
        assert status["health"] == "ok"
