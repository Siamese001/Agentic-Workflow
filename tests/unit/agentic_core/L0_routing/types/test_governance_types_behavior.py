"""Behavioral tests for ``agentic_core.L0_routing.types.governance_types``.

Covers P3 Governance & Human Escalation artifacts:
- Enum membership: ExceptionScope, ProposalStatus, HILOutcome, ChangeAction.
- EvidencePack validation: trace_id, tuple types, risk_score bounds, boundary_snapshot_hash.
- PolicyExceptionArtifact validation + ``is_expired`` TTL semantics.
- HILReviewOutcome basic construction + L5 re-clearance flag.
- ProposedPolicyChange construction.
- PolicyUpdateProposal validation: required fields, status type, confidence bounds.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.governance_types import (
    ChangeAction,
    EvidencePack,
    ExceptionScope,
    HILOutcome,
    HILReviewOutcome,
    PolicyExceptionArtifact,
    PolicySnapshot,
    PolicyUpdateProposal,
    ProposalStatus,
    ProposedPolicyChange,
    RouteDecisionRef,
)


# ---- Enums ---------------------------------------------------------------


class TestEnums:
    def test_exception_scope(self) -> None:
        assert {e.value for e in ExceptionScope} == {
            "single_agent",
            "healing_wave",
            "full_pipeline",
        }

    def test_proposal_status(self) -> None:
        assert {p.value for p in ProposalStatus} == {"pending", "accepted", "rejected"}

    def test_hil_outcome(self) -> None:
        assert {o.value for o in HILOutcome} == {
            "approved",
            "rejected",
            "overridden",
            "needs_more_info",
        }

    def test_change_action(self) -> None:
        assert {c.value for c in ChangeAction} == {"add", "remove", "adjust"}


# ---- RouteDecisionRef / PolicySnapshot -----------------------------------


class TestSimpleFrozenDataclasses:
    def test_route_decision_ref_constructs(self) -> None:
        r = RouteDecisionRef(
            trace_id="t",
            decision="ALLOW",
            agent_name="agent",
            reason="policy-ok",
        )
        assert r.decision == "ALLOW"

    def test_route_decision_ref_is_frozen(self) -> None:
        r = RouteDecisionRef(trace_id="t", decision="d", agent_name="a", reason="r")
        with pytest.raises(AttributeError):
            r.decision = "other"  # type: ignore[misc]

    def test_policy_snapshot_constructs(self) -> None:
        s = PolicySnapshot(
            security_level="high",
            risk_tier="tier-2",
            laws_applied=("law-1", "law-2"),
            policy_hash="abc",
        )
        assert s.laws_applied == ("law-1", "law-2")


# ---- EvidencePack --------------------------------------------------------


def _ep(**overrides: object) -> EvidencePack:
    kwargs: dict[str, object] = {
        "trace_id": "t1",
        "action_trace": ("step-1", "step-2"),
        "policy_evals": ("eval-1",),
        "risk_score": 0.5,
        "budget_breach_data": {"cpu": 100},
        "boundary_snapshot_hash": "hash-1",
    }
    kwargs.update(overrides)
    return EvidencePack(**kwargs)  # type: ignore[arg-type]


class TestEvidencePack:
    def test_valid_minimal(self) -> None:
        ep = _ep()
        assert ep.trace_id == "t1"
        assert ep.evidence_id == ""  # default
        assert ep.route_decision_ref is None
        assert ep.attachments == ()

    def test_empty_trace_id(self) -> None:
        with pytest.raises(ValueError, match="trace_id"):
            _ep(trace_id="")

    def test_action_trace_must_be_tuple(self) -> None:
        with pytest.raises(TypeError, match="action_trace"):
            _ep(action_trace=["s1"])  # type: ignore[arg-type]

    def test_policy_evals_must_be_tuple(self) -> None:
        with pytest.raises(TypeError, match="policy_evals"):
            _ep(policy_evals=["e1"])  # type: ignore[arg-type]

    @pytest.mark.parametrize("score", [-0.01, 1.01, 2.0, -1.0])
    def test_risk_score_out_of_range(self, score: float) -> None:
        with pytest.raises(ValueError, match="risk_score"):
            _ep(risk_score=score)

    @pytest.mark.parametrize("score", [0.0, 0.5, 1.0])
    def test_risk_score_boundaries_accepted(self, score: float) -> None:
        assert _ep(risk_score=score).risk_score == score

    def test_empty_boundary_hash(self) -> None:
        with pytest.raises(ValueError, match="boundary_snapshot_hash"):
            _ep(boundary_snapshot_hash="")

    def test_optional_fields_passthrough(self) -> None:
        rdr = RouteDecisionRef(trace_id="t", decision="d", agent_name="a", reason="r")
        ep = _ep(evidence_id="E1", escalation_reason="budget", route_decision_ref=rdr)
        assert ep.evidence_id == "E1"
        assert ep.route_decision_ref is rdr


# ---- PolicyExceptionArtifact --------------------------------------------


def _pea(**overrides: object) -> PolicyExceptionArtifact:
    kwargs: dict[str, object] = {
        "trace_id": "t1",
        "nonce": "nonce-1",
        "exception_scope": ExceptionScope.SINGLE_AGENT,
        "semantic_clock_tick": 10,
        "issuer_signature": "sig-1",
    }
    kwargs.update(overrides)
    return PolicyExceptionArtifact(**kwargs)  # type: ignore[arg-type]


class TestPolicyExceptionArtifact:
    def test_valid(self) -> None:
        pea = _pea()
        assert pea.ttl_ticks == 0  # default

    @pytest.mark.parametrize("field", ["trace_id", "nonce", "issuer_signature"])
    def test_empty_required_field(self, field: str) -> None:
        with pytest.raises(ValueError, match=field):
            _pea(**{field: ""})

    def test_bad_scope_type(self) -> None:
        with pytest.raises(TypeError, match="exception_scope"):
            _pea(exception_scope="single_agent")  # type: ignore[arg-type]

    def test_negative_tick(self) -> None:
        with pytest.raises(ValueError, match="semantic_clock_tick"):
            _pea(semantic_clock_tick=-1)

    def test_is_expired_ttl_zero_never_expires(self) -> None:
        pea = _pea(semantic_clock_tick=0, ttl_ticks=0)
        assert pea.is_expired(now_tick=0) is False
        assert pea.is_expired(now_tick=10_000) is False

    def test_is_expired_within_ttl(self) -> None:
        pea = _pea(semantic_clock_tick=10, ttl_ticks=5)
        # valid through tick 15 inclusive
        assert pea.is_expired(now_tick=10) is False
        assert pea.is_expired(now_tick=15) is False

    def test_is_expired_beyond_ttl(self) -> None:
        pea = _pea(semantic_clock_tick=10, ttl_ticks=5)
        assert pea.is_expired(now_tick=16) is True
        assert pea.is_expired(now_tick=100) is True


# ---- HILReviewOutcome ----------------------------------------------------


class TestHILReviewOutcome:
    def test_defaults(self) -> None:
        h = HILReviewOutcome(decision="APPROVE", reviewer_id="r1", reviewer_sig="sig")
        assert h.requires_l5_reclear is False

    def test_modify_diff_flag(self) -> None:
        h = HILReviewOutcome(
            decision="MODIFY_DIFF",
            reviewer_id="r1",
            reviewer_sig="sig",
            requires_l5_reclear=True,
        )
        assert h.requires_l5_reclear is True

    def test_is_frozen(self) -> None:
        h = HILReviewOutcome(decision="d", reviewer_id="r", reviewer_sig="s")
        with pytest.raises(AttributeError):
            h.decision = "other"  # type: ignore[misc]


# ---- ProposedPolicyChange ------------------------------------------------


class TestProposedPolicyChange:
    def test_minimal(self) -> None:
        p = ProposedPolicyChange(
            target="rule-42",
            action=ChangeAction.ADJUST,
            scope="pipeline",
            risk_note="low-risk",
        )
        assert p.current_value == ""
        assert p.proposed_value == ""

    def test_full(self) -> None:
        p = ProposedPolicyChange(
            target="r1",
            action=ChangeAction.ADD,
            scope="agent",
            risk_note="n",
            current_value="old",
            proposed_value="new",
        )
        assert p.action is ChangeAction.ADD


# ---- PolicyUpdateProposal ------------------------------------------------


def _pup(**overrides: object) -> PolicyUpdateProposal:
    kwargs: dict[str, object] = {
        "trace_id": "t1",
        "override_id": "o1",
        "proposed_policy_diff": "diff-text",
        "originating_agent": "agent-1",
        "semantic_clock_tick": 5,
    }
    kwargs.update(overrides)
    return PolicyUpdateProposal(**kwargs)  # type: ignore[arg-type]


class TestPolicyUpdateProposal:
    def test_valid_minimal(self) -> None:
        p = _pup()
        assert p.status is ProposalStatus.PENDING
        assert p.confidence == 0.0
        assert p.proposed_changes == ()

    @pytest.mark.parametrize(
        "field",
        ["trace_id", "override_id", "proposed_policy_diff", "originating_agent"],
    )
    def test_empty_required_field(self, field: str) -> None:
        with pytest.raises(ValueError, match=field):
            _pup(**{field: ""})

    def test_negative_tick(self) -> None:
        with pytest.raises(ValueError, match="semantic_clock_tick"):
            _pup(semantic_clock_tick=-1)

    def test_bad_status_type(self) -> None:
        with pytest.raises(TypeError, match="status"):
            _pup(status="pending")  # type: ignore[arg-type]

    @pytest.mark.parametrize("c", [-0.01, 1.01, 2.0])
    def test_confidence_out_of_range(self, c: float) -> None:
        with pytest.raises(ValueError, match="confidence"):
            _pup(confidence=c)

    @pytest.mark.parametrize("c", [0.0, 0.5, 1.0])
    def test_confidence_boundaries_accepted(self, c: float) -> None:
        assert _pup(confidence=c).confidence == c

    def test_accepted_status(self) -> None:
        p = _pup(status=ProposalStatus.ACCEPTED)
        assert p.status is ProposalStatus.ACCEPTED

    def test_with_proposed_changes(self) -> None:
        change = ProposedPolicyChange(
            target="r",
            action=ChangeAction.REMOVE,
            scope="s",
            risk_note="n",
        )
        p = _pup(proposed_changes=(change,))
        assert len(p.proposed_changes) == 1
        assert p.proposed_changes[0] is change
