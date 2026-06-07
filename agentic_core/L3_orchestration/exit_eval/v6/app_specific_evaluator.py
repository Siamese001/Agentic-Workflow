"""App-specific Exit evaluator (W5 runtime consumption).

Consumes the app-contract refs carried by :class:`ExitReviewPacket` (populated
at L0 by ``agentic_core.L0_routing.app_domain_resolver``) and evaluates the
run against the resolved :class:`AppEvalRubricRecord` +
:class:`AppThresholdProfileRecord` + :class:`AppGraderRosterRecord` from L4.

Key invariants:

- UNKNOWN on any ``fail_closed_if_unknown`` dimension ⇒ FAIL (no pass)
- Every dimension's ``min_required_score`` MUST be met in addition to
  ``overall_pass_threshold``
- Missing rubric / threshold / grader_roster in L4 ⇒ fail-closed
- Generic V6 fall-through preserved for non-app-bound runs (returns a
  :class:`AppSpecificEvalResult` with ``bound=False`` and no scoring)

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-domain-contract-fortknox-c4d8e2.md`` §W5.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, Mapping, Optional

from agentic_core.L4_state.contracts.app_domain import (
    AppEvalRubricRecord,
    AppThresholdProfileRecord,
    ScoreDimension,
)
from agentic_core.L4_state.contracts.app_domain_lookup import (
    InMemoryAppDomainStore,
    UnknownAppContractError,
    get_default_app_domain_store,
)

Logger = logging.getLogger(__name__)


# Grader returns one of these for each dimension. UNKNOWN is a real
# value (caller said "I could not compute"); it's distinct from "low score".
GRADER_UNKNOWN_SENTINEL = -1.0


@dataclass(slots=True)
class DimensionResult:
    """Per-dimension eval outcome."""

    dimension_id: str
    score: float             # [0, 1] or GRADER_UNKNOWN_SENTINEL
    weight: float
    grader_type: str
    status: str              # PASS | FAIL | UNKNOWN
    reason: str = ""
    min_required_score: float = -1.0
    evidence_refs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AppSpecificEvalResult:
    """Final app-specific eval verdict."""

    bound: bool                          # False if route had no app-contract ref
    app_id: str = ""
    task_class: str = ""
    rubric_ref: str = ""
    threshold_profile_ref: str = ""
    overall_score: float = 0.0
    overall_pass_threshold: float = 0.0
    passed: bool = False
    fail_reasons: list[str] = field(default_factory=list)
    dimensions: list[DimensionResult] = field(default_factory=list)
    # W2.P5 — HITL policy carried from the resolved threshold profile so X2
    # can route to ESCALATE vs DENY without a store lookup.
    # Values: "none" | "required_on_low" | "required_always".
    hitl_policy: str = "none"

    def to_packet_dict(self) -> Dict[str, object]:
        """Serialize for ExitReviewPacket.app_specific_eval."""
        return {
            "bound": self.bound,
            "app_id": self.app_id,
            "task_class": self.task_class,
            "rubric_ref": self.rubric_ref,
            "threshold_profile_ref": self.threshold_profile_ref,
            "overall_score": self.overall_score,
            "overall_pass_threshold": self.overall_pass_threshold,
            "passed": self.passed,
            "fail_reasons": list(self.fail_reasons),
            "hitl_policy": self.hitl_policy,
            "dimensions": [
                {
                    "dimension_id": d.dimension_id,
                    "score": d.score,
                    "weight": d.weight,
                    "grader_type": d.grader_type,
                    "status": d.status,
                    "reason": d.reason,
                    "min_required_score": d.min_required_score,
                    "evidence_refs": list(d.evidence_refs),
                }
                for d in self.dimensions
            ],
        }


# A "grader callable" returns (score, evidence_refs). Score can be
# GRADER_UNKNOWN_SENTINEL to signal UNKNOWN. evidence_refs is a list of
# opaque evidence ids (source_ids, profile_ids, etc.) that back the score.
GraderFn = Callable[[ScoreDimension, Mapping[str, object]], "tuple[float, list[str]]"]


def _default_grader_not_implemented(
    dim: ScoreDimension,
    _run_context: Mapping[str, object],
) -> "tuple[float, list[str]]":
    """Default grader — returns UNKNOWN. Real grader implementations are
    registered by downstream code per dimension_id."""
    return GRADER_UNKNOWN_SENTINEL, []


class AppSpecificEvaluator:
    """Evaluates a run against a resolved app-domain rubric + threshold.

    Graders are pluggable: callers register per-dimension_id grader
    functions. When no grader is registered for a dimension, the default
    returns UNKNOWN. Dimensions flagged ``fail_closed_if_unknown`` then
    cause the whole evaluation to FAIL, which is the intended posture
    for hard guardrails (``no_fabrication``, ``no_sensitive_targeting``, etc.).
    """

    def __init__(
        self,
        *,
        store: Optional[InMemoryAppDomainStore] = None,
        graders: Optional[Dict[str, GraderFn]] = None,
        default_grader: Optional[GraderFn] = None,
    ) -> None:
        self._store = store or get_default_app_domain_store()
        self._graders: Dict[str, GraderFn] = dict(graders or {})
        # W1.P2: optional fallback grader used when no per-dim grader is registered.
        # Preserves existing fail-closed-on-UNKNOWN posture when default_grader is None.
        self._default_grader: GraderFn = default_grader or _default_grader_not_implemented

    def register_grader(self, dimension_id: str, fn: GraderFn) -> None:
        """Install a grader for ``dimension_id``. Overwrites any prior grader."""
        self._graders[dimension_id] = fn

    def register_graders(self, graders: Mapping[str, GraderFn]) -> None:
        """Bulk-register multiple graders."""
        for dim_id, fn in graders.items():
            self._graders[dim_id] = fn

    def evaluate(
        self,
        *,
        app_id: str,
        task_class: str,
        rubric_ref: str,
        threshold_profile_ref: str,
        run_context: Mapping[str, object],
    ) -> AppSpecificEvalResult:
        """Run the full app-specific evaluation. Fail-closed on any error.

        Returns an :class:`AppSpecificEvalResult`. When ``bound=False``,
        the caller should fall through to generic V6 evaluation.
        """
        # If either ref is missing, the route wasn't bound. Return unbound.
        if not rubric_ref or not threshold_profile_ref:
            return AppSpecificEvalResult(bound=False)

        try:
            rubric = self._store.get_eval_rubric(rubric_ref)
            threshold = self._store.get_threshold_profile(threshold_profile_ref)
        except UnknownAppContractError as exc:
            Logger.warning(
                "app_specific_evaluator: unknown rubric_ref=%s threshold_ref=%s: %s",
                rubric_ref, threshold_profile_ref, exc,
            )
            return AppSpecificEvalResult(
                bound=True,
                app_id=app_id,
                task_class=task_class,
                rubric_ref=rubric_ref,
                threshold_profile_ref=threshold_profile_ref,
                passed=False,
                fail_reasons=[f"unknown_app_contract::{exc}"],
            )

        return self._score_against_rubric(
            app_id=app_id,
            task_class=task_class,
            rubric=rubric,
            threshold=threshold,
            run_context=run_context,
        )

    def _score_against_rubric(
        self,
        *,
        app_id: str,
        task_class: str,
        rubric: AppEvalRubricRecord,
        threshold: AppThresholdProfileRecord,
        run_context: Mapping[str, object],
    ) -> AppSpecificEvalResult:
        dim_results: list[DimensionResult] = []
        fail_reasons: list[str] = []
        weighted_score = 0.0
        total_weight = 0.0
        # progress: bounded by len(rubric.score_dimensions) — typically 6-10 per app, no UI bar needed
        for dim in rubric.score_dimensions:
            grader = self._graders.get(dim.dimension_id, self._default_grader)
            try:
                raw_score, evidence = grader(dim, run_context)
            except (ValueError, TypeError, RuntimeError) as exc:
                # guardian: allow-log-and-swallow -- grader failure is treated as UNKNOWN per
                # fail-closed posture; we never let a buggy grader crash the eval pipeline.
                Logger.warning(
                    "app_specific_evaluator: grader for %s raised %s: %s",
                    dim.dimension_id, type(exc).__name__, exc,
                )
                raw_score, evidence = GRADER_UNKNOWN_SENTINEL, []
            # W4.P2 — retry-on-low for llm_as_judge graders. When the first
            # score is suspiciously low (< min_required_score) AND the grader
            # type is llm_as_judge AND run_context carries a retry hint, run
            # the grader exactly once more. This is Anthropic's "re-run
            # the judge on low scores to guard against transient LLM noise".
            # Budget: 1 retry per dim per run max. Idempotent: the grader
            # must return deterministically for the same run_context; only
            # llm_as_judge graders are allowed to vary and thus retried.
            if (
                dim.grader_type == "llm_as_judge"
                and raw_score != GRADER_UNKNOWN_SENTINEL
                and dim.min_required_score > 0
                and raw_score < dim.min_required_score
                and bool(run_context.get("judge_retry_on_low", False))
            ):
                try:
                    retry_score, retry_evidence = grader(dim, run_context)
                    # Accept higher of the two — retry only REDUCES false-low;
                    # it doesn't rescue genuine fails.
                    if retry_score != GRADER_UNKNOWN_SENTINEL and retry_score > raw_score:
                        raw_score = retry_score
                        evidence = list(evidence) + [f"retry_on_low={retry_score:.3f}"] + list(retry_evidence or [])
                except (ValueError, TypeError, RuntimeError) as retry_exc:  # guardian: allow-log-and-swallow -- P1 ADG burndown
                    # guardian: allow-log-and-swallow -- retry is best-effort;
                    # failure preserves original score (fail-closed posture intact)
                    Logger.info(
                        "app_specific_evaluator: retry for %s raised %s",
                        dim.dimension_id, type(retry_exc).__name__,
                    )

            result = self._classify_dimension(dim, raw_score, evidence)
            dim_results.append(result)
            if result.status == "FAIL":
                fail_reasons.append(
                    f"dimension_fail::{dim.dimension_id}::{result.reason}",
                )
            if raw_score != GRADER_UNKNOWN_SENTINEL:
                weighted_score += raw_score * dim.weight
                total_weight += dim.weight

        overall_score = (weighted_score / total_weight) if total_weight > 0 else 0.0

        # Enforce per-dimension minimums from the threshold profile
        # (in addition to the rubric's per-dimension min_required_score).
        for dim_id, dim_min in threshold.dimension_minimums.items():
            matching = next(
                (r for r in dim_results if r.dimension_id == dim_id), None,
            )
            if matching is None:
                continue  # dim not in rubric (threshold can reference subset)
            # UNKNOWN handled above; here we only check numeric below-min
            if matching.score != GRADER_UNKNOWN_SENTINEL and matching.score < dim_min:
                fail_reasons.append(
                    f"threshold_min::{dim_id}::score={matching.score:.3f}<min={dim_min:.3f}",
                )
                # Flip the dim's status to FAIL if it was PASS
                matching.status = "FAIL"
                matching.reason = (
                    f"below_threshold_min({dim_min:.3f})"
                )

        passed = (
            not fail_reasons
            and overall_score >= threshold.overall_pass_threshold
        )
        if not passed and not fail_reasons:
            # Must have failed on overall_pass_threshold
            fail_reasons.append(
                f"overall_below_threshold::score={overall_score:.3f}"
                f"<threshold={threshold.overall_pass_threshold:.3f}",
            )

        return AppSpecificEvalResult(
            bound=True,
            app_id=app_id,
            task_class=task_class,
            rubric_ref=rubric.eval_rubric_id,
            threshold_profile_ref=threshold.threshold_profile_id,
            overall_score=overall_score,
            overall_pass_threshold=threshold.overall_pass_threshold,
            passed=passed,
            fail_reasons=fail_reasons,
            dimensions=dim_results,
            hitl_policy=threshold.hitl_policy,
        )

    def _classify_dimension(
        self,
        dim: ScoreDimension,
        raw_score: float,
        evidence: list[str],
    ) -> DimensionResult:
        """Decide PASS / FAIL / UNKNOWN for a single dimension."""
        if raw_score == GRADER_UNKNOWN_SENTINEL:
            if dim.fail_closed_if_unknown:
                return DimensionResult(
                    dimension_id=dim.dimension_id,
                    score=GRADER_UNKNOWN_SENTINEL,
                    weight=dim.weight,
                    grader_type=dim.grader_type,
                    status="FAIL",
                    reason="unknown_fail_closed",
                    min_required_score=dim.min_required_score,
                    evidence_refs=list(evidence),
                )
            return DimensionResult(
                dimension_id=dim.dimension_id,
                score=GRADER_UNKNOWN_SENTINEL,
                weight=dim.weight,
                grader_type=dim.grader_type,
                status="UNKNOWN",
                reason="unknown_not_fail_closed",
                min_required_score=dim.min_required_score,
                evidence_refs=list(evidence),
            )
        if not 0.0 <= raw_score <= 1.0:
            return DimensionResult(
                dimension_id=dim.dimension_id,
                score=raw_score,
                weight=dim.weight,
                grader_type=dim.grader_type,
                status="FAIL",
                reason=f"score_out_of_range::{raw_score}",
                min_required_score=dim.min_required_score,
                evidence_refs=list(evidence),
            )
        if dim.evidence_required and not evidence:
            return DimensionResult(
                dimension_id=dim.dimension_id,
                score=raw_score,
                weight=dim.weight,
                grader_type=dim.grader_type,
                status="FAIL",
                reason="evidence_required_but_empty",
                min_required_score=dim.min_required_score,
                evidence_refs=[],
            )
        if dim.min_required_score >= 0.0 and raw_score < dim.min_required_score:
            return DimensionResult(
                dimension_id=dim.dimension_id,
                score=raw_score,
                weight=dim.weight,
                grader_type=dim.grader_type,
                status="FAIL",
                reason=f"below_rubric_min({dim.min_required_score:.3f})",
                min_required_score=dim.min_required_score,
                evidence_refs=list(evidence),
            )
        return DimensionResult(
            dimension_id=dim.dimension_id,
            score=raw_score,
            weight=dim.weight,
            grader_type=dim.grader_type,
            status="PASS",
            reason="",
            min_required_score=dim.min_required_score,
            evidence_refs=list(evidence),
        )


def evaluate_from_packet(
    *,
    evaluator: AppSpecificEvaluator,
    app_id: str,
    task_class: str,
    rubric_ref: str,
    threshold_profile_ref: str,
    run_context: Mapping[str, object],
) -> AppSpecificEvalResult:
    """Convenience entry-point used by the Exit pipeline.

    Accepts the refs already extracted from :class:`ExitReviewPacket` and
    runs the evaluation. Keeping the packet unpacking out of the
    evaluator keeps the evaluator pure.
    """
    return evaluator.evaluate(
        app_id=app_id,
        task_class=task_class,
        rubric_ref=rubric_ref,
        threshold_profile_ref=threshold_profile_ref,
        run_context=run_context,
    )


__all__ = [
    "GRADER_UNKNOWN_SENTINEL",
    "GraderFn",
    "DimensionResult",
    "AppSpecificEvalResult",
    "AppSpecificEvaluator",
    "evaluate_from_packet",
]
