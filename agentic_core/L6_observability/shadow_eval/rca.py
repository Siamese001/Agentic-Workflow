"""06.5 — Signal Fusion, RCA, and Pattern Synthesis.

Implements:

* FusedSignalBundle
* FailureChain
* FirstBadSpanLocalization
* RCAPacket
* DriftClusterMap
* AffectedSurfaceCandidateMap
* PatternSynthesisRecord

Hard precondition (06.5):
* Only ``CompletedEvalRecord`` rows whose ``allowed_downstream_use`` includes
  ``RCA_ONLY`` or ``RCA_AND_PROPOSAL`` may be consumed.
* Raw traces and unsealed evaluations cannot enter RCA as learning signal.
"""

from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from typing import Iterable

from agentic_core.L6_observability.shadow_eval._digest import stamp_digest
from agentic_core.L6_observability.shadow_eval.contracts import (
    ROOT_CAUSE_CLASSES,
    AffectedSurfaceCandidateMap,
    CompletedEvalRecord,
    DriftClusterMap,
    FailureChain,
    FirstBadSpanLocalization,
    FusedSignalBundle,
    GovernanceRegressionRecord,
    NormalizedEvidenceRecord,
    OutcomeEvalRecord,
    PatternSynthesisRecord,
    RCAPacket,
    TrajectoryEvalRecord,
)


class RCAError(Exception):
    """Raised when RCA preconditions are violated."""


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


# ---------------------------------------------------------------------------
# Signal fusion
# ---------------------------------------------------------------------------


def _require_consumable(record: CompletedEvalRecord) -> None:
    if record.allowed_downstream_use not in {"RCA_ONLY", "RCA_AND_PROPOSAL"}:
        raise RCAError(
            f"RCA refused: completed eval record allowed_downstream_use={record.allowed_downstream_use!r}"
        )


def fuse_signals(
    completed_evals: Iterable[CompletedEvalRecord],
    *,
    hitl_outcome_refs: Iterable[str] = (),
    denial_reroute_reason_refs: Iterable[str] = (),
    replay_failure_refs: Iterable[str] = (),
    incident_report_refs: Iterable[str] = (),
    red_team_failure_refs: Iterable[str] = (),
    support_report_refs: Iterable[str] = (),
    source_reliability_scores: dict[str, float] | None = None,
    evaluator_reliability_scores: dict[str, float] | None = None,
    recency_weight: float = 1.0,
) -> FusedSignalBundle:
    evals = list(completed_evals)
    for r in evals:
        _require_consumable(r)
    sample_size = len(evals)
    severity = (
        "high"
        if any(r.immutable_score_bundle.get("governance.policy_drift_count", 0) > 0 for r in evals)
        else "low"
    )
    repro = sum(1 for r in evals if r.immutable_score_bundle.get("trajectory.retry_thrash", 1.0) < 0.5) / max(
        sample_size, 1
    )
    user_impact = float(sample_size)
    policy_criticality = float(
        sum(r.immutable_score_bundle.get("governance.policy_drift_count", 0) for r in evals)
    )
    affected_candidates: list[str] = []
    for r in evals:
        if r.immutable_score_bundle.get("governance.policy_drift_count", 0) > 0:
            affected_candidates.append("policy")
        if r.immutable_score_bundle.get("governance.replay_drift_count", 0) > 0:
            affected_candidates.append("replay")
        if r.immutable_score_bundle.get("trajectory.retry_thrash", 1.0) < 0.5:
            affected_candidates.append("execution")

    bundle = FusedSignalBundle(
        fused_signal_bundle_id=_gen_id("fused"),
        completed_eval_record_refs=[r.completed_eval_record_id for r in evals],
        outcome_signal_refs=[r.outcome_eval_ref for r in evals],
        trajectory_signal_refs=[r.trajectory_eval_ref for r in evals],
        governance_signal_refs=[r.governance_regression_ref for r in evals],
        calibration_signal_refs=[r.calibration_record_ref for r in evals],
        hitl_outcome_refs=list(hitl_outcome_refs),
        denial_reroute_reason_refs=list(denial_reroute_reason_refs),
        replay_failure_refs=list(replay_failure_refs),
        incident_report_refs=list(incident_report_refs),
        red_team_failure_refs=list(red_team_failure_refs),
        support_report_refs=list(support_report_refs),
        source_reliability_scores=dict(source_reliability_scores or {}),
        evaluator_reliability_scores=dict(evaluator_reliability_scores or {}),
        sample_size=sample_size,
        severity_class=severity,
        confidence_band="medium" if sample_size >= 5 else "low",
        recency_weight=recency_weight,
        reproducibility_score=repro,
        user_impact_score=user_impact,
        policy_criticality_score=policy_criticality,
        affected_surface_candidates=sorted(set(affected_candidates)),
        recommended_investigation_type=(
            "POLICY_DRIFT"
            if "policy" in affected_candidates
            else "EXECUTION_FAULT"
            if "execution" in affected_candidates
            else "OBSERVATION_ONLY"
        ),
    )
    return stamp_digest(bundle)


# ---------------------------------------------------------------------------
# RCA packet
# ---------------------------------------------------------------------------


def _build_failure_chain(
    trajectory: TrajectoryEvalRecord | None,
    normalized: list[NormalizedEvidenceRecord],
) -> FailureChain:
    steps: list[str] = []
    first_bad: str | None = None
    final_observed: str | None = None
    if trajectory:
        steps.extend(trajectory.trajectory_flags)
    for rec in normalized:
        final_observed = rec.canonical_stage
        if rec.error_code or rec.retry_count > 2:
            steps.append(f"{rec.canonical_stage}:{rec.error_code or 'retry_thrash'}")
            if first_bad is None:
                first_bad = rec.canonical_stage
    return FailureChain(
        failure_chain_id=_gen_id("chain"),
        steps=steps,
        first_bad_stage=first_bad,
        final_observed_stage=final_observed,
    )


def _localize_first_bad_span(
    normalized: list[NormalizedEvidenceRecord],
) -> FirstBadSpanLocalization:
    for rec in normalized:
        if rec.error_code or rec.retry_count > 2:
            return FirstBadSpanLocalization(
                localization_id=_gen_id("loc"),
                span_id=rec.span_id,
                trace_id=rec.trace_id,
                stage=rec.canonical_stage,
                confidence="medium",
            )
    return FirstBadSpanLocalization(
        localization_id=_gen_id("loc"),
        span_id=None,
        trace_id=None,
        stage=None,
        confidence="UNKNOWN",
    )


def _classify_root_cause(
    fused: FusedSignalBundle,
    governance: GovernanceRegressionRecord | None,
    chain: FailureChain,
) -> str:
    if governance and governance.policy_drift_flags:
        return "POLICY_THRESHOLD_ERROR"
    if governance and governance.replay_digest_drift_flags:
        return "REPLAY_INTEGRITY_ERROR"
    if "silent_fallback" in chain.steps or any("retry_thrash" in s for s in chain.steps):
        return "PROVIDER_DRIFT"
    if "execution" in fused.affected_surface_candidates:
        return "TOOL_ARG_SCHEMA_ERROR"
    return "UNKNOWN_ROOT_CAUSE"


def build_rca_packet(
    fused: FusedSignalBundle,
    *,
    normalized: list[NormalizedEvidenceRecord],
    trajectory: TrajectoryEvalRecord | None = None,
    governance: GovernanceRegressionRecord | None = None,
    incident_id: str | None = None,
) -> RCAPacket:
    chain = _build_failure_chain(trajectory, normalized)
    span = _localize_first_bad_span(normalized)
    root_cause = _classify_root_cause(fused, governance, chain)
    if root_cause not in ROOT_CAUSE_CLASSES:
        raise RCAError(f"unknown root_cause_class: {root_cause}")

    affected = list(fused.affected_surface_candidates)
    proposed_fix = affected[0] if affected else None
    no_stable_pattern = (
        "insufficient_sample" if root_cause == "UNKNOWN_ROOT_CAUSE" and fused.sample_size < 3 else None
    )
    confidence = (
        "high"
        if fused.sample_size >= 10 and root_cause != "UNKNOWN_ROOT_CAUSE"
        else "medium"
        if fused.sample_size >= 3
        else "low"
    )

    packet = RCAPacket(
        rca_packet_id=_gen_id("rca"),
        fused_signal_bundle_id=fused.fused_signal_bundle_id,
        failure_chain=chain,
        first_bad_span=span,
        first_bad_stage=chain.first_bad_stage,
        root_cause_class=root_cause,
        affected_surfaces=affected,
        proposed_fix_surface=proposed_fix,
        evidence_links=list(fused.completed_eval_record_refs),
        counterevidence_links=[],
        confidence_band=confidence,
        uncertainty_markers=(["FIRST_BAD_SPAN_UNKNOWN"] if span.confidence == "UNKNOWN" else []),
        incident_id=incident_id,
        no_stable_pattern_reason=no_stable_pattern,
    )
    return stamp_digest(packet)


# ---------------------------------------------------------------------------
# Pattern synthesis
# ---------------------------------------------------------------------------


def synthesize_patterns(
    rca_packets: Iterable[RCAPacket],
    *,
    minimum_recurrence: int = 2,
) -> list[PatternSynthesisRecord]:
    packets = list(rca_packets)
    by_class: dict[str, list[RCAPacket]] = defaultdict(list)
    for p in packets:
        by_class[p.root_cause_class].append(p)

    patterns: list[PatternSynthesisRecord] = []
    for cls, group in by_class.items():
        if len(group) < minimum_recurrence:
            continue
        affected = sorted({s for p in group for s in p.affected_surfaces})
        examples = [p.rca_packet_id for p in group]
        confidence = "high" if len(group) >= 5 else "medium"
        action = "PROPOSE_FIX" if cls != "UNKNOWN_ROOT_CAUSE" else "WATCH"
        rec = PatternSynthesisRecord(
            pattern_id=_gen_id("pattern"),
            rca_packet_refs=[p.rca_packet_id for p in group],
            examples=examples,
            counterexamples=[],
            affected_surfaces=affected,
            pattern_class=cls,
            recurrence_score=float(len(group)),
            blast_radius_estimate="MEDIUM" if len(affected) > 1 else "LOW",
            confidence_band=confidence,
            proposed_action_class=action,
            hold_watch_reason=None if action == "PROPOSE_FIX" else "below_evidence_floor",
        )
        patterns.append(stamp_digest(rec))
    return patterns


def build_drift_cluster_map(
    rca_packets: Iterable[RCAPacket],
) -> DriftClusterMap:
    clusters: dict[str, list[str]] = defaultdict(list)
    for p in rca_packets:
        clusters[p.root_cause_class].append(p.rca_packet_id)
    return DriftClusterMap(
        drift_cluster_map_id=_gen_id("drift"),
        clusters=dict(clusters),
    )


def build_affected_surface_candidate_map(
    fused_bundles: Iterable[FusedSignalBundle],
) -> AffectedSurfaceCandidateMap:
    counter: Counter[str] = Counter()
    for b in fused_bundles:
        counter.update(b.affected_surface_candidates)
    total = sum(counter.values()) or 1
    return AffectedSurfaceCandidateMap(
        affected_surface_candidate_map_id=_gen_id("surf"),
        candidates={k: v / total for k, v in counter.items()},
    )


__all__ = [
    "RCAError",
    "fuse_signals",
    "build_rca_packet",
    "synthesize_patterns",
    "build_drift_cluster_map",
    "build_affected_surface_candidate_map",
]
