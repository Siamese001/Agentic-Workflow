"""ADG-driven tests for apps_rg/engines/gap_closure_engine.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_gap_closure_engine_adg")
_emit_applies_guardrail("p0", "test_gap_closure_engine_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_gap_closure_engine_adg", "policy_binding")
_emit_snapshots_state("p0", "test_gap_closure_engine_adg", "state_snapshot")
emit_replay_key("p0", "test_gap_closure_engine_adg")
emit_determinism_digest("p0", "test_gap_closure_engine_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from apps_rg.engines.gap_closure_engine import GapClosureEngine


class TestGapClosureEngine:
    def test_importable(self):
        assert callable(GapClosureEngine)

    def test_creates(self):
        engine = GapClosureEngine()
        assert engine is not None

    def test_has_execute(self):
        assert hasattr(GapClosureEngine, "execute")
