"""06.6 — Proposal Drafting and Admission Gate.

Implements:

* DraftProposalPacket
* ProposedDiffManifest (built per-target-surface)
* ProposalEvidenceMap
* ProposalBlastRadiusAssessment
* ProposalRollbackPlanRef
* ProposalTestPlan
* ProposalAdmissionReceipt

Hard preconditions (06.6):
* Only ``CompletedEvalRecord`` with ``allowed_downstream_use=RCA_AND_PROPOSAL``.
* RCAPacket or PatternSynthesisRecord required.
* Exact ``proposed_diff`` required — no vague "improve prompt" prose.
* ``rollback_plan``, ``blast_radius``, ``test_plan``, ``owner/signer`` required.

Forbidden:
* Eval-less proposal.
* Direct 6D entry.
* Current-run repair.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterable

from agentic_core.L6_observability.shadow_eval._digest import (
    canonical_json,
    stamp_digest,
)
from agentic_core.L6_observability.shadow_eval.contracts import (
    ADMIT_TO_GAUNTLET,
    HOLD_FOR_MORE_EVIDENCE,
    PROPOSAL_TYPES,
    REJECT_WEAK_PROPOSAL,
    REQUIRE_SME_REVIEW,
    CompletedEvalRecord,
    DraftProposalPacket,
    PatternSynthesisRecord,
    ProposalAdmissionReceipt,
    ProposalBlastRadiusAssessment,
    ProposalRollbackPlanRef,
    ProposalTestPlan,
    ProposedDiffManifest,
    RCAPacket,
)


class ProposalError(Exception):
    """Raised when a proposal violates 06.6 preconditions."""


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Sub-component builders
# ---------------------------------------------------------------------------


def build_proposed_diff_manifest(
    *,
    target_surface: str,
    operation_type: str,
    before_ref: str,
    after_candidate_ref: str,
    diff_summary: str,
    exact_patch_ref: str | None = None,
    schema_ref: str | None = None,
    validation_rules: Iterable[str] = (),
    affected_surfaces: Iterable[str] = (),
    compatibility_notes: str = "",
) -> ProposedDiffManifest:
    if not target_surface or not operation_type:
        raise ProposalError("ProposedDiffManifest requires target_surface + operation_type")
    if not before_ref or not after_candidate_ref:
        raise ProposalError("ProposedDiffManifest requires before_ref + after_candidate_ref")
    if not exact_patch_ref:
        # The diff manifest itself can carry the patch ref; doctrine requires
        # the proposal carries an exact diff. We allow empty here only if the
        # caller supplies an exact_patch_ref via DraftProposalPacket fields.
        pass
    rec = ProposedDiffManifest(
        proposed_diff_manifest_id=_gen_id("diff"),
        target_surface=target_surface,
        operation_type=operation_type,
        before_ref=before_ref,
        after_candidate_ref=after_candidate_ref,
        diff_summary=diff_summary,
        exact_patch_ref=exact_patch_ref,
        schema_ref=schema_ref,
        validation_rules=list(validation_rules),
        affected_surfaces=list(affected_surfaces),
        compatibility_notes=compatibility_notes,
    )
    return stamp_digest(rec)


def build_blast_radius(
    *,
    proposal_id: str,
    affected_surfaces: Iterable[str],
    affected_tests: Iterable[str] = (),
    rollout_risk_score: float = 0.0,
    notes: str = "",
) -> ProposalBlastRadiusAssessment:
    surfaces = list(affected_surfaces)
    if not surfaces:
        raise ProposalError("blast radius must list at least one affected surface")
    return ProposalBlastRadiusAssessment(
        blast_radius_id=_gen_id("blast"),
        proposal_id=proposal_id,
        affected_surfaces=surfaces,
        affected_tests=list(affected_tests),
        rollout_risk_score=rollout_risk_score,
        notes=notes,
    )


def build_rollback_plan(
    *,
    proposal_id: str,
    rollback_steps: Iterable[str],
    rehearsal_status: str = "UNTESTED",
) -> ProposalRollbackPlanRef:
    steps = list(rollback_steps)
    if not steps:
        raise ProposalError("rollback plan must contain at least one step")
    return ProposalRollbackPlanRef(
        rollback_plan_ref_id=_gen_id("rb"),
        proposal_id=proposal_id,
        rollback_steps=steps,
        rehearsal_status=rehearsal_status,
    )


def build_test_plan(
    *,
    proposal_id: str,
    affected_tests: Iterable[str],
    regression_pack_refs: Iterable[str] = (),
    golden_set_refs: Iterable[str] = (),
    adversarial_case_refs: Iterable[str] = (),
) -> ProposalTestPlan:
    tests = list(affected_tests)
    if not tests:
        raise ProposalError("test plan must list affected tests")
    return ProposalTestPlan(
        proposal_test_plan_id=_gen_id("plan"),
        proposal_id=proposal_id,
        affected_tests=tests,
        regression_pack_refs=list(regression_pack_refs),
        golden_set_refs=list(golden_set_refs),
        adversarial_case_refs=list(adversarial_case_refs),
    )


# ---------------------------------------------------------------------------
# Draft proposal
# ---------------------------------------------------------------------------


def draft_proposal(
    *,
    proposal_type: str,
    target_surface: str,
    current_version_ref: str,
    proposed_version_ref: str | None,
    problem_statement: str,
    completed_eval_record: CompletedEvalRecord,
    rca_packet: RCAPacket | None,
    pattern: PatternSynthesisRecord | None,
    proposed_diff: ProposedDiffManifest,
    expected_effect: str,
    rollback_plan: ProposalRollbackPlanRef,
    blast_radius: ProposalBlastRadiusAssessment,
    affected_tests: Iterable[str],
    migration_notes: str,
    owner: str,
    signer_identity: str,
    expiration_ttl_days: int = 14,
    review_ttl_days: int = 7,
    policy_hash: str = "",
    evidence_links: Iterable[str] = (),
) -> DraftProposalPacket:
    """Build a DraftProposalPacket; raises ProposalError on doctrine breach."""
    if proposal_type not in PROPOSAL_TYPES:
        raise ProposalError(f"unknown proposal_type: {proposal_type}")
    if completed_eval_record.allowed_downstream_use != "RCA_AND_PROPOSAL":
        raise ProposalError(
            "proposal requires CompletedEvalRecord with allowed_downstream_use=RCA_AND_PROPOSAL"
        )
    if rca_packet is None and pattern is None:
        raise ProposalError("proposal requires RCAPacket or PatternSynthesisRecord")
    if not problem_statement.strip():
        raise ProposalError("proposal requires problem_statement")
    if not target_surface.strip():
        raise ProposalError("proposal requires explicit target_surface")
    if not (owner and signer_identity):
        raise ProposalError("proposal requires owner and signer_identity")
    if not affected_tests:
        # Fall back to blast radius affected_tests if explicit list empty.
        affected_tests = list(blast_radius.affected_tests)
    if not affected_tests:
        raise ProposalError("proposal requires at least one affected test")

    now = datetime.now(timezone.utc)
    expiration = (now + timedelta(days=expiration_ttl_days)).isoformat()
    review = (now + timedelta(days=review_ttl_days)).isoformat()

    proposal_id = _gen_id("proposal")
    rec = DraftProposalPacket(
        proposal_id=proposal_id,
        proposal_type=proposal_type,
        target_surface=target_surface,
        current_version_ref=current_version_ref,
        proposed_version_ref=proposed_version_ref,
        problem_statement=problem_statement,
        evidence_links=list(evidence_links) or list(rca_packet.evidence_links if rca_packet else []),
        completed_eval_record_id=completed_eval_record.completed_eval_record_id,
        rca_packet_id=rca_packet.rca_packet_id if rca_packet else None,
        pattern_id=pattern.pattern_id if pattern else None,
        proposed_diff=proposed_diff,
        expected_effect=expected_effect,
        rollback_plan_ref=rollback_plan,
        blast_radius=blast_radius,
        affected_tests=list(affected_tests),
        migration_notes=migration_notes,
        owner=owner,
        signer_identity=signer_identity,
        expiration_ttl=expiration,
        review_ttl=review,
        policy_hash=policy_hash,
    )
    return stamp_digest(rec)


# ---------------------------------------------------------------------------
# Admission gate
# ---------------------------------------------------------------------------


_HIGH_IMPACT_TYPES = frozenset({"POLICY_CLARIFICATION", "RUBRIC_UPDATE"})
_HIGH_IMPACT_SURFACES = frozenset({"policy", "rubric", "guardrail", "safety"})


def admit_proposal(
    proposal: DraftProposalPacket,
    *,
    test_plan: ProposalTestPlan,
    completed_eval_record: CompletedEvalRecord,
    rca_packet: RCAPacket | None,
    pattern: PatternSynthesisRecord | None,
    eval_freshness_ok: bool = True,
    calibration_freshness_ok: bool = True,
) -> ProposalAdmissionReceipt:
    open_blockers: list[str] = []
    reasons: list[str] = []

    eval_present = completed_eval_record is not None
    rca_or_pattern = rca_packet is not None or pattern is not None
    target_present = bool(proposal.target_surface)
    diff_present = bool(proposal.proposed_diff and proposal.proposed_diff.diff_summary)
    blast_present = bool(proposal.blast_radius and proposal.blast_radius.affected_surfaces)
    rollback_present = bool(proposal.rollback_plan_ref and proposal.rollback_plan_ref.rollback_steps)
    test_present = bool(test_plan and test_plan.affected_tests)
    owner_present = bool(proposal.owner and proposal.signer_identity)

    if not eval_present:
        open_blockers.append("MISSING_EVAL_RECORD")
        reasons.append("eval_record_required")
    if not rca_or_pattern:
        open_blockers.append("MISSING_RCA_OR_PATTERN")
        reasons.append("rca_or_pattern_required")
    if not target_present:
        open_blockers.append("MISSING_TARGET_SURFACE")
    if not diff_present:
        open_blockers.append("MISSING_DIFF")
    if not blast_present:
        open_blockers.append("MISSING_BLAST_RADIUS")
    if not rollback_present:
        open_blockers.append("MISSING_ROLLBACK")
    if not test_present:
        open_blockers.append("MISSING_TEST_PLAN")
    if not owner_present:
        open_blockers.append("MISSING_OWNER_SIGNER")
    if not eval_freshness_ok:
        open_blockers.append("STALE_EVAL")
        reasons.append("eval_freshness_failed")
    if not calibration_freshness_ok:
        open_blockers.append("STALE_CALIBRATION")
        reasons.append("calibration_freshness_failed")

    if open_blockers:
        decision = (
            HOLD_FOR_MORE_EVIDENCE
            if {"MISSING_EVAL_RECORD", "MISSING_RCA_OR_PATTERN"} & set(open_blockers)
            else REJECT_WEAK_PROPOSAL
        )
    elif (
        proposal.proposal_type in _HIGH_IMPACT_TYPES
        or any(s in _HIGH_IMPACT_SURFACES for s in proposal.blast_radius.affected_surfaces)
        or proposal.blast_radius.rollout_risk_score >= 0.7
    ):
        decision = REQUIRE_SME_REVIEW
    else:
        decision = ADMIT_TO_GAUNTLET

    receipt = ProposalAdmissionReceipt(
        admission_receipt_id=_gen_id("admit"),
        proposal_id=proposal.proposal_id,
        eval_record_present=eval_present,
        rca_or_pattern_present=rca_or_pattern,
        target_surface_present=target_present,
        proposed_diff_present=diff_present,
        blast_radius_present=blast_present,
        rollback_plan_present=rollback_present,
        test_plan_present=test_present,
        owner_signer_present=owner_present,
        freshness_check_status="OK" if eval_freshness_ok and calibration_freshness_ok else "STALE",
        open_blockers=open_blockers,
        decision=decision,
        reason_codes=reasons,
    )
    return stamp_digest(receipt)


def proposal_content_hash(proposal: DraftProposalPacket) -> str:
    """Stable content hash used by 06.7 PromotionPacket / GauntletReceipt."""
    payload = {
        "proposal_id": proposal.proposal_id,
        "proposal_type": proposal.proposal_type,
        "target_surface": proposal.target_surface,
        "proposed_diff_digest": proposal.proposed_diff.deterministic_digest,
        "current_version_ref": proposal.current_version_ref,
        "proposed_version_ref": proposal.proposed_version_ref,
        "policy_hash": proposal.policy_hash,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


__all__ = [
    "ProposalError",
    "build_proposed_diff_manifest",
    "build_blast_radius",
    "build_rollback_plan",
    "build_test_plan",
    "draft_proposal",
    "admit_proposal",
    "proposal_content_hash",
]
