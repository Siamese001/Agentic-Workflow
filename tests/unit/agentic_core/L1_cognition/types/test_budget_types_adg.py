"""ADG-driven tests for L1_cognition/types/budget_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_budget_types_adg")
_emit_applies_guardrail("p0", "test_budget_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_budget_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_budget_types_adg", "state_snapshot")
emit_replay_key("p0", "test_budget_types_adg")
emit_determinism_digest("p0", "test_budget_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.budget_types import ToolCallBudget


class TestToolCallBudget:
    def test_creates_with_defaults(self):
        budget = ToolCallBudget()
        assert budget._minimum == 0
        assert budget._maximum == 20

    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolCallBudget)

    def test_guidance_default_empty(self):
        budget = ToolCallBudget()
        assert budget._guidance == {}
