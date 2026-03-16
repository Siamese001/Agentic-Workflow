"""ADG-driven tests for L1_cognition/types/identity_type_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_identity_type_types_adg")
_emit_applies_guardrail("p0", "test_identity_type_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_identity_type_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_identity_type_types_adg", "state_snapshot")
emit_replay_key("p0", "test_identity_type_types_adg")
emit_determinism_digest("p0", "test_identity_type_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.identity_type_types import (
    AgentIdentity,
    IdentityType,
    TrustDomain,
)


class TestIdentityType:
    def test_is_enum(self):
        import enum
        assert issubclass(IdentityType, enum.Enum)

    def test_orchestrator_value(self):
        assert IdentityType.ORCHESTRATOR.value == "orchestrator"

    def test_cognitive_agent_value(self):
        assert IdentityType.COGNITIVE_AGENT.value == "cognitive_agent"


class TestTrustDomain:
    def test_is_enum(self):
        import enum
        assert issubclass(TrustDomain, enum.Enum)

    def test_local_value(self):
        assert TrustDomain.LOCAL.value == "local"


class TestAgentIdentity:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentIdentity)

    def test_creates(self):
        import time
        now = time.time()
        identity = AgentIdentity(
            spiffe_id="spiffe://local/agent-001",
            agent_type=IdentityType.ORCHESTRATOR,
            TrustDomain=TrustDomain.LOCAL,
            public_key="pub-key",
            private_key="priv-key",
            issued_at=now,
            expires_at=now + 3600,
        )
        assert identity.spiffe_id == "spiffe://local/agent-001"
        assert identity.agent_type == IdentityType.ORCHESTRATOR
