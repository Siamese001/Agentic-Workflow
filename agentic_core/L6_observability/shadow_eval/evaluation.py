"""06.3 — Outcome, Trajectory, and Governance Evaluation.

This module produces the three sealed eval records that 6C consumes:

* ``OutcomeEvalRecord`` — answer-level dimensions
* ``TrajectoryEvalRecord`` — process-level dimensions
* ``GovernanceRegressionRecord`` — regression flags vs baseline

Doctrine rules enforced here:

- ``UNKNOWN`` results are preserved; never coerced to PASS.
- 6B refuses to run without an EvalReadinessReceipt with decision in
  ``READY_FOR_6B`` or ``PARTIAL_BUT_SCORABLE``.
- Unsupported claims are surfaced as a list, not silently filtered.
- Evaluation results MUST NOT be used as a live Exit disposition; the
  records are pure data carriers and contain no callable hooks into the
  runtime.

Graders are pluggable. The default ``CodeOnlyGrader`` makes structural,
deterministic decisions from normalized evidence. Tests can inject their
own graders or mocks.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Callable, Iterable, Protocol

from agentic_core.L6_observability.shadow_eval._digest import stamp_digest
from agentic_core.L6_observability.shadow_eval.contracts import (
    EVAL_DIMENSION_RESULTS,
    GRADER_TYPES,
    EvalDimensionScore,
    EvalReadinessReceipt,
    GovernanceRegressionRecord,
    NormalizedEvidenceRecord,
    OutcomeEvalRecord,
    TrajectoryEvalRecord,
)
from agentic_core.L6_observability.shadow_eval.observer import (
    READINESS_PARTIAL,
    READINESS_READY,
)


class EvaluationError(Exception):
    """Raised when 6B is invoked outside doctrine preconditions."""


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


# ---------------------------------------------------------------------------
# Grader protocol
# ---------------------------------------------------------------------------


class DimensionGrader(Protocol):
    """Pluggable grader for a single eval dimension."""

    def grade(
        self,
        dimension_id: str,
        dimension_name: str,
        evidence: list[NormalizedEvidenceRecord],
    ) -> EvalDimensionScore: ...


@dataclass(slots=True)
class CodeOnlyGrader:
    """Deterministic grader that scores from structural evidence only.

    The default grader treats absence of negative signals as PASS. Tests can
    inject custom graders or the ``HybridGrader`` below for mixed strategies.
    """

    grader_version: str = "code-only-v1"
    rubric_hash: str = "rubric:l6:code-only-v1"

    def grade(
        self,
        dimension_id: str,
        dimension_name: str,
        evidence: list[NormalizedEvidenceRecord],
    ) -> EvalDimensionScore:
        # If no evidence at all, the dimension is UNKNOWN. The doctrine bans
        # coercing UNKNOWN to PASS.
        if not evidence:
            return EvalDimensionScore(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                grader_type="code",
                score=0.0,
                threshold=0.5,
                result="UNKNOWN",
                confidence_band="low",
                support_rationale="no evidence available",
                rubric_hash=self.rubric_hash,
                grader_version=self.grader_version,
            )
        # Default heuristic: dimension passes when all evidence carries a
        # readiness hint other than NON_EVALUABLE/UNKNOWN.
        bad = [r for r in evidence if r.eval_readiness_hint in ("NON_EVALUABLE", "UNKNOWN")]
        if bad:
            return EvalDimensionScore(
                dimension_id=dimension_id,
                dimension_name=dimension_name,
                grader_type="code",
                score=0.4,
                threshold=0.5,
                result="WARN",
                confidence_band="medium",
                evidence_refs=[r.normalized_record_id for r in bad],
                support_rationale=f"{len(bad)} record(s) flagged as non-evaluable/unknown",
                rubric_hash=self.rubric_hash,
                grader_version=self.grader_version,
            )
        return EvalDimensionScore(
            dimension_id=dimension_id,
            dimension_name=dimension_name,
            grader_type="code",
            score=0.95,
            threshold=0.5,
            result="PASS",
            confidence_band="high",
            evidence_refs=[r.normalized_record_id for r in evidence],
            support_rationale="structural evidence intact",
            rubric_hash=self.rubric_hash,
            grader_version=self.grader_version,
        )


@dataclass(slots=True)
class HybridGrader:
    """Hybrid grader: structural decision + grader_type=hybrid label.

    Composition is preferred over inheritance here because slot dataclasses
    do not cleanly resolve ``super().grade()`` across the C3 MRO.
    """

    grader_version: str = "hybrid-v1"
    rubric_hash: str = "rubric:l6:hybrid-v1"

    def grade(
        self,
        dimension_id: str,
        dimension_name: str,
        evidence: list[NormalizedEvidenceRecord],
    ) -> EvalDimensionScore:
        # Delegate to a fresh CodeOnlyGrader instance so we get the same
        # structural verdict, then re-label as hybrid.
        score = CodeOnlyGrader().grade(dimension_id, dimension_name, evidence)
        return EvalDimensionScore(
            dimension_id=score.dimension_id,
            dimension_name=score.dimension_name,
            grader_type="hybrid",
            score=score.score,
            threshold=score.threshold,
            result=score.result,
            confidence_band=score.confidence_band,
            evidence_refs=score.evidence_refs,
            support_rationale=score.support_rationale,
            uncertainty_markers=score.uncertainty_markers,
            rubric_hash=self.rubric_hash,
            grader_version=self.grader_version,
        )


# ---------------------------------------------------------------------------
# Precondition check
# ---------------------------------------------------------------------------


def _require_ready(receipt: EvalReadinessReceipt) -> None:
    if receipt.readiness_decision not in (READINESS_READY, READINESS_PARTIAL):
        raise EvaluationError(f"6B refused: readiness_decision={receipt.readiness_decision!r}")


# ---------------------------------------------------------------------------
# Outcome eval
# ---------------------------------------------------------------------------

OUTCOME_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("dim.task_completion", "task_completion"),
    ("dim.answer_correctness", "answer_correctness"),
    ("dim.groundedness", "groundedness"),
    ("dim.citation_support", "citation_support"),
    ("dim.source_coverage", "source_coverage"),
    ("dim.evidence_sufficiency", "evidence_sufficiency"),
    ("dim.abstain_correctness", "abstain_correctness"),
    ("dim.refusal_correctness", "refusal_correctness"),
    ("dim.format_schema_fit", "format_schema_fit"),
    ("dim.user_constraint_adherence", "user_constraint_adherence"),
    ("dim.scope_discipline", "scope_discipline"),
    ("dim.usefulness", "usefulness"),
    ("dim.artifact_validity", "artifact_validity"),
)


def evaluate_outcome(
    readiness: EvalReadinessReceipt,
    normalized: list[NormalizedEvidenceRecord],
    *,
    grader: DimensionGrader | None = None,
    completed_run_ref: str = "",
    unsupported_claims: Iterable[str] = (),
) -> OutcomeEvalRecord:
    _require_ready(readiness)
    g = grader or CodeOnlyGrader()
    scores: dict[str, EvalDimensionScore] = {
        name: g.grade(dim_id, name, normalized) for dim_id, name in OUTCOME_DIMENSIONS
    }
    record = OutcomeEvalRecord(
        outcome_eval_id=_gen_id("outcome"),
        normalized_record_refs=[r.normalized_record_id for r in normalized],
        completed_run_ref=completed_run_ref,
        task_completion_score=scores["task_completion"],
        answer_correctness_score=scores["answer_correctness"],
        groundedness_score=scores["groundedness"],
        citation_support_score=scores["citation_support"],
        source_coverage_score=scores["source_coverage"],
        evidence_sufficiency_score=scores["evidence_sufficiency"],
        abstain_correctness_score=scores["abstain_correctness"],
        refusal_correctness_score=scores["refusal_correctness"],
        format_schema_fit_score=scores["format_schema_fit"],
        user_constraint_adherence_score=scores["user_constraint_adherence"],
        scope_discipline_score=scores["scope_discipline"],
        usefulness_score=scores["usefulness"],
        artifact_validity_score=scores["artifact_validity"],
        unsupported_claims=list(unsupported_claims),
        uncertainty_markers=[f"{name}=UNKNOWN" for name, sc in scores.items() if sc.result == "UNKNOWN"],
        result_summary=_summarize(scores),
    )
    return stamp_digest(record)


def _summarize(scores: dict[str, EvalDimensionScore]) -> str:
    counts = {r: 0 for r in EVAL_DIMENSION_RESULTS}
    for s in scores.values():
        counts[s.result] = counts.get(s.result, 0) + 1
    return ",".join(f"{k}={v}" for k, v in sorted(counts.items()))


# ---------------------------------------------------------------------------
# Trajectory eval
# ---------------------------------------------------------------------------

TRAJECTORY_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("dim.route_fit", "route_fit"),
    ("dim.tool_order", "tool_order"),
    ("dim.tool_choice", "tool_choice"),
    ("dim.model_lane_selection", "model_lane_selection"),
    ("dim.argument_correctness", "argument_correctness"),
    ("dim.retrieval_use", "retrieval_use"),
    ("dim.prompt_assembly_correctness", "prompt_assembly_correctness"),
    ("dim.fallback_depth", "fallback_depth"),
    ("dim.retry_thrash", "retry_thrash"),
    ("dim.loop_productivity", "loop_productivity"),
    ("dim.budget_behavior", "budget_behavior"),
    ("dim.latency_behavior", "latency_behavior"),
    ("dim.cost_behavior", "cost_behavior"),
    ("dim.hitl_trigger_fit", "hitl_trigger_fit"),
    ("dim.sandbox_scope_fit", "sandbox_scope_fit"),
    ("dim.write_request_legitimacy", "write_request_legitimacy"),
    ("dim.evidence_preservation", "evidence_preservation"),
)


def evaluate_trajectory(
    readiness: EvalReadinessReceipt,
    normalized: list[NormalizedEvidenceRecord],
    *,
    grader: DimensionGrader | None = None,
) -> TrajectoryEvalRecord:
    _require_ready(readiness)
    g = grader or CodeOnlyGrader()
    scores: dict[str, EvalDimensionScore] = {
        name: g.grade(dim_id, name, normalized) for dim_id, name in TRAJECTORY_DIMENSIONS
    }

    flags: list[str] = []
    if any(r.retry_count > 2 for r in normalized):
        flags.append("retry_thrash")
    if any(r.fallback_depth > 1 for r in normalized):
        flags.append("silent_fallback")
    if any(r.error_code for r in normalized):
        flags.append("execution_error")

    fault_candidates = [r.span_id for r in normalized if r.error_code or r.retry_count > 2]

    record = TrajectoryEvalRecord(
        trajectory_eval_id=_gen_id("trajectory"),
        normalized_record_refs=[r.normalized_record_id for r in normalized],
        route_fit_score=scores["route_fit"],
        tool_order_score=scores["tool_order"],
        tool_choice_score=scores["tool_choice"],
        model_lane_selection_score=scores["model_lane_selection"],
        argument_correctness_score=scores["argument_correctness"],
        retrieval_use_score=scores["retrieval_use"],
        prompt_assembly_correctness_score=scores["prompt_assembly_correctness"],
        fallback_depth_score=scores["fallback_depth"],
        retry_thrash_score=scores["retry_thrash"],
        loop_productivity_score=scores["loop_productivity"],
        budget_behavior_score=scores["budget_behavior"],
        latency_behavior_score=scores["latency_behavior"],
        cost_behavior_score=scores["cost_behavior"],
        hitl_trigger_fit_score=scores["hitl_trigger_fit"],
        sandbox_scope_fit_score=scores["sandbox_scope_fit"],
        write_request_legitimacy_score=scores["write_request_legitimacy"],
        evidence_preservation_score=scores["evidence_preservation"],
        span_fault_candidates=fault_candidates,
        trajectory_flags=flags,
    )
    return stamp_digest(record)


# ---------------------------------------------------------------------------
# Governance regression eval
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GovernanceBaseline:
    policy_hash: str | None
    rubric_hash: str | None
    replay_digest: str | None
    schema_version: str | None = None


def evaluate_governance_regression(
    readiness: EvalReadinessReceipt,
    normalized: list[NormalizedEvidenceRecord],
    baseline: GovernanceBaseline,
    *,
    severity: str = "low",
) -> GovernanceRegressionRecord:
    _require_ready(readiness)

    policy_drift: list[str] = []
    schema_drift: list[str] = []
    replay_drift: list[str] = []
    refusal_drift: list[str] = []
    impacted: set[str] = set()

    for rec in normalized:
        if baseline.policy_hash and rec.policy_hash and rec.policy_hash != baseline.policy_hash:
            policy_drift.append(rec.normalized_record_id)
            impacted.add("policy")
        if baseline.replay_digest and rec.replay_key and rec.replay_key != baseline.replay_digest:
            replay_drift.append(rec.normalized_record_id)
            impacted.add("replay")
        if rec.canonical_event_type == "refusal" and rec.error_code:
            refusal_drift.append(rec.normalized_record_id)
            impacted.add("refusal")

    high = bool(policy_drift) or bool(replay_drift)
    severity_class = "high" if high else severity

    required_review = "L5_GOVERNANCE_REVIEW" if high else "NONE"
    record = GovernanceRegressionRecord(
        governance_regression_id=_gen_id("gov"),
        policy_drift_flags=policy_drift,
        schema_api_drift_flags=schema_drift,
        replay_digest_drift_flags=replay_drift,
        refusal_abstain_drift_flags=refusal_drift,
        impacted_surfaces=sorted(impacted),
        severity=severity_class,
        suspected_cause="DRIFT" if high else "NONE",
        required_review=required_review,
        policy_hash=baseline.policy_hash,
        rubric_hash=baseline.rubric_hash,
        replay_digest=baseline.replay_digest,
    )
    return stamp_digest(record)


__all__ = [
    "EvaluationError",
    "DimensionGrader",
    "CodeOnlyGrader",
    "HybridGrader",
    "OUTCOME_DIMENSIONS",
    "TRAJECTORY_DIMENSIONS",
    "GovernanceBaseline",
    "evaluate_outcome",
    "evaluate_trajectory",
    "evaluate_governance_regression",
]
