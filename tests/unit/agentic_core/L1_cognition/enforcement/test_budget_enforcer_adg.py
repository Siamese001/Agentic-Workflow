"""ADG-driven tests for L1_cognition/enforcement/budget_enforcer.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_budget_enforcer_adg")
_emit_applies_guardrail("p0", "test_budget_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_budget_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_budget_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_budget_enforcer_adg")
emit_determinism_digest("p0", "test_budget_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.enforcement.budget_enforcer import EnforceBudgetLimits


class TestEnforceBudgetLimits:
    def test_importable(self):
        assert callable(EnforceBudgetLimits)

    def test_creates(self):
        obj = EnforceBudgetLimits()
        assert obj is not None
