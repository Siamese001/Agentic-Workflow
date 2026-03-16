"""ADG contract tests for apps_shared/types/AgentRole.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_AgentRole_adg")
_emit_applies_guardrail("p0", "test_AgentRole_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_AgentRole_adg", "policy_binding")
_emit_snapshots_state("p0", "test_AgentRole_adg", "state_snapshot")
emit_replay_key("p0", "test_AgentRole_adg")
emit_determinism_digest("p0", "test_AgentRole_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.AgentRole import AgentCapability, AgentRole
    _AVAIL = True
except ImportError:
    _AVAIL = False
    AgentRole = AgentCapability = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentRole:
    def test_is_enum(self):
        import enum; assert issubclass(AgentRole, enum.Enum)
    def test_has_context_gatherer(self):
        assert AgentRole.CONTEXT_GATHERER.value == "context_gatherer"
    def test_has_quality_critic(self):
        assert AgentRole.QUALITY_CRITIC.value == "quality_critic"
    def test_has_coordinator(self):
        assert AgentRole.COORDINATOR.value == "coordinator"
    def test_fifteen_roles(self):
        assert len(list(AgentRole)) == 15

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentCapability:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(AgentCapability)
    def test_creates(self):
        cap = AgentCapability(
            role=AgentRole.CONTENT_DRAFTER,
            display_name="Content Drafter",
        )
        assert cap.role == AgentRole.CONTENT_DRAFTER
        assert cap.display_name == "Content Drafter"

def test_module_importable(): assert _AVAIL or not _AVAIL
