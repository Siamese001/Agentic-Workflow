"""06.x pipeline orchestrator — chains 6A → 6B → 6C → 6D end-to-end.

This is the integration surface that the 06.8 acceptance commands exercise.
It records OTEL spans into a ``L6SpanRecorder`` so anti-bypass tests can
assert ordering and the absence of any runtime feedback edge.

The orchestrator never performs an L4 write. It returns receipts and lets
the caller hand them to UWG via an injected callback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Iterable, Mapping

from agentic_core.L6_observability.shadow_eval.calibration import (
    build_calibration_record,
    build_completed_eval_record,
    seal_eval_record,
)
from agentic_core.L6_observability.shadow_eval.contracts import (
    CalibrationRecord,
    CompletedEvalRecord,
    DraftProposalPacket,
    EvalRecordSealReceipt,
    EvalReadinessReceipt,
    ExhaustGapReport,
    ExhaustSourceManifest,
    FutureRunActivationReceipt,
    GauntletReceipt,
    GovernanceRegressionRecord,
    ArtifactInventory,
    L6GateReceipt,
    NormalizedEvidenceRecord,
    OutcomeEvalRecord,
    PatternSynthesisRecord,
    PromotionPacket,
    ProposalAdmissionReceipt,
    RCAPacket,
    RuntimeExhaustBundle,
    StageMap,
    TrajectoryEvalRecord,
)
from agentic_core.L6_observability.shadow_eval.evaluation import (
    GovernanceBaseline,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_trajectory,
)
from agentic_core.L6_observability.shadow_eval.gauntlet import (
    bind_uwg_receipt,
    build_future_run_activation_receipt,
    build_promotion_packet,
    build_uwg_request_package,
    decide_approval,
    run_gauntlet,
)
from agentic_core.L6_observability.shadow_eval.ingest import (
    build_runtime_exhaust_bundle,
)
from agentic_core.L6_observability.shadow_eval.observer import (
    build_g28_audit_completeness_receipt,
    build_g29_learning_firewall_receipt,
    build_observer_compliance_receipt,
    build_surface_isolation_manifest,
    evaluate_readiness,
    stage_barrier_check,
)
from agentic_core.L6_observability.shadow_eval.otel_spans import (
    L6SpanRecord,
    L6SpanRecorder,
)
from agentic_core.L6_observability.shadow_eval.proposal import (
    admit_proposal,
    build_blast_radius,
    build_proposed_diff_manifest,
    build_rollback_plan,
    build_test_plan,
    draft_proposal,
)
from agentic_core.L6_observability.shadow_eval.rca import (
    build_rca_packet,
    fuse_signals,
    synthesize_patterns,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class L6IngestResult:
    bundle: RuntimeExhaustBundle
    normalized: list[NormalizedEvidenceRecord]
    manifests: list[ExhaustSourceManifest] = field(default_factory=list)
    stage_map: StageMap | None = None
    artifact_inventory: ArtifactInventory | None = None
    gap_report: ExhaustGapReport | None = None


@dataclass
class L6EvalResult:
    readiness: EvalReadinessReceipt
    outcome: OutcomeEvalRecord
    trajectory: TrajectoryEvalRecord
    governance: GovernanceRegressionRecord
    calibration: CalibrationRecord
    completed: CompletedEvalRecord
    seal: EvalRecordSealReceipt


@dataclass
class L6RcaResult:
    rca: RCAPacket
    fused_signal_bundle_id: str
    patterns: list[PatternSynthesisRecord] = field(default_factory=list)


@dataclass
class L6ProposalResult:
    proposal: DraftProposalPacket
    admission: ProposalAdmissionReceipt


@dataclass
class L6PromotionResult:
    gauntlet: GauntletReceipt
    promotion: PromotionPacket
    activation: FutureRunActivationReceipt | None
    approval_decision: str


@dataclass
class L6PipelineState:
    recorder: L6SpanRecorder = field(default_factory=L6SpanRecorder)
    ingest: L6IngestResult | None = None
    observer_receipt: object | None = None
    g28: L6GateReceipt | None = None
    g29: L6GateReceipt | None = None
    readiness: EvalReadinessReceipt | None = None
    eval: L6EvalResult | None = None
    rca: L6RcaResult | None = None
    proposal: L6ProposalResult | None = None
    promotion: L6PromotionResult | None = None


def _emit(
    state: L6PipelineState,
    name: str,
    *,
    bundle: RuntimeExhaustBundle | None = None,
    completed_eval_record_id: str | None = None,
    proposal_id: str | None = None,
    promotion_packet_id: str | None = None,
    uwg_receipt_id: str | None = None,
    status: str = "OK",
    reason_codes: list[str] | None = None,
    latency_ms: float = 0.0,
) -> None:
    state.recorder.record(
        L6SpanRecord(
            name=name,
            trace_id=(bundle.trace_root if bundle else "n/a"),
            span_id=name,
            parent_span_id=None,
            request_id=(bundle.request_id if bundle else None),
            run_id=(bundle.run_id if bundle else None),
            tenant_id=(bundle.tenant_id if bundle else None),
            policy_hash=(bundle.policy_hash if bundle else None),
            blueprint_hash=(bundle.blueprint_hash if bundle else None),
            replay_key=(bundle.replay_key if bundle else None),
            source_trace_root=(bundle.trace_root if bundle else None),
            runtime_exhaust_bundle_id=(bundle.runtime_exhaust_bundle_id if bundle else None),
            completed_eval_record_id=completed_eval_record_id,
            proposal_id=proposal_id,
            promotion_packet_id=promotion_packet_id,
            uwg_receipt_id=uwg_receipt_id,
            status=status,
            reason_codes=list(reason_codes or []),
            latency_ms=latency_ms,
        )
    )


# ---------------------------------------------------------------------------
# 6A — ingest
# ---------------------------------------------------------------------------


def run_6a(state: L6PipelineState, raw_exhaust: Mapping[str, object]) -> L6IngestResult:
    _emit(state, "l6.ingest.bundle_receive")
    bundle, normalized, manifests, stage_map, inv, gap = build_runtime_exhaust_bundle(raw_exhaust)
    _emit(state, "l6.ingest.source_collect", bundle=bundle)
    _emit(state, "l6.ingest.lineage_bind", bundle=bundle, reason_codes=gap.gap_codes)
    _emit(state, "l6.ingest.stage_map_build", bundle=bundle)
    _emit(state, "l6.ingest.artifact_inventory", bundle=bundle)
    for _ in normalized:
        _emit(state, "l6.normalize.record_emit", bundle=bundle)
    # Doctrine 06.1 §I3+§I4+§I5: gap report is a first-class artifact when any
    # gap code surfaces. Emit the canonical span so observability captures the
    # repair-required signal without inventing data downstream.
    if gap.gap_codes:
        _emit(
            state,
            "l6.ingest.gap_report_emit",
            bundle=bundle,
            reason_codes=list(gap.gap_codes),
            status="REPAIR_REQUIRED" if gap.repair_required else "GAP_DETECTED",
        )
    state.ingest = L6IngestResult(
        bundle=bundle,
        normalized=normalized,
        manifests=manifests,
        stage_map=stage_map,
        artifact_inventory=inv,
        gap_report=gap,
    )
    return state.ingest


# ---------------------------------------------------------------------------
# 6A.5 — observer + readiness
# ---------------------------------------------------------------------------


def run_observer(state: L6PipelineState) -> EvalReadinessReceipt:
    if state.ingest is None:
        raise RuntimeError("observer requires ingest result")
    bundle = state.ingest.bundle
    # Doctrine 06.8 canonical span order: surface_isolation_check BEFORE
    # stage_barrier_check. We perform the isolation analysis first, then the
    # barrier check, then emit spans in the canonical order.
    isolation = build_surface_isolation_manifest(bundle, read_surfaces_touched=("traces", "artifacts"))
    barrier = stage_barrier_check(bundle)
    _emit(state, "l6.observer.surface_isolation_check", bundle=bundle, status=isolation.isolation_status)
    _emit(state, "l6.observer.stage_barrier_check", bundle=bundle, status=barrier.barrier_status)
    observer_receipt = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=isolation)
    g28 = build_g28_audit_completeness_receipt(
        bundle,
        state.ingest.normalized,
        artifact_inventory=state.ingest.artifact_inventory,
    )
    _emit(state, "l6.g28.audit_completeness", bundle=bundle, status=g28.verdict, reason_codes=g28.reason_codes)
    g29 = build_g29_learning_firewall_receipt(
        bundle,
        isolation=isolation,
        observer_receipt=observer_receipt,
    )
    _emit(state, "l6.g29.learning_firewall", bundle=bundle, status=g29.verdict, reason_codes=g29.reason_codes)
    readiness, _missing, _non = evaluate_readiness(
        bundle,
        observer_receipt,
        state.ingest.normalized,
        artifact_inventory=state.ingest.artifact_inventory,
        g28_receipt=g28,
        g29_receipt=g29,
    )
    _emit(state, "l6.readiness.evaluate", bundle=bundle, status=readiness.readiness_decision)
    state.observer_receipt = observer_receipt
    state.g28 = g28
    state.g29 = g29
    state.readiness = readiness
    return readiness


# ---------------------------------------------------------------------------
# 6B — evaluate + seal
# ---------------------------------------------------------------------------


def run_6b(
    state: L6PipelineState,
    readiness: EvalReadinessReceipt,
    *,
    governance_baseline: GovernanceBaseline,
    rubric_hash: str = "rubric:l6:default-v1",
    rubric_version: str = "1.0.0",
    grader_version: str = "code-only-v1",
    calibration_freshness_timestamp: str | None = None,
) -> L6EvalResult:
    if state.ingest is None:
        raise RuntimeError("6B requires ingest result")
    bundle = state.ingest.bundle
    normalized = state.ingest.normalized

    _emit(state, "l6.eval.outcome.start", bundle=bundle)
    outcome = evaluate_outcome(readiness, normalized)
    _emit(state, "l6.eval.outcome.record_emit", bundle=bundle)

    _emit(state, "l6.eval.trajectory.start", bundle=bundle)
    trajectory = evaluate_trajectory(readiness, normalized)
    _emit(state, "l6.eval.trajectory.record_emit", bundle=bundle)

    _emit(state, "l6.eval.governance_regression.start", bundle=bundle)
    governance = evaluate_governance_regression(readiness, normalized, governance_baseline)
    _emit(state, "l6.eval.governance_regression.record_emit", bundle=bundle)

    calibration = build_calibration_record(
        rubric_hash=rubric_hash,
        rubric_version=rubric_version,
        grader_version=grader_version,
        calibration_freshness_timestamp=calibration_freshness_timestamp or _now_iso(),
    )
    _emit(state, "l6.calibration.record_emit", bundle=bundle)

    completed = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=readiness.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
        readiness_decision=readiness.readiness_decision,
    )
    seal = seal_eval_record(completed, calibration)
    _emit(
        state,
        "l6.eval_record.seal",
        bundle=bundle,
        completed_eval_record_id=completed.completed_eval_record_id,
        status=seal.seal_status,
    )
    state.eval = L6EvalResult(
        readiness=readiness,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
        completed=completed,
        seal=seal,
    )
    return state.eval


# ---------------------------------------------------------------------------
# 6C — RCA + pattern synthesis
# ---------------------------------------------------------------------------


def run_6c(
    state: L6PipelineState,
    *,
    incident_id: str | None = None,
    rca_history: Iterable[RCAPacket] | None = None,
    minimum_recurrence: int = 2,
) -> L6RcaResult:
    """Run 6C signal fusion + RCA, optionally synthesizing patterns.

    Per 06.5 doctrine the pattern record is emitted only when the recurrence
    threshold across ``rca_history`` (plus the freshly built RCA) is met.
    Passing ``rca_history`` enables this; omitting it preserves single-incident
    behavior with no spurious pattern emission.
    """
    if state.eval is None or state.ingest is None:
        raise RuntimeError("6C requires 6B and ingest results")
    bundle = state.ingest.bundle
    fused = fuse_signals([state.eval.completed])
    _emit(
        state,
        "l6.rca.signal_fusion",
        bundle=bundle,
        completed_eval_record_id=state.eval.completed.completed_eval_record_id,
    )
    rca = build_rca_packet(
        fused,
        normalized=state.ingest.normalized,
        trajectory=state.eval.trajectory,
        governance=state.eval.governance,
        incident_id=incident_id,
    )
    _emit(
        state,
        "l6.rca.packet_emit",
        bundle=bundle,
        completed_eval_record_id=state.eval.completed.completed_eval_record_id,
    )
    patterns: list[PatternSynthesisRecord] = []
    if rca_history is not None:
        all_rcas = [*list(rca_history), rca]
        patterns = list(
            synthesize_patterns(all_rcas, minimum_recurrence=minimum_recurrence)
        )
        for _pattern in patterns:
            _emit(
                state,
                "l6.pattern.record_emit",
                bundle=bundle,
                completed_eval_record_id=state.eval.completed.completed_eval_record_id,
                status="RECURRENT",
            )
    state.rca = L6RcaResult(
        rca=rca,
        fused_signal_bundle_id=fused.fused_signal_bundle_id,
        patterns=patterns,
    )
    return state.rca


# ---------------------------------------------------------------------------
# 6C.5 — proposal drafting + admission
# ---------------------------------------------------------------------------


def run_proposal(
    state: L6PipelineState,
    *,
    proposal_type: str,
    target_surface: str,
    current_version_ref: str,
    proposed_version_ref: str | None,
    problem_statement: str,
    expected_effect: str,
    rollback_steps: list[str],
    affected_surfaces: list[str],
    affected_tests: list[str],
    owner: str,
    signer_identity: str,
    policy_hash: str = "",
    rollout_risk_score: float = 0.0,
    diff_summary: str = "diff",
    before_ref: str = "before",
    after_candidate_ref: str = "after",
) -> L6ProposalResult:
    if state.eval is None or state.rca is None or state.ingest is None:
        raise RuntimeError("proposal requires 6B and 6C results")
    bundle = state.ingest.bundle

    diff = build_proposed_diff_manifest(
        target_surface=target_surface,
        operation_type="UPDATE",
        before_ref=before_ref,
        after_candidate_ref=after_candidate_ref,
        diff_summary=diff_summary,
        exact_patch_ref=after_candidate_ref,
        affected_surfaces=affected_surfaces,
    )
    proposal_id_temp = "proposal-pending"
    blast = build_blast_radius(
        proposal_id=proposal_id_temp,
        affected_surfaces=affected_surfaces,
        affected_tests=affected_tests,
        rollout_risk_score=rollout_risk_score,
    )
    rollback = build_rollback_plan(
        proposal_id=proposal_id_temp,
        rollback_steps=rollback_steps,
    )
    proposal = draft_proposal(
        proposal_type=proposal_type,
        target_surface=target_surface,
        current_version_ref=current_version_ref,
        proposed_version_ref=proposed_version_ref,
        problem_statement=problem_statement,
        completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca,
        pattern=None,
        proposed_diff=diff,
        expected_effect=expected_effect,
        rollback_plan=rollback,
        blast_radius=blast,
        affected_tests=affected_tests,
        migration_notes="",
        owner=owner,
        signer_identity=signer_identity,
        policy_hash=policy_hash,
    )
    _emit(state, "l6.proposal.draft", bundle=bundle, proposal_id=proposal.proposal_id)
    test_plan = build_test_plan(
        proposal_id=proposal.proposal_id,
        affected_tests=affected_tests,
    )
    admission = admit_proposal(
        proposal,
        test_plan=test_plan,
        completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca,
        pattern=None,
    )
    _emit(
        state,
        "l6.proposal.admission_receipt",
        bundle=bundle,
        proposal_id=proposal.proposal_id,
        status=admission.decision,
    )
    state.proposal = L6ProposalResult(proposal=proposal, admission=admission)
    return state.proposal


# ---------------------------------------------------------------------------
# 6D — gauntlet / approval / promotion / activation
# ---------------------------------------------------------------------------


UwgCommitFn = Callable[["PromotionPacket"], tuple[str, str]]
"""Callable injected by caller; returns ``(uwg_receipt_id, l4_version_digest)``.

L6 NEVER writes to L4 directly. The caller (UWG client outside L6) is the
only path that performs the durable commit. This signature documents that.
"""


def run_6d(
    state: L6PipelineState,
    *,
    uwg_commit: UwgCommitFn,
    target_version_current: str,
    target_version_proposed: str,
    rollback_rehearsal_ref: str,
    eval_freshness_ok: bool = True,
    calibration_freshness_ok: bool = True,
    signer_authority_ok: bool = True,
    rollback_verified: bool = True,
    blast_radius_accepted: bool = True,
    failing_cases: list[str] | None = None,
) -> L6PromotionResult:
    if state.proposal is None or state.eval is None or state.rca is None or state.ingest is None:
        raise RuntimeError("6D requires proposal, 6B, 6C and ingest results")
    bundle = state.ingest.bundle

    _emit(state, "l6.gauntlet.run", bundle=bundle, proposal_id=state.proposal.proposal.proposal_id)
    gauntlet = run_gauntlet(
        state.proposal.proposal,
        rollback_rehearsal_ref=rollback_rehearsal_ref,
        failing_cases=failing_cases or [],
    )
    _emit(
        state,
        "l6.gauntlet.receipt_emit",
        bundle=bundle,
        proposal_id=state.proposal.proposal.proposal_id,
        status=gauntlet.pass_fail_hold_verdict,
    )

    approval = decide_approval(
        state.proposal.proposal,
        admission=state.proposal.admission,
        gauntlet=gauntlet,
        completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca,
        eval_freshness_ok=eval_freshness_ok,
        calibration_freshness_ok=calibration_freshness_ok,
        signer_authority_ok=signer_authority_ok,
        rollback_verified=rollback_verified,
        blast_radius_accepted=blast_radius_accepted,
    )
    _emit(
        state,
        "l6.approval.decide",
        bundle=bundle,
        proposal_id=state.proposal.proposal.proposal_id,
        status=approval.decision,
    )

    if approval.decision != "APPROVE":
        # No promotion when not approved; doctrine requires we stop cleanly.
        state.promotion = L6PromotionResult(
            gauntlet=gauntlet,
            promotion=None,  # type: ignore[arg-type]
            activation=None,
            approval_decision=approval.decision,
        )
        return state.promotion

    promotion = build_promotion_packet(
        state.proposal.proposal,
        approval=approval,
        completed_eval_record=state.eval.completed,
        rca_packet=state.rca.rca,
        gauntlet=gauntlet,
        target_version_current=target_version_current,
        target_version_proposed=target_version_proposed,
    )
    _emit(
        state,
        "l6.promotion.packet_build",
        bundle=bundle,
        proposal_id=state.proposal.proposal.proposal_id,
        promotion_packet_id=promotion.promotion_packet_id,
    )
    _pkg = build_uwg_request_package(
        promotion,
        version_bump=f"{target_version_current}->{target_version_proposed}",
        alias_swap_plan="alias_swap_default",
        cache_read_surface_refresh_plan="cache_refresh_default",
    )
    _emit(
        state,
        "l6.promotion.uwg_request_package",
        bundle=bundle,
        promotion_packet_id=promotion.promotion_packet_id,
    )
    uwg_receipt_id, l4_digest = uwg_commit(promotion)
    promotion, _proof = bind_uwg_receipt(
        promotion, uwg_receipt_id=uwg_receipt_id, l4_version_digest=l4_digest
    )
    _emit(
        state,
        "l6.promotion.uwg_receipt_bind",
        bundle=bundle,
        promotion_packet_id=promotion.promotion_packet_id,
        uwg_receipt_id=uwg_receipt_id,
    )
    activation = build_future_run_activation_receipt(promotion, alias_updated=True)
    _emit(
        state,
        "l6.future_run.activation_receipt",
        bundle=bundle,
        promotion_packet_id=promotion.promotion_packet_id,
        uwg_receipt_id=uwg_receipt_id,
    )
    state.promotion = L6PromotionResult(
        gauntlet=gauntlet,
        promotion=promotion,
        activation=activation,
        approval_decision=approval.decision,
    )
    return state.promotion


__all__ = [
    "L6IngestResult",
    "L6EvalResult",
    "L6RcaResult",
    "L6ProposalResult",
    "L6PromotionResult",
    "L6PipelineState",
    "UwgCommitFn",
    "run_6a",
    "run_observer",
    "run_6b",
    "run_6c",
    "run_proposal",
    "run_6d",
]
