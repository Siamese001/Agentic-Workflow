"""06.6 proposal drafting / admission doctrine tests.

Doctrine TEST REQUIREMENTS (06.6):
- Proposal lacks CompletedEvalRecord -> rejected.
- Proposal lacks RCA/pattern link -> rejected.
- Proposal has no exact diff -> rejected.
- Proposal has no rollback plan -> rejected.
- Proposal has no blast radius -> rejected.
- Proposal goes directly to UWG without gauntlet/approval -> rejected.
- Raw telemetry cannot become memory/policy directly.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L6_observability.shadow_eval import (
    ProposalError,
    admit_proposal,
    build_blast_radius,
    build_calibration_record,
    build_completed_eval_record,
    build_observer_compliance_receipt,
    build_proposed_diff_manifest,
    build_rca_packet,
    build_rollback_plan,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    build_test_plan,
    draft_proposal,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    fuse_signals,
    GovernanceBaseline,
    proposal_content_hash,
    stage_barrier_check,
)


def _eval_and_rca(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    outcome = evaluate_outcome(receipt, normalized)
    trajectory = evaluate_trajectory(receipt, normalized)
    # Match replay_digest to the run; replay-digest drift at high severity
    # forces allowed_downstream_use=RCA_ONLY per 06.4 hardening, which would
    # block proposal admission. Keep policy drift to exercise governance.
    baseline = GovernanceBaseline(
        policy_hash="DIFF-POL", rubric_hash="rh", replay_digest=bundle.replay_key,
    )
    governance = evaluate_governance_regression(receipt, normalized, baseline)
    calibration = build_calibration_record(rubric_hash="rh", rubric_version="1", grader_version="cv1")
    completed = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
    )
    fused = fuse_signals([completed])
    rca = build_rca_packet(fused, normalized=normalized, trajectory=trajectory, governance=governance)
    return completed, rca


def _build_full_proposal(completed, rca, *, owner="alice", signer="alice@org"):
    diff = build_proposed_diff_manifest(
        target_surface="prompt",
        operation_type="UPDATE",
        before_ref="prompt-v1",
        after_candidate_ref="prompt-v2",
        diff_summary="add chain-of-thought instruction",
        exact_patch_ref="patch-1",
    )
    blast = build_blast_radius(
        proposal_id="pending",
        affected_surfaces=["prompt"],
        affected_tests=["test_prompt_a"],
    )
    rollback = build_rollback_plan(
        proposal_id="pending",
        rollback_steps=["revert to prompt-v1"],
    )
    return draft_proposal(
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="prompt-v1",
        proposed_version_ref="prompt-v2",
        problem_statement="prompt produces unsupported claims under stress",
        completed_eval_record=completed,
        rca_packet=rca,
        pattern=None,
        proposed_diff=diff,
        expected_effect="reduce unsupported claims",
        rollback_plan=rollback,
        blast_radius=blast,
        affected_tests=["test_prompt_a"],
        migration_notes="",
        owner=owner,
        signer_identity=signer,
        policy_hash="policy-A",
    )


def test_proposal_requires_eval_with_proposal_downstream_use(sealed_completed_run):
    completed, rca = _eval_and_rca(sealed_completed_run)
    bad = dataclasses.replace(completed, allowed_downstream_use="RCA_ONLY")
    with pytest.raises(ProposalError):
        _build_full_proposal(bad, rca)


def test_proposal_requires_rca_or_pattern(sealed_completed_run):
    completed, _rca = _eval_and_rca(sealed_completed_run)
    diff = build_proposed_diff_manifest(
        target_surface="prompt",
        operation_type="UPDATE",
        before_ref="a",
        after_candidate_ref="b",
        diff_summary="x",
        exact_patch_ref="p",
    )
    blast = build_blast_radius(proposal_id="x", affected_surfaces=["prompt"], affected_tests=["t"])
    rb = build_rollback_plan(proposal_id="x", rollback_steps=["revert"])
    with pytest.raises(ProposalError):
        draft_proposal(
            proposal_type="PROMPT_UPDATE",
            target_surface="prompt",
            current_version_ref="a",
            proposed_version_ref="b",
            problem_statement="problem",
            completed_eval_record=completed,
            rca_packet=None,
            pattern=None,
            proposed_diff=diff,
            expected_effect="effect",
            rollback_plan=rb,
            blast_radius=blast,
            affected_tests=["t"],
            migration_notes="",
            owner="o",
            signer_identity="s",
        )


def test_proposal_requires_owner_signer(sealed_completed_run):
    completed, rca = _eval_and_rca(sealed_completed_run)
    with pytest.raises(ProposalError):
        _build_full_proposal(completed, rca, owner="", signer="")


def test_proposal_blast_radius_requires_surfaces():
    with pytest.raises(ProposalError):
        build_blast_radius(proposal_id="p", affected_surfaces=[], affected_tests=[])


def test_proposal_rollback_requires_steps():
    with pytest.raises(ProposalError):
        build_rollback_plan(proposal_id="p", rollback_steps=[])


def test_proposal_test_plan_requires_tests():
    with pytest.raises(ProposalError):
        build_test_plan(proposal_id="p", affected_tests=[])


def test_admission_admits_clean_proposal(sealed_completed_run):
    completed, rca = _eval_and_rca(sealed_completed_run)
    proposal = _build_full_proposal(completed, rca)
    test_plan = build_test_plan(
        proposal_id=proposal.proposal_id,
        affected_tests=["test_prompt_a"],
    )
    receipt = admit_proposal(
        proposal,
        test_plan=test_plan,
        completed_eval_record=completed,
        rca_packet=rca,
        pattern=None,
    )
    assert receipt.decision == "ADMIT_TO_GAUNTLET"
    assert not receipt.open_blockers
    assert receipt.deterministic_digest


def test_admission_holds_when_eval_freshness_fails(sealed_completed_run):
    completed, rca = _eval_and_rca(sealed_completed_run)
    proposal = _build_full_proposal(completed, rca)
    test_plan = build_test_plan(
        proposal_id=proposal.proposal_id,
        affected_tests=["test_prompt_a"],
    )
    receipt = admit_proposal(
        proposal,
        test_plan=test_plan,
        completed_eval_record=completed,
        rca_packet=rca,
        pattern=None,
        eval_freshness_ok=False,
    )
    assert receipt.decision == "REJECT_WEAK_PROPOSAL"
    assert "STALE_EVAL" in receipt.open_blockers


def test_admission_requires_sme_for_high_impact(sealed_completed_run):
    completed, rca = _eval_and_rca(sealed_completed_run)
    diff = build_proposed_diff_manifest(
        target_surface="policy",
        operation_type="UPDATE",
        before_ref="pol-v1",
        after_candidate_ref="pol-v2",
        diff_summary="tighten safety policy",
        exact_patch_ref="p",
    )
    blast = build_blast_radius(
        proposal_id="pending",
        affected_surfaces=["policy", "guardrail"],
        affected_tests=["t"],
    )
    rollback = build_rollback_plan(proposal_id="pending", rollback_steps=["revert"])
    proposal = draft_proposal(
        proposal_type="POLICY_CLARIFICATION",
        target_surface="policy",
        current_version_ref="pol-v1",
        proposed_version_ref="pol-v2",
        problem_statement="policy needs tightening",
        completed_eval_record=completed,
        rca_packet=rca,
        pattern=None,
        proposed_diff=diff,
        expected_effect="reduce policy gap",
        rollback_plan=rollback,
        blast_radius=blast,
        affected_tests=["t"],
        migration_notes="",
        owner="o",
        signer_identity="s",
        policy_hash="A",
    )
    test_plan = build_test_plan(proposal_id=proposal.proposal_id, affected_tests=["t"])
    receipt = admit_proposal(
        proposal,
        test_plan=test_plan,
        completed_eval_record=completed,
        rca_packet=rca,
        pattern=None,
    )
    assert receipt.decision == "REQUIRE_SME_REVIEW"


def test_proposal_content_hash_is_stable_for_same_content(sealed_completed_run):
    completed, rca = _eval_and_rca(sealed_completed_run)
    p1 = _build_full_proposal(completed, rca)
    h1 = proposal_content_hash(p1)
    h2 = proposal_content_hash(p1)
    assert h1 == h2 and len(h1) == 64
