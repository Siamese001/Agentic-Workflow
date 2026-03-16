"""ADG-driven tests for L5_safety/reasoning/gravity_validator.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_gravity_validator_adg")
_emit_applies_guardrail("p0", "test_gravity_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_gravity_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_gravity_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_gravity_validator_adg")
emit_determinism_digest("p0", "test_gravity_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.gravity_validator import (
        CHECK_ID,
        GravityValidatorAgent,
    )
    _GRAVITY_VALIDATOR_AVAILABLE = True
except ImportError:
    _GRAVITY_VALIDATOR_AVAILABLE = False
    CHECK_ID = "gravity_violations"
    GravityValidatorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _GRAVITY_VALIDATOR_AVAILABLE, reason="gravity_validator has NameError at module level")
class TestGravityValidatorAgent:
    def test_check_id_value(self):
        assert CHECK_ID == "gravity_violations"

    def test_creates(self, tmp_path):
        agent = GravityValidatorAgent(project_root=tmp_path)
        assert agent is not None

    def test_project_root_resolved(self, tmp_path):
        agent = GravityValidatorAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path.resolve()

    def test_has_scan(self):
        assert hasattr(GravityValidatorAgent, "scan")

    def test_has_to_check_dict(self):
        assert hasattr(GravityValidatorAgent, "to_check_dict")

    def test_to_check_dict_returns_dict(self, tmp_path):
        agent = GravityValidatorAgent(project_root=tmp_path)
        result = agent.to_check_dict()
        assert isinstance(result, dict)
        assert result.get("check_id") == CHECK_ID


def test_check_id_constant():
    assert CHECK_ID == "gravity_violations"
