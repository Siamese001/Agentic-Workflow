"""ADG-driven tests for L1_cognition/validators/truth_keeper_validator.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_truth_keeper_validator_adg")
_emit_applies_guardrail("p0", "test_truth_keeper_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_truth_keeper_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_truth_keeper_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_truth_keeper_validator_adg")
emit_determinism_digest("p0", "test_truth_keeper_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.truth_keeper_validator import TruthKeeper


class TestTruthKeeper:
    def test_creates_with_defaults(self):
        tk = TruthKeeper()
        assert tk.llm_client is None
        assert tk.api_key is None

    def test_creates_with_llm_client(self):
        mock_client = object()
        tk = TruthKeeper(llm_client=mock_client)
        assert tk.llm_client is mock_client

    def test_has_check_file_consistency(self):
        assert hasattr(TruthKeeper, "check_file_consistency")
