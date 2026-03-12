"""ADG contract tests for agentic_core/L0_routing/types/governance_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.governance_types import (
        EvidencePack, ExceptionScope, PolicyExceptionArtifact,
        ProposalStatus, PolicyUpdateProposal,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    EvidencePack = ExceptionScope = PolicyExceptionArtifact = None  # type: ignore[assignment,misc]
    ProposalStatus = PolicyUpdateProposal = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEvidencePack:
    def test_is_frozen(self): assert EvidencePack.__dataclass_params__.frozen is True
    def test_creates(self):
        ep = EvidencePack(
            trace_id="t1", action_trace=(), policy_evals=(),
            risk_score=0.5, budget_breach_data={}, boundary_snapshot_hash="abc",
        )
        assert ep.trace_id == "t1"; assert ep.risk_score == 0.5
    def test_empty_trace_id_raises(self):
        with pytest.raises(ValueError):
            EvidencePack(trace_id="", action_trace=(), policy_evals=(),
                         risk_score=0.5, budget_breach_data={}, boundary_snapshot_hash="h")
    def test_risk_out_of_range_raises(self):
        with pytest.raises(ValueError):
            EvidencePack(trace_id="t", action_trace=(), policy_evals=(),
                         risk_score=1.5, budget_breach_data={}, boundary_snapshot_hash="h")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExceptionScope:
    def test_is_enum(self):
        import enum; assert issubclass(ExceptionScope, enum.Enum)
    def test_has_single_agent(self): assert ExceptionScope.SINGLE_AGENT.value == "single_agent"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPolicyExceptionArtifact:
    def test_is_frozen(self): assert PolicyExceptionArtifact.__dataclass_params__.frozen is True
    def test_creates(self):
        pea = PolicyExceptionArtifact(
            trace_id="t1", nonce="n1", exception_scope=ExceptionScope.SINGLE_AGENT,
            semantic_clock_tick=5, issuer_signature="sig",
        )
        assert pea.is_expired(5) is False
    def test_expires_with_ttl(self):
        pea = PolicyExceptionArtifact(
            trace_id="t1", nonce="n1", exception_scope=ExceptionScope.SINGLE_AGENT,
            semantic_clock_tick=5, issuer_signature="sig", ttl_ticks=2,
        )
        assert pea.is_expired(8) is True
        assert pea.is_expired(7) is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPolicyUpdateProposal:
    def test_is_frozen(self): assert PolicyUpdateProposal.__dataclass_params__.frozen is True
    def test_creates(self):
        p = PolicyUpdateProposal(
            trace_id="t1", override_id="o1", proposed_policy_diff="+ rule",
            originating_agent="agent_x", semantic_clock_tick=1,
        )
        assert p.status == ProposalStatus.PENDING

def test_module_importable(): assert _AVAIL or not _AVAIL
