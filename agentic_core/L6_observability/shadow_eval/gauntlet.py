"""06.7 — Gauntlet, Approval, UWG Promotion Request, Future-Run Publish.

Implements:

* GauntletReceipt
* ApprovalDecisionRecord
* PromotionPacket
* PromotionUWGRequestPackage
* LedgerProofReference
* FutureRunActivationReceipt

Hard rules (06.7):
* Approve only with: fresh 6B eval, RCA/pattern, gauntlet PASS, fresh
  calibration, signer authority, rollback verified, blast radius accepted.
* L6 may construct a ``PromotionUWGRequestPackage`` only after
  ``ApprovalDecisionRecord.decision == APPROVE``.
* L6 does NOT write to L4 — UWG commits, L4 stores. This module is the
  request side; ``bind_uwg_receipt`` accepts a UWG receipt as a *ref* and
  records it; it never invokes UWG.
* BUS U activation is future-run only and is encoded by
  ``FutureRunActivationReceipt.activate_at = NEXT_RUN_START``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Iterable

from agentic_core.L6_observability.shadow_eval._digest import stamp_digest
from agentic_core.L6_observability.shadow_eval.contracts import (
    APPROVAL_DECISIONS,
    GAUNTLET_FAIL,
    GAUNTLET_PASS,
    HOLD_FOR_MORE_EVIDENCE,
    ApprovalDecisionRecord,
    CompletedEvalRecord,
    DraftProposalPacket,
    FutureRunActivationReceipt,
    GauntletReceipt,
    LedgerProofReference,
    PromotionPacket,
    PromotionUWGRequestPackage,
    ProposalAdmissionReceipt,
    RCAPacket,
)
from agentic_core.L6_observability.shadow_eval.proposal import proposal_content_hash


class GauntletError(Exception):
    """Raised when a gauntlet/approval invariant is violated."""


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Gauntlet
# ---------------------------------------------------------------------------


def run_gauntlet(
    proposal: DraftProposalPacket,
    *,
    replay_case_refs: Iterable[str] = (),
    regression_pack_refs: Iterable[str] = (),
    golden_set_refs: Iterable[str] = (),
    adversarial_case_refs: Iterable[str] = (),
    compatibility_check_refs: Iterable[str] = (),
    rollback_rehearsal_ref: str = "",
    failing_cases: Iterable[str] = (),
    sme_signoff_ref: str | None = None,
    rollout_risk_score: float | None = None,
    replay_proof_ref: str = "",
    divergence_localization: Iterable[str] = (),
    signer_identity: str = "",
) -> GauntletReceipt:
    if not proposal:
        raise GauntletError("proposal required for gauntlet")
    if not rollback_rehearsal_ref:
        raise GauntletError("gauntlet requires rollback rehearsal reference")
    failing = list(failing_cases)
    verdict = GAUNTLET_PASS if not failing else GAUNTLET_FAIL
    risk = rollout_risk_score if rollout_risk_score is not None else proposal.blast_radius.rollout_risk_score
    receipt = GauntletReceipt(
        gauntlet_receipt_id=_gen_id("gauntlet"),
        proposal_id=proposal.proposal_id,
        proposal_content_hash=proposal_content_hash(proposal),
        replay_case_refs=list(replay_case_refs),
        regression_pack_refs=list(regression_pack_refs),
        golden_set_refs=list(golden_set_refs),
        adversarial_case_refs=list(adversarial_case_refs),
        compatibility_check_refs=list(compatibility_check_refs),
        rollback_rehearsal_ref=rollback_rehearsal_ref,
        sme_signoff_ref=sme_signoff_ref,
        pass_fail_hold_verdict=verdict,
        failing_cases=failing,
        rollout_risk_score=risk,
        replay_proof_ref=replay_proof_ref,
        divergence_localization=list(divergence_localization),
        signer_identity=signer_identity or proposal.signer_identity,
    )
    return stamp_digest(receipt)


# ---------------------------------------------------------------------------
# Approval
# ---------------------------------------------------------------------------


_APPROVAL_PRIORITY: dict[str, int] = {
    # Lowest = most permissive. The highest priority across all surfaced
    # reason codes wins the decision. Doctrine 06.7: REJECT is terminal;
    # HOLD blocks progress until more evidence; REQUIRE_* are actionable
    # human-loop asks; APPROVE is the only "go" state.
    "APPROVE": 0,
    "REQUIRE_SME_REVIEW": 1,
    "REQUIRE_ROLLBACK_PLAN": 2,
    "REQUIRE_NARROWER_SCOPE": 3,
    "REQUIRE_ADR_EXCEPTION": 4,
    "HOLD_FOR_MORE_EVIDENCE": 5,
    "REJECT": 6,
}


def _select_decision(*candidates: str) -> str:
    """Return the highest-priority decision among the candidates."""
    return max(candidates, key=lambda d: _APPROVAL_PRIORITY.get(d, -1))


def decide_approval(
    proposal: DraftProposalPacket,
    *,
    admission: ProposalAdmissionReceipt,
    gauntlet: GauntletReceipt,
    completed_eval_record: CompletedEvalRecord,
    rca_packet: RCAPacket,
    eval_freshness_ok: bool,
    calibration_freshness_ok: bool,
    signer_authority_ok: bool,
    rollback_verified: bool,
    blast_radius_accepted: bool,
    adr_required: bool = False,
    adr_ref: str | None = None,
) -> ApprovalDecisionRecord:
    """Make the canonical APPROVE / REJECT / HOLD / REQUIRE_* decision.

    Decision priority (highest wins): REJECT > HOLD > REQUIRE_ADR_EXCEPTION >
    REQUIRE_NARROWER_SCOPE > REQUIRE_ROLLBACK_PLAN > REQUIRE_SME_REVIEW >
    APPROVE. All gates are evaluated and surfaced as reason codes regardless
    of which one wins. Doctrine 06.7 forbids approving without each gate
    explicitly evaluated.

    ``adr_required`` and ``adr_ref`` enable the REQUIRE_ADR_EXCEPTION path
    per 06.7: an architectural change that touches policy/rubric/guardrail
    surfaces requires an ADR exception ref; missing one yields the dedicated
    decision so the user knows precisely what is missing.
    """
    reasons: list[str] = []
    decision = "APPROVE"

    if admission.decision != "ADMIT_TO_GAUNTLET":
        reasons.append("PROPOSAL_NOT_ADMITTED")
        decision = _select_decision(decision, "REJECT")
    if gauntlet.pass_fail_hold_verdict != GAUNTLET_PASS:
        reasons.append("GAUNTLET_FAIL")
        decision = _select_decision(decision, "REJECT")
    if not eval_freshness_ok:
        reasons.append("STALE_EVAL")
        decision = _select_decision(decision, "HOLD_FOR_MORE_EVIDENCE")
    if not calibration_freshness_ok:
        reasons.append("STALE_CALIBRATION")
        decision = _select_decision(decision, "HOLD_FOR_MORE_EVIDENCE")
    if not signer_authority_ok:
        reasons.append("INSUFFICIENT_SIGNER_AUTHORITY")
        decision = _select_decision(decision, "REQUIRE_SME_REVIEW")
    if not rollback_verified:
        reasons.append("ROLLBACK_NOT_VERIFIED")
        decision = _select_decision(decision, "REQUIRE_ROLLBACK_PLAN")
    if not blast_radius_accepted:
        reasons.append("BLAST_RADIUS_NOT_ACCEPTED")
        decision = _select_decision(decision, "REQUIRE_NARROWER_SCOPE")
    if adr_required and not adr_ref:
        reasons.append("ADR_EXCEPTION_REQUIRED")
        decision = _select_decision(decision, "REQUIRE_ADR_EXCEPTION")
    # Content-hash binding: the gauntlet receipt MUST cover the same content
    # the approval decision is being made about. Doctrine 06.8 anti-bypass.
    if gauntlet.proposal_content_hash != proposal_content_hash(proposal):
        reasons.append("CONTENT_HASH_MISMATCH")
        decision = _select_decision(decision, "REJECT")
    if decision not in APPROVAL_DECISIONS:
        raise GauntletError(f"invalid decision: {decision}")

    rec = ApprovalDecisionRecord(
        approval_decision_id=_gen_id("approval"),
        proposal_id=proposal.proposal_id,
        gauntlet_receipt_id=gauntlet.gauntlet_receipt_id,
        completed_eval_record_id=completed_eval_record.completed_eval_record_id,
        rca_packet_id=rca_packet.rca_packet_id,
        eval_freshness_status="FRESH" if eval_freshness_ok else "STALE",
        calibration_freshness_status="FRESH" if calibration_freshness_ok else "STALE",
        signer_authority_status="OK" if signer_authority_ok else "INSUFFICIENT",
        rollback_verified=rollback_verified,
        blast_radius_accepted=blast_radius_accepted,
        decision=decision,
        reason_codes=reasons,
    )
    return stamp_digest(rec)


# ---------------------------------------------------------------------------
# Promotion packet (immutable artifact for UWG handoff)
# ---------------------------------------------------------------------------


def build_promotion_packet(
    proposal: DraftProposalPacket,
    *,
    approval: ApprovalDecisionRecord,
    completed_eval_record: CompletedEvalRecord,
    rca_packet: RCAPacket,
    gauntlet: GauntletReceipt,
    target_version_current: str,
    target_version_proposed: str,
    rollout_plan: str = "",
    incident_ids: Iterable[str] = (),
    pattern_ids: Iterable[str] = (),
    activation_policy: str = "NEXT_RUN_START",
    bus_u_activation_receipt: str | None = None,
) -> PromotionPacket:
    if approval.decision != "APPROVE":
        raise GauntletError("PromotionPacket requires APPROVE decision")
    if gauntlet.pass_fail_hold_verdict != GAUNTLET_PASS:
        raise GauntletError("PromotionPacket requires gauntlet PASS")
    content_hash = proposal_content_hash(proposal)
    if gauntlet.proposal_content_hash != content_hash:
        raise GauntletError("PromotionPacket: content hash mismatch with gauntlet")

    rec = PromotionPacket(
        promotion_packet_id=_gen_id("promo"),
        proposal_id=proposal.proposal_id,
        proposal_type=proposal.proposal_type,
        target_surface=proposal.target_surface,
        target_version_current=target_version_current,
        target_version_proposed=target_version_proposed,
        proposed_diff=proposal.proposed_diff,
        content_hash=content_hash,
        signer_identity=proposal.signer_identity,
        owner=proposal.owner,
        policy_hash=proposal.policy_hash,
        eval_record_id=completed_eval_record.completed_eval_record_id,
        outcome_eval_ref=completed_eval_record.outcome_eval_ref,
        trajectory_eval_ref=completed_eval_record.trajectory_eval_ref,
        governance_eval_ref=completed_eval_record.governance_regression_ref,
        calibration_ref=completed_eval_record.calibration_record_ref,
        rca_packet_id=rca_packet.rca_packet_id,
        incident_ids=list(incident_ids),
        pattern_ids=list(pattern_ids),
        evidence_links=list(proposal.evidence_links),
        root_cause_class=rca_packet.root_cause_class,
        first_bad_span=rca_packet.first_bad_span.span_id,
        expected_effect=proposal.expected_effect,
        affected_surfaces=list(proposal.blast_radius.affected_surfaces),
        blast_radius=str(proposal.blast_radius.rollout_risk_score),
        regression_pack_ids=list(gauntlet.regression_pack_refs),
        golden_set_ids=list(gauntlet.golden_set_refs),
        gauntlet_receipt=gauntlet.gauntlet_receipt_id,
        rollout_plan=rollout_plan,
        rollback_plan=proposal.rollback_plan_ref.rollback_plan_ref_id,
        activation_policy=activation_policy,
        approval_decision_id=approval.approval_decision_id,
        uwg_receipt_id=None,
        l4_version_digest=None,
        bus_u_activation_receipt=bus_u_activation_receipt,
    )
    return stamp_digest(rec)


# ---------------------------------------------------------------------------
# UWG request package + receipt binding
# ---------------------------------------------------------------------------


def build_uwg_request_package(
    promotion: PromotionPacket,
    *,
    version_bump: str,
    alias_swap_plan: str,
    cache_read_surface_refresh_plan: str,
) -> PromotionUWGRequestPackage:
    if promotion.approval_decision_id == "":
        raise GauntletError("UWG request package requires an approval_decision_id")
    pkg = PromotionUWGRequestPackage(
        package_id=_gen_id("uwgpkg"),
        promotion_packet_id=promotion.promotion_packet_id,
        proposal_id=promotion.proposal_id,
        approval_decision_id=promotion.approval_decision_id,
        gauntlet_receipt_id=promotion.gauntlet_receipt,
        content_hash=promotion.content_hash,
        signer_identity=promotion.signer_identity,
        policy_hash=promotion.policy_hash,
        target_surface=promotion.target_surface,
        blast_radius=promotion.blast_radius,
        rollback_plan=promotion.rollback_plan,
        version_bump=version_bump,
        alias_swap_plan=alias_swap_plan,
        cache_read_surface_refresh_plan=cache_read_surface_refresh_plan,
    )
    return stamp_digest(pkg)


def bind_uwg_receipt(
    promotion: PromotionPacket,
    *,
    uwg_receipt_id: str,
    l4_version_digest: str,
) -> tuple[PromotionPacket, LedgerProofReference]:
    """Record the UWG receipt against the promotion packet.

    The PromotionPacket is frozen-style; we mutate via ``object.__setattr__``
    to preserve the original digest while pinning the UWG receipt fields.
    The returned ``LedgerProofReference`` is the durable proof binding.
    """
    if not uwg_receipt_id or not l4_version_digest:
        raise GauntletError("UWG receipt binding requires both ids")
    object.__setattr__(promotion, "uwg_receipt_id", uwg_receipt_id)
    object.__setattr__(promotion, "l4_version_digest", l4_version_digest)
    proof = LedgerProofReference(
        ledger_proof_id=_gen_id("ledger"),
        promotion_packet_id=promotion.promotion_packet_id,
        uwg_receipt_id=uwg_receipt_id,
        l4_version_digest=l4_version_digest,
        notes="bound at L6 promotion handoff",
    )
    return promotion, proof


# ---------------------------------------------------------------------------
# Future-run activation receipt
# ---------------------------------------------------------------------------


def build_future_run_activation_receipt(
    promotion: PromotionPacket,
    *,
    alias_updated: bool,
    canary_scope: str | None = None,
    ttl_review_date: str | None = None,
) -> FutureRunActivationReceipt:
    if not promotion.uwg_receipt_id:
        raise GauntletError(
            "FutureRunActivationReceipt requires UWG receipt; L6 cannot publish to BUS U before UWG receipt"
        )
    if not promotion.l4_version_digest:
        raise GauntletError("FutureRunActivationReceipt requires l4_version_digest")
    rec = FutureRunActivationReceipt(
        activation_receipt_id=_gen_id("activate"),
        promotion_packet_id=promotion.promotion_packet_id,
        uwg_receipt_id=promotion.uwg_receipt_id,
        l4_version_digest=promotion.l4_version_digest,
        target_surface=promotion.target_surface,
        alias_updated=alias_updated,
        activate_at="NEXT_RUN_START",
        canary_scope=canary_scope,
        ttl_review_date=ttl_review_date,
        no_current_run_mutation_assertion=True,
        no_retroactive_regrade_assertion=True,
        bus_u_publish_marker="DEFERRED_UNTIL_RUN_START",
    )
    return stamp_digest(rec)


__all__ = [
    "GauntletError",
    "run_gauntlet",
    "decide_approval",
    "build_promotion_packet",
    "build_uwg_request_package",
    "bind_uwg_receipt",
    "build_future_run_activation_receipt",
]
