from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agentic_core.L4_state.contracts import (
    AppDomainContractRecord,
    AppInputContractRecord,
    AppOutputSchemaRecord,
    InMemoryAppDomainStore,
    TaskClassEntry,
    UnknownAppContractError,
)
from agentic_core.L4_state.uwg import (
    AppDomainContractBundle,
    DurableWriteGateway,
    register_judge_calibration_baseline,
)
from agentic_core.L6_observability.shadow_eval import (
    GovernanceBaseline,
    run_6c,
    run_6d,
    run_proposal,
)
from agentic_core.L6_observability.shadow_eval.spearman_calibration import (
    CalibrationContext,
    CalibrationMode,
    CalibrationSample,
    SpearmanCalibrationProfile,
)
from agentic_core.runtime.exhaust.runtime_exhaust_bundle import (
    build_runtime_exhaust_bundle,
)
from apps_rg.runtime.bindings.exit_binding import (
    ExitGateVerdict,
    _resolve_judge_reliability_gate,
)
from apps_rg.runtime.bindings.judge_calibration_baseline import (
    build_apps_rg_judge_calibration_baseline,
)
from apps_rg.runtime.spine.governed_l6_shadow_compose import (
    run_integrated_exhaust_through_l6,
)

RUBRIC_HASH = "e3cec96dfac21b61056f4f5d1d150fa769e3242a5e4b93c4c907afe8b731fdb1"


def _profile() -> SpearmanCalibrationProfile:
    return SpearmanCalibrationProfile(
        app_id="apps_rg",
        task_class="resume_generation",
        judge_id="rg::executive_positioning_judge::v1",
        judge_version="v1",
        rubric_hash=RUBRIC_HASH,
        rubric_version="1.0.0",
        provider_profile_ref="local_qwen_generator",
        minimum_samples=4,
        minimum_spearman_rho=0.8,
        maximum_p_value=0.05,
        informational_only=True,
        required_for_exit=False,
    )


def _samples(judge_scores: list[float]) -> tuple[CalibrationSample, ...]:
    return tuple(
        CalibrationSample(
            sample_id=f"sample-{index}",
            dataset_id="apps_rg_executive_positioning",
            dataset_version="v1",
            human_score=float(index + 1),
            judge_score=score,
            label_source="human_semantic_review",
            candidate_text=f"candidate {index}",
            reviewer_refs=(f"reviewer-a-{index}", f"reviewer-b-{index}"),
            content_digest=f"sha256:{index:064x}",
            task_class="resume_generation",
            judge_id="rg::executive_positioning_judge::v1",
            rubric_hash=RUBRIC_HASH,
            rubric_version="1.0.0",
        )
        for index, score in enumerate(judge_scores)
    )


def _runtime_bundle():
    return build_runtime_exhaust_bundle(
        request_id="request-1",
        run_id="run-1",
        trace_root="trace-1",
        route_contract_ref="route-contract-1",
        sealed_result_ref="sealed-result-1",
        gate_mesh_result_ref="gate-mesh-1",
        exit_disposition_ref="exit-disposition-1",
        runtime_receipt_refs=("runtime-receipt-1",),
        l5_certification_packet_ref="l5-cert-ref:test",
    )


def _spans() -> tuple[dict, ...]:
    return (
        {
            "name": "exit.disposition",
            "kind": "exit",
            "layer": "L5_safety",
            "trace_id": "trace-1",
            "span_id": "span-exit",
            "parent_span_id": "",
            "status": "ok",
            "attributes": {
                "provider_lane": "local_qwen_generator",
                "prompt_hash": "prompt-hash-1",
                "artifact_digest": "artifact-digest-1",
                "eval_readiness_hint": "READY",
            },
        },
    )


def _run(scores: list[float]):
    bundle = _runtime_bundle()
    before = bundle.as_dict()
    profile = _profile()
    state = run_integrated_exhaust_through_l6(
        bundle,
        spans=_spans(),
        governance_baseline=GovernanceBaseline(
            policy_hash="policy-1",
            rubric_hash=RUBRIC_HASH,
            replay_digest=bundle.deterministic_digest,
        ),
        calibration_context=CalibrationContext(
            mode=CalibrationMode.RUN_HUMAN_ALIGNMENT_CALIBRATION,
            profile=profile,
            samples=_samples(scores),
        ),
        blueprint_hash="blueprint-1",
    )
    assert bundle.as_dict() == before
    assert state.eval is not None
    return bundle, state


def _base_domain_bundle() -> AppDomainContractBundle:
    return AppDomainContractBundle(
        contract=AppDomainContractRecord(
            app_domain_contract_id="adc::apps_rg::spearman-test::v1",
            app_id="apps_rg",
            app_version="1.0.0",
            domain="resume_generation",
            owner_surface="apps_rg",
            status="active",
            task_classes=(
                TaskClassEntry(
                    task_class="resume_generation",
                    kind="generation",
                    description="resume generation",
                ),
            ),
            negative_control_refs=("negative-control::spearman-test",),
            policy_hash="policy-1",
            blueprint_hash="blueprint-1",
        ),
        input_contract=AppInputContractRecord(
            input_contract_id="aic::apps_rg::spearman-test::v1",
            app_id="apps_rg",
            task_class="resume_generation",
            version="1.0.0",
            status="active",
            missing_input_behavior="fail_closed",
            ambiguity_behavior="escalate",
        ),
        output_schema=AppOutputSchemaRecord(
            output_schema_id="aos::apps_rg::spearman-test::v1",
            app_id="apps_rg",
            task_class="resume_generation",
            version="1.0.0",
            status="active",
            output_type="structured_record",
        ),
    )


def test_post_exit_bridge_reaches_l64_without_current_run_mutation():
    _, state = _run([0.1, 0.2, 0.3, 0.4, 0.5])
    assert state.readiness is not None
    assert state.readiness.readiness_decision == "READY_FOR_6B"
    assert state.eval.calibration_result is not None
    assert state.eval.calibration_result.status == "PASS"
    assert state.eval.completed.judge_reliability_signal_ref


def test_weak_calibration_produces_rca_and_hybrid_fallback():
    _, state = _run([0.5, 0.4, 0.3, 0.2, 0.1])
    assert state.eval is not None and state.eval.judge_reliability is not None
    assert state.eval.judge_reliability.recommended_use == "REQUIRE_HYBRID"
    rca = run_6c(state)
    assert rca.calibration_failure is not None
    assert rca.rca.root_cause_class == "RUBRIC_CALIBRATION_ERROR"


def test_passed_calibration_promotes_via_uwg_and_next_exit_reads_baseline():
    _, state = _run([0.1, 0.2, 0.3, 0.4, 0.5])
    run_6c(state)
    run_proposal(
        state,
        proposal_type="RUBRIC_UPDATE",
        target_surface="rubric",
        current_version_ref="rubric-v1",
        proposed_version_ref="rubric-v2",
        problem_statement="calibration baseline promotion",
        expected_effect="bind approved judge reliability for future runs",
        rollback_steps=["restore rubric-v1"],
        affected_surfaces=["apps_rg executive positioning judge"],
        affected_tests=["test_spearman_l6_calibration_spine"],
        owner="calibration-owner",
        signer_identity="calibration-owner@example.test",
        sme_signoff_ref="sme-signoff::human-calibration-owner",
    )
    store = InMemoryAppDomainStore()
    gateway = DurableWriteGateway()

    def commit_through_uwg(promotion):
        assert promotion.promotion_packet_id
        return "uwg::promotion::test-approved", "l4::promotion::test-digest"

    promoted = run_6d(
        state,
        uwg_commit=commit_through_uwg,
        target_version_current="rubric-v1",
        target_version_proposed="rubric-v2",
        rollback_rehearsal_ref="rollback-rehearsal::pass",
    )
    assert promoted.approval_decision == "APPROVE"
    assert state.eval is not None and state.eval.calibration_result is not None
    baseline = build_apps_rg_judge_calibration_baseline(
        state.eval.calibration_result,
        promoted,
        approved_at=datetime.now(timezone.utc).isoformat(),
        expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    )
    with pytest.raises(UnknownAppContractError):
        store.get_judge_calibration_baseline(baseline.baseline_id)
    receipt = register_judge_calibration_baseline(
        _base_domain_bundle(),
        baseline,
        gateway=gateway,
        store=store,
        l5_certification_ref="test:valid:spearman-calibration",
        clearance_proof_id="clearance::test::spearman-calibration",
        commit_request_signature="signature::test::spearman-calibration",
    )
    assert receipt.accepted is True, (
        receipt.blocked_receipt.blocked_reason_codes if receipt.blocked_receipt is not None else ()
    )
    assert baseline.uwg_receipt_ref == promoted.promotion.uwg_receipt_id
    assert store.get_judge_calibration_baseline(baseline.baseline_id) == baseline
    contract = store.get_contract("apps_rg", "resume_generation")
    assert baseline.baseline_id in contract.judge_calibration_baseline_refs
    next_run_gate = _resolve_judge_reliability_gate(
        baseline.baseline_id,
        store=store,
    )
    assert next_run_gate.verdict == ExitGateVerdict.WARN
    assert "ALLOW_ADVISORY_ONLY" in next_run_gate.reason
