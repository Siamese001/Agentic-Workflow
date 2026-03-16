"""ADG-driven tests for L1_cognition/engines/perception_engine.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_perception_engine_adg")
_emit_applies_guardrail("p0", "test_perception_engine_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_perception_engine_adg", "policy_binding")
_emit_snapshots_state("p0", "test_perception_engine_adg", "state_snapshot")
emit_replay_key("p0", "test_perception_engine_adg")
emit_determinism_digest("p0", "test_perception_engine_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.perception_engine import PerceptionNode


class TestPerceptionNode:
    def test_creates(self):
        node = PerceptionNode()
        assert node.inputs_processed == 0
        assert node.cache == {}

    def test_has_process(self):
        assert hasattr(PerceptionNode, "process")

    def test_process_returns_dict(self):
        node = PerceptionNode()
        result = node.process(
            raw_input={"text": "hello"},
            context={"session_id": "s-1"},
        )
        assert isinstance(result, dict)
