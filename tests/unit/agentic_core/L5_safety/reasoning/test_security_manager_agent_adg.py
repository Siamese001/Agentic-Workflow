"""ADG-driven tests for L5_safety/reasoning/SecurityManagerAgent.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_security_manager_agent_adg")
_emit_applies_guardrail("p0", "test_security_manager_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_security_manager_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_security_manager_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_security_manager_agent_adg")
emit_determinism_digest("p0", "test_security_manager_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.SecurityManagerAgent import (
    PermissionLevel,
    SecurityAction,
    SecurityManagerAgent,
)


class TestPermissionLevel:
    def test_none_value_0(self):
        assert PermissionLevel.NONE.value == 0

    def test_admin_highest(self):
        assert PermissionLevel.ADMIN.value > PermissionLevel.SECURE_WRITER.value

    def test_all_levels_present(self):
        for level in ("NONE", "SECURE_READER", "SECURE_WRITER", "ADMIN"):
            assert hasattr(PermissionLevel, level)


class TestSecurityAction:
    def test_read_config_member(self):
        assert hasattr(SecurityAction, "READ_CONFIG")

    def test_write_config_member(self):
        assert hasattr(SecurityAction, "WRITE_CONFIG")

    def test_create_checkpoint_member(self):
        assert hasattr(SecurityAction, "CREATE_CHECKPOINT")


class TestSecurityManagerAgent:
    def test_creates(self):
        agent = SecurityManagerAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(SecurityManagerAgent, "heal_repository")
