"""Governance — L6 promotion requires gauntlet proof refs + UWG posture (W5).

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f
"""
from __future__ import annotations

import pytest

from agentic_core.L6_learning import (
    FutureRunPromotionRequest,
    ProposalPacket,
    ProposalType,
    ProofType,
)
from agentic_core.L6_learning.promotion_gauntlet import PromotionGauntlet


def _base_request(**kwargs) -> FutureRunPromotionRequest:
    d = dict(
        request_id="pr-1",
        run_id="run-1",
        proposal_packets=(),
        rollback_plan_ref="rollback://r1",
        replay_proof_ref="replay://r1",
        regression_proof_ref="regression://r1",
        safety_proof_ref="safety://r1",
        audit_manifest_ref="manifest://r1",
        completed_eval_record_ref="eval://r1",
        rca_packet_ref="rca://r1",
        calibration_proof_ref="",
    )
    d.update(kwargs)
    return FutureRunPromotionRequest(**d)


def _cache_proposal() -> ProposalPacket:
    return ProposalPacket(
        proposal_id="p-cache",
        run_id="run-1",
        proposal_type=ProposalType.CACHE_THRESHOLD,
        required_proofs=(ProofType.REPLAY, ProofType.REGRESSION),
    )


gauntlet = PromotionGauntlet()


def test_promotion_requires_eval_record_ref() -> None:
    req = _base_request(completed_eval_record_ref="")
    res = gauntlet.run_gauntlet(req)
    assert res.passed is False
    assert any("COMPLETED_EVAL_RECORD_REQUIRED" in f for f in res.failures)


def test_promotion_requires_rca_packet_ref_when_rca_needed() -> None:
    req = _base_request(
        proposal_packets=(_cache_proposal(),),
        rca_packet_ref="",
    )
    res = gauntlet.run_gauntlet(req)
    assert res.passed is False
    assert any("RCA_PACKET_REQUIRED" in f for f in res.failures)


def test_promotion_with_all_refs_passes_gauntlet() -> None:
    req = _base_request(proposal_packets=(_cache_proposal(),))
    res = gauntlet.run_gauntlet(req)
    assert res.passed is True


def test_no_auto_activate_ever() -> None:
    req = _base_request(auto_activate=True, proposal_packets=(_cache_proposal(),))
    res = gauntlet.run_gauntlet(req)
    assert res.passed is False
    assert any("AUTO_ACTIVATE" in f for f in res.failures)


def test_uwg_review_status_pre_approved_blocked() -> None:
    req = _base_request(
        uwg_review_status="PRE_APPROVED",
        proposal_packets=(_cache_proposal(),),
    )
    res = gauntlet.run_gauntlet(req)
    assert res.passed is False


def test_activation_only_future_run() -> None:
    req = _base_request(
        target_future_run_window="CURRENT_RUN",
        proposal_packets=(_cache_proposal(),),
    )
    res = gauntlet.run_gauntlet(req)
    assert res.passed is False


def test_proposal_inert_until_uwg() -> None:
    p = ProposalPacket(
        proposal_id="p1",
        run_id="r1",
        proposal_type=ProposalType.PROMPT_IMPROVEMENT,
        safety_review_status="PENDING_UWG",
    )
    assert p.is_inert() is True
    p2 = ProposalPacket(
        proposal_id="p2",
        run_id="r1",
        proposal_type=ProposalType.PROMPT_IMPROVEMENT,
        safety_review_status="ACTIVATED",
    )
    assert p2.is_inert() is False


def test_default_auto_activate_false_on_request() -> None:
    r = FutureRunPromotionRequest(request_id="a", run_id="b", rollback_plan_ref="x")
    assert r.auto_activate is False


@pytest.mark.parametrize(
    "ptype",
    [
        ProposalType.CACHE_THRESHOLD,
        ProposalType.PROMPT_IMPROVEMENT,
        ProposalType.RUBRIC_IMPROVEMENT,
        ProposalType.RETRIEVAL_PROFILE,
        ProposalType.CHUNKING_PROFILE,
        ProposalType.FRESHNESS_TTL,
    ],
)
def test_durable_surface_proposals_default_pending_uwg(ptype: ProposalType) -> None:
    p = ProposalPacket(proposal_id="x", run_id="y", proposal_type=ptype)
    assert p.safety_review_status == "PENDING_UWG"
    assert p.activation_trigger == "FUTURE_RUN_START"
