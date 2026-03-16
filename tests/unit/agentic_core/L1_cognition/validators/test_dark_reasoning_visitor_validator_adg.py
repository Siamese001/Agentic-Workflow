"""ADG-driven tests for L1_cognition/validators/dark_reasoning_visitor_validator.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_dark_reasoning_visitor_validator_adg")
_emit_applies_guardrail("p0", "test_dark_reasoning_visitor_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_dark_reasoning_visitor_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_dark_reasoning_visitor_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_dark_reasoning_visitor_validator_adg")
emit_determinism_digest("p0", "test_dark_reasoning_visitor_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.dark_reasoning_visitor_validator import (
    check_dark_reasoning,
)


class TestCheckDarkReasoning:
    def test_returns_list(self, tmp_path):
        dummy = tmp_path / "dummy.py"
        dummy.write_text("x = 1\n")
        result = check_dark_reasoning(dummy)
        assert isinstance(result, list)

    def test_non_l1_l2_l3_returns_empty(self, tmp_path):
        dummy = tmp_path / "L0_routing" / "some_file.py"
        dummy.parent.mkdir(parents=True)
        dummy.write_text("x = 1\n")
        result = check_dark_reasoning(dummy)
        assert result == []

    def test_callable(self):
        assert callable(check_dark_reasoning)
