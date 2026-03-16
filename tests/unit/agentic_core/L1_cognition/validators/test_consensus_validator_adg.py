"""ADG-driven tests for L1_cognition/validators/consensus_validator.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_consensus_validator_adg")
_emit_applies_guardrail("p0", "test_consensus_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_consensus_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_consensus_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_consensus_validator_adg")
emit_determinism_digest("p0", "test_consensus_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.consensus_validator import ConsensusEngine


class TestConsensusEngine:
    def test_creates_with_defaults(self):
        engine = ConsensusEngine()
        assert engine is not None

    def test_critical_keywords_is_list(self):
        assert isinstance(ConsensusEngine.CRITICAL_KEYWORDS, list)

    def test_majority_threshold(self):
        assert 0 < ConsensusEngine.MAJORITY_THRESHOLD <= 1.0

    def test_model_check_config_is_dict(self):
        assert isinstance(ConsensusEngine.MODEL_CHECK_CONFIG, dict)
