"""06.7 gauntlet / approval / promotion / activation doctrine tests.

Doctrine TEST REQUIREMENTS (06.7):
- Proposal cannot be approved without gauntlet PASS.
- Stale eval cannot be used on write.
- Promotion must include rollback.
- L6 must NOT write to L4 directly (proven structurally — uwg_commit
  callback is the only path).
- BUS U publish does not occur before UWG receipt.
- Activation cannot affect current run.
- content_hash must match between approved packet and UWG package.
- Ledger proof refs are stored after UWG receipt.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L6_observability.shadow_eval import (
    GauntletError,
    admit_proposal,
    bind_uwg_receipt,
    build_blast_radius,
    build_calibration_record,
    build_completed_eval_record,
    build_future_run_activation_receipt,
    build_observer_compliance_receipt,
    build_promotion_packet,
    build_proposed_diff_manifest,
    build_rca_packet,
    build_rollback_plan,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    build_test_plan,
    build_uwg_request_package,
    decide_approval,
    draft_proposal,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    fuse_signals,
    GovernanceBaseline,
    proposal_content_hash,
    run_gauntlet,
    stage_barrier_check,
)


@pytest.fixture
def proposal_bundle(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    outcome = evaluate_outcome(receipt, normalized)
    trajectory = evaluate_trajectory(receipt, normalized)
    # Match replay_digest to the run; only policy drifts. Replay-digest drift
    # at high severity forces allowed_downstream_use=RCA_ONLY per 06.4
    # doctrine, which would block proposal admission for these proposal/
    # gauntlet tests. Policy drift remains as governance signal.
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
    diff = build_proposed_diff_manifest(
        target_surface="prompt",
        operation_type="UPDATE",
        before_ref="p1",
        after_candidate_ref="p2",
        diff_summary="d",
        exact_patch_ref="patch",
    )
    blast = build_blast_radius(proposal_id="pending", affected_surfaces=["prompt"], affected_tests=["t1"])
    rollback = build_rollback_plan(proposal_id="pending", rollback_steps=["revert prompt"])
    proposal = draft_proposal(
        proposal_type="PROMPT_UPDATE",
        target_surface="prompt",
        current_version_ref="p1",
        proposed_version_ref="p2",
        problem_statement="prompt drift",
        completed_eval_record=completed,
        rca_packet=rca,
        pattern=None,
        proposed_diff=diff,
        expected_effect="reduce drift",
        rollback_plan=rollback,
        blast_radius=blast,
        affected_tests=["t1"],
        migration_notes="",
        owner="o",
        signer_identity="o@org",
        policy_hash="A",
    )
    test_plan = build_test_plan(proposal_id=proposal.proposal_id, affected_tests=["t1"])
    admission = admit_proposal(
        proposal,
        test_plan=test_plan,
        completed_eval_record=completed,
        rca_packet=rca,
        pattern=None,
    )
    return completed, rca, proposal, admission


def test_gauntlet_requires_rollback_rehearsal(proposal_bundle):
    _c, _r, proposal, _a = proposal_bundle
    with pytest.raises(GauntletError):
        run_gauntlet(proposal, rollback_rehearsal_ref="")


def test_gauntlet_pass_when_no_failing_cases(proposal_bundle):
    _c, _r, proposal, _a = proposal_bundle
    receipt = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1")
    assert receipt.pass_fail_hold_verdict == "GAUNTLET_PASS"
    assert receipt.proposal_content_hash == proposal_content_hash(proposal)


def test_gauntlet_fail_with_failing_cases(proposal_bundle):
    _c, _r, proposal, _a = proposal_bundle
    receipt = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1", failing_cases=["case-A"])
    assert receipt.pass_fail_hold_verdict == "GAUNTLET_FAIL"


def test_approval_rejects_when_gauntlet_failed(proposal_bundle):
    completed, rca, proposal, admission = proposal_bundle
    gauntlet = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1", failing_cases=["case-A"])
    decision = decide_approval(
        proposal,
        admission=admission,
        gauntlet=gauntlet,
        completed_eval_record=completed,
        rca_packet=rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    assert decision.decision == "REJECT"
    assert "GAUNTLET_FAIL" in decision.reason_codes


def test_approval_holds_for_stale_eval(proposal_bundle):
    completed, rca, proposal, admission = proposal_bundle
    gauntlet = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1")
    decision = decide_approval(
        proposal,
        admission=admission,
        gauntlet=gauntlet,
        completed_eval_record=completed,
        rca_packet=rca,
        eval_freshness_ok=False,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    assert decision.decision == "HOLD_FOR_MORE_EVIDENCE"
    assert "STALE_EVAL" in decision.reason_codes


def test_approval_requires_rollback(proposal_bundle):
    completed, rca, proposal, admission = proposal_bundle
    gauntlet = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1")
    decision = decide_approval(
        proposal,
        admission=admission,
        gauntlet=gauntlet,
        completed_eval_record=completed,
        rca_packet=rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=False,
        blast_radius_accepted=True,
    )
    assert decision.decision == "REQUIRE_ROLLBACK_PLAN"


def test_promotion_packet_content_hash_pinned(proposal_bundle):
    completed, rca, proposal, admission = proposal_bundle
    gauntlet = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1")
    decision = decide_approval(
        proposal,
        admission=admission,
        gauntlet=gauntlet,
        completed_eval_record=completed,
        rca_packet=rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    promotion = build_promotion_packet(
        proposal,
        approval=decision,
        completed_eval_record=completed,
        rca_packet=rca,
        gauntlet=gauntlet,
        target_version_current="p1",
        target_version_proposed="p2",
    )
    assert promotion.content_hash == proposal_content_hash(proposal)
    assert promotion.gauntlet_receipt == gauntlet.gauntlet_receipt_id


def test_promotion_blocked_when_content_hash_mismatch(proposal_bundle):
    """Doctrine: gauntlet must cover same content as the approval target."""
    completed, rca, proposal, admission = proposal_bundle
    gauntlet = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1")
    # Tamper with a field that participates in proposal_content_hash so the
    # recomputed hash diverges from the gauntlet's pinned hash.
    tampered = dataclasses.replace(proposal, current_version_ref="p1-DIFFERENT")
    decision = decide_approval(
        tampered,
        admission=admission,
        gauntlet=gauntlet,
        completed_eval_record=completed,
        rca_packet=rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    # decide_approval surfaces the mismatch as REJECT with the explicit reason
    assert decision.decision == "REJECT"
    assert "CONTENT_HASH_MISMATCH" in decision.reason_codes
    # And build_promotion_packet must refuse to build off a non-APPROVE decision
    with pytest.raises(GauntletError):
        build_promotion_packet(
            tampered,
            approval=decision,
            completed_eval_record=completed,
            rca_packet=rca,
            gauntlet=gauntlet,
            target_version_current="p1",
            target_version_proposed="p2",
        )


def test_activation_requires_uwg_receipt(proposal_bundle):
    completed, rca, proposal, admission = proposal_bundle
    gauntlet = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1")
    decision = decide_approval(
        proposal,
        admission=admission,
        gauntlet=gauntlet,
        completed_eval_record=completed,
        rca_packet=rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    promotion = build_promotion_packet(
        proposal,
        approval=decision,
        completed_eval_record=completed,
        rca_packet=rca,
        gauntlet=gauntlet,
        target_version_current="p1",
        target_version_proposed="p2",
    )
    # No UWG receipt bound yet -> activation must refuse.
    with pytest.raises(GauntletError):
        build_future_run_activation_receipt(promotion, alias_updated=True)


def test_full_promotion_path_emits_activation(proposal_bundle):
    completed, rca, proposal, admission = proposal_bundle
    gauntlet = run_gauntlet(proposal, rollback_rehearsal_ref="rehearsal-1")
    decision = decide_approval(
        proposal,
        admission=admission,
        gauntlet=gauntlet,
        completed_eval_record=completed,
        rca_packet=rca,
        eval_freshness_ok=True,
        calibration_freshness_ok=True,
        signer_authority_ok=True,
        rollback_verified=True,
        blast_radius_accepted=True,
    )
    promotion = build_promotion_packet(
        proposal,
        approval=decision,
        completed_eval_record=completed,
        rca_packet=rca,
        gauntlet=gauntlet,
        target_version_current="p1",
        target_version_proposed="p2",
    )
    pkg = build_uwg_request_package(
        promotion,
        version_bump="p1->p2",
        alias_swap_plan="alias-default",
        cache_read_surface_refresh_plan="cache-default",
    )
    assert pkg.content_hash == promotion.content_hash
    promotion, proof = bind_uwg_receipt(promotion, uwg_receipt_id="uwg-99", l4_version_digest="l4-digest-A")
    activation = build_future_run_activation_receipt(promotion, alias_updated=True)
    assert activation.activate_at == "NEXT_RUN_START"
    assert activation.no_current_run_mutation_assertion is True
    assert activation.no_retroactive_regrade_assertion is True
    assert activation.bus_u_publish_marker == "DEFERRED_UNTIL_RUN_START"
    assert proof.uwg_receipt_id == "uwg-99"
    assert promotion.uwg_receipt_id == "uwg-99"


def test_l6_does_not_write_to_l4_directly():
    """Static proof: gauntlet module exposes no L4 write client.

    The only path L4 mutation is via the UwgCommitFn callback the caller
    injects. The signature documents this; the package does not import any
    UWG/L4 client.
    """
    import agentic_core.L6_observability.shadow_eval.gauntlet as g

    src = open(g.__file__, encoding="utf-8").read()
    assert "uwg_client" not in src
    assert "L4_state.write" not in src
    # The gauntlet module accepts a callable but does not invoke any module-
    # level write API. The runtime check is that uwg_commit is the parameter.
    assert "uwg_commit" not in src or "Callable" in src
