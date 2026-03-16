"""ADG-driven tests for L1_cognition/validators/semantic_gatekeeper_validator.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_semantic_gatekeeper_validator_adg")
_emit_applies_guardrail("p0", "test_semantic_gatekeeper_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_gatekeeper_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_gatekeeper_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_semantic_gatekeeper_validator_adg")
emit_determinism_digest("p0", "test_semantic_gatekeeper_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.semantic_gatekeeper_validator import semantic_gatekeeper


class TestSemanticGatekeeper:
    def test_creates(self):
        gk = semantic_gatekeeper(config={"mission_scope": "software_development"})
        assert gk.mission_scope == "software_development"

    def test_creates_with_default_scope(self):
        gk = semantic_gatekeeper(config={})
        assert gk.mission_scope == "software_development"

    def test_has_check_drift(self):
        assert hasattr(semantic_gatekeeper, "check_drift")
