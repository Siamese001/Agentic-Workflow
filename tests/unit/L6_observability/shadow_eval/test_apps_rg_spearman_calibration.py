from __future__ import annotations

import math
from dataclasses import replace

from agentic_core.L6_observability.shadow_eval import (
    GovernanceBaseline,
    L6PipelineState,
    build_calibration_record,
    run_6a,
    run_6b,
    run_observer,
)
from agentic_core.L6_observability.shadow_eval.spearman_calibration import (
    CalibrationContext,
    CalibrationMode,
    CalibrationSample,
    SpearmanCalibrationProfile,
    compute_spearman_calibration,
)


def _profile(*, minimum_samples: int = 4) -> SpearmanCalibrationProfile:
    return SpearmanCalibrationProfile(
        app_id="apps_rg",
        task_class="resume_generation",
        judge_id="rg::executive_positioning_judge::v1",
        judge_version="v1",
        rubric_hash="rubric-hash",
        rubric_version="1.0.0",
        provider_profile_ref="local_qwen_generator",
        minimum_samples=minimum_samples,
        minimum_spearman_rho=0.8,
        maximum_p_value=0.05,
        informational_only=True,
        required_for_exit=False,
    )


def _samples(
    judge_scores: list[float],
    *,
    human_scores: list[float] | None = None,
    label_source: str = "human_semantic_review",
) -> tuple[CalibrationSample, ...]:
    humans = human_scores or [float(i + 1) for i in range(len(judge_scores))]
    return tuple(
        CalibrationSample(
            sample_id=f"s-{index}",
            dataset_id="apps-rg-exec-positioning",
            dataset_version="v1",
            human_score=humans[index],
            judge_score=score,
            label_source=label_source,
            reviewer_refs=(f"reviewer-a-{index}", f"reviewer-b-{index}"),
            content_digest=f"sha256:sample-{index}",
            task_class="resume_generation",
            judge_id="rg::executive_positioning_judge::v1",
            rubric_hash="rubric-hash",
            rubric_version="1.0.0",
        )
        for index, score in enumerate(judge_scores)
    )


def test_perfect_human_alignment_is_digest_bound_and_promotion_eligible():
    result = compute_spearman_calibration(
        _samples([0.1, 0.2, 0.3, 0.4, 0.5]),
        _profile(),
        computed_at="2026-07-13T12:00:00+00:00",
    )
    assert result.status == "PASS"
    assert result.spearman_rho == 1.0
    assert result.promotion_eligible is True
    assert result.human_score_digest
    assert result.judge_score_digest
    assert result.deterministic_digest


def test_inverse_alignment_fails_closed():
    result = compute_spearman_calibration(
        _samples([0.5, 0.4, 0.3, 0.2, 0.1]),
        _profile(),
    )
    assert result.status == "BELOW_THRESHOLD"
    assert result.spearman_rho == -1.0
    assert result.promotion_eligible is False
    assert "RHO_BELOW_THRESHOLD" in result.failure_reason_codes


def test_tied_ranks_are_deterministic():
    samples = _samples(
        [0.1, 0.1, 0.4, 0.4, 0.9],
        human_scores=[1.0, 1.0, 2.0, 2.0, 3.0],
    )
    first = compute_spearman_calibration(samples, _profile(), computed_at="fixed")
    second = compute_spearman_calibration(samples, _profile(), computed_at="fixed")
    assert first.spearman_rho == 1.0
    assert first.deterministic_digest == second.deterministic_digest


def test_constant_and_non_finite_sets_are_rejected():
    human_constant = compute_spearman_calibration(
        _samples([0.1, 0.2, 0.3, 0.4], human_scores=[1.0] * 4),
        _profile(),
    )
    judge_constant = compute_spearman_calibration(
        _samples([0.2] * 4),
        _profile(),
    )
    non_finite = compute_spearman_calibration(
        _samples([0.1, 0.2, math.nan, 0.4]),
        _profile(),
    )
    assert human_constant.status == "INVALID_CALIBRATION_SET"
    assert judge_constant.status == "JUDGE_COLLAPSE"
    assert non_finite.status == "INSUFFICIENT"


def test_minimum_sample_and_synthetic_promotion_controls():
    insufficient = compute_spearman_calibration(
        _samples([0.1, 0.2, 0.3]),
        _profile(minimum_samples=4),
    )
    synthetic = compute_spearman_calibration(
        _samples(
            [0.1, 0.2, 0.3, 0.4, 0.5],
            label_source="heuristic_sanity_synthetic",
        ),
        _profile(),
    )
    assert insufficient.status == "INSUFFICIENT"
    assert synthetic.status == "PASS"
    assert synthetic.promotion_eligible is False
    assert synthetic.fallback_only is True
    assert "NON_HUMAN_LABEL_SOURCE_NOT_PROMOTION_ELIGIBLE" in (synthetic.failure_reason_codes)


def test_heuristic_profile_cannot_enable_synthetic_promotion():
    profile = replace(_profile(), promotion_requires_human_labels=False)
    synthetic = compute_spearman_calibration(
        _samples(
            [0.1, 0.2, 0.3, 0.4, 0.5],
            label_source="heuristic_sanity_synthetic",
        ),
        profile,
    )
    assert synthetic.status == "PASS"
    assert synthetic.promotion_eligible is False


def test_sample_identity_mismatch_is_insufficient():
    samples = list(_samples([0.1, 0.2, 0.3, 0.4]))
    samples[0] = replace(samples[0], judge_id="rg::different-judge::v1")
    result = compute_spearman_calibration(samples, _profile())
    assert result.status == "INSUFFICIENT"
    assert "JUDGE_ID_MISSING_OR_MISMATCHED" in result.failure_reason_codes


def test_dataset_identity_must_match_profile_when_declared():
    profile = replace(
        _profile(),
        dataset_id="different-dataset",
        dataset_version="v2",
    )
    result = compute_spearman_calibration(
        _samples([0.1, 0.2, 0.3, 0.4]),
        profile,
    )
    assert result.status == "INSUFFICIENT"
    assert "DATASET_ID_DIFFERS_FROM_PROFILE" in result.failure_reason_codes
    assert "DATASET_VERSION_DIFFERS_FROM_PROFILE" in result.failure_reason_codes


def test_fresh_timestamp_without_evidence_is_insufficient():
    record = build_calibration_record(
        rubric_hash="rubric-hash",
        rubric_version="1",
        grader_version="v1",
        calibration_freshness_timestamp="2026-07-13T12:00:00+00:00",
    )
    assert record.calibration_status == "INSUFFICIENT"


def test_run_6b_emits_l64_reliability_and_seals_lineage(sealed_completed_run):
    state = L6PipelineState()
    ingest = run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    profile = _profile()
    context = CalibrationContext(
        mode=CalibrationMode.RUN_HUMAN_ALIGNMENT_CALIBRATION,
        profile=profile,
        samples=_samples([0.1, 0.2, 0.3, 0.4, 0.5]),
    )
    result = run_6b(
        state,
        readiness,
        governance_baseline=GovernanceBaseline(
            policy_hash=ingest.bundle.policy_hash,
            rubric_hash=profile.rubric_hash,
            replay_digest=ingest.bundle.replay_key,
        ),
        calibration_context=context,
    )
    assert result.calibration_result is not None
    assert result.judge_reliability is not None
    assert result.calibration.calibration_mode == CalibrationMode.RUN_HUMAN_ALIGNMENT_CALIBRATION.value
    assert result.judge_reliability.recommended_use == "ALLOW_ADVISORY_ONLY"
    assert (
        result.completed.judge_reliability_signal_ref == result.judge_reliability.judge_reliability_signal_id
    )
    assert "l6.calibration.spearman_compute" in state.recorder.names()
    assert "l6.calibration.record_seal" in state.recorder.names()


def test_approved_baseline_mode_reuses_result_without_rescoring(sealed_completed_run):
    profile = _profile()
    approved = compute_spearman_calibration(
        _samples([0.1, 0.2, 0.3, 0.4, 0.5]),
        profile,
    )
    state = L6PipelineState()
    ingest = run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    result = run_6b(
        state,
        readiness,
        governance_baseline=GovernanceBaseline(
            policy_hash=ingest.bundle.policy_hash,
            rubric_hash=profile.rubric_hash,
            replay_digest=ingest.bundle.replay_key,
        ),
        calibration_context=CalibrationContext(
            mode=CalibrationMode.USE_APPROVED_BASELINE,
            profile=profile,
            approved_result=approved,
            approved_baseline_ref="baseline::apps_rg::approved-v1",
        ),
    )
    assert result.calibration.calibration_mode == CalibrationMode.USE_APPROVED_BASELINE.value
    assert result.calibration.approved_baseline_ref == "baseline::apps_rg::approved-v1"
    assert result.judge_reliability is not None
    assert result.judge_reliability.approved_baseline_ref == "baseline::apps_rg::approved-v1"
    assert "l6.calibration.holdout_load" not in state.recorder.names()
    assert "l6.calibration.judge_score" not in state.recorder.names()


def test_approved_baseline_mode_rejects_tampered_result(sealed_completed_run):
    profile = _profile()
    approved = compute_spearman_calibration(
        _samples([0.1, 0.2, 0.3, 0.4, 0.5]),
        profile,
    )
    approved.dataset_version = "tampered"
    state = L6PipelineState()
    ingest = run_6a(state, sealed_completed_run)
    readiness = run_observer(state)
    result = run_6b(
        state,
        readiness,
        governance_baseline=GovernanceBaseline(
            policy_hash=ingest.bundle.policy_hash,
            rubric_hash=profile.rubric_hash,
            replay_digest=ingest.bundle.replay_key,
        ),
        calibration_context=CalibrationContext(
            mode=CalibrationMode.USE_APPROVED_BASELINE,
            profile=profile,
            approved_result=approved,
            approved_baseline_ref="baseline::apps_rg::approved-v1",
        ),
    )
    assert result.calibration.calibration_status == "INSUFFICIENT"
    assert "APPROVED_CALIBRATION_DIGEST_INVALID" in (result.calibration.failure_reason_codes)
    assert result.judge_reliability is None
