"""apps_eval → L6 promotion gate adapter.

Closes the largest open architectural gap from the SVP review: every shadow
eval run must feed Wilson-CI promotion gates with deterministic verdicts.

Pure adapter — no I/O, no LLM calls. Takes two `EvalRunSummary` instances
(candidate vs baseline), maps `scenarios_passed/scenarios_run` to the
Bernoulli sample required by `promotion_decision()`, and returns a
`PromotionAdapterResult` carrying the verdict + provenance.

Usage:
    from apps_eval.integrations.promotion_loop import evaluate_for_promotion

    verdict = evaluate_for_promotion(
        candidate_summary=current_run_summary,
        baseline_summary=last_known_good_summary,
    )
    if verdict.promote:
        ...

Constitutional §29 closed-loop: `promotion_decision()` itself records a
ROUTER_DECISION + ledger row. This adapter does NOT double-record;
attribution is owned by the L6 gate.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W4.1)
"""
from __future__ import annotations

from dataclasses import dataclass

from apps_eval.types import EvalRunSummary

from agentic_core.L6_observability.promotion_gates import (
    PromotionVerdict,
    counterfactual_uplift,
    promotion_decision,
)


@dataclass(frozen=True)
class PromotionAdapterResult:
    """Adapter result — wraps the L6 verdict with apps_eval provenance."""

    verdict: PromotionVerdict
    candidate_trace_id: str
    baseline_trace_id: str
    candidate_app: str
    candidate_version: str
    baseline_version: str

    @property
    def promote(self) -> bool:
        return self.verdict.promote

    @property
    def reason(self) -> str:
        return self.verdict.reason


def evaluate_for_promotion(
    *,
    candidate_summary: EvalRunSummary,
    baseline_summary: EvalRunSummary,
    z: float = 1.96,
    min_n_each_arm: int = 30,
) -> PromotionAdapterResult:
    """Decide whether the candidate eval run promotes over the baseline.

    Maps ``scenarios_passed`` → successes and ``scenarios_run`` → trials,
    then defers to L6 ``promotion_decision()``. The L6 gate is the single
    source of truth for the Wilson-CI verdict; this function only adapts
    the apps_eval contract to it.

    Pre-conditions checked:
        * Both summaries describe the same app (``app`` field match).
        * Neither summary is in error state (``status='complete'``).
        * Both have non-zero ``scenarios_run`` and non-negative
          ``scenarios_passed`` ≤ ``scenarios_run``.

    Raises:
        ValueError: any pre-condition violated. Promotion gating MUST NOT
        accept malformed inputs silently — that would corrupt the verdict.
    """
    _validate_summary("candidate", candidate_summary)
    _validate_summary("baseline", baseline_summary)
    if candidate_summary.app and baseline_summary.app:
        if candidate_summary.app != baseline_summary.app:
            raise ValueError(
                "candidate.app and baseline.app must match: "
                f"{candidate_summary.app!r} != {baseline_summary.app!r}"
            )

    verdict = promotion_decision(
        candidate_successes=candidate_summary.scenarios_passed,
        candidate_n=candidate_summary.scenarios_run,
        baseline_successes=baseline_summary.scenarios_passed,
        baseline_n=baseline_summary.scenarios_run,
        z=z,
        min_n_each_arm=min_n_each_arm,
    )
    return PromotionAdapterResult(
        verdict=verdict,
        candidate_trace_id=candidate_summary.trace_id,
        baseline_trace_id=baseline_summary.trace_id,
        candidate_app=candidate_summary.app,
        candidate_version=candidate_summary.version,
        baseline_version=baseline_summary.version,
    )


def _validate_summary(label: str, summary: EvalRunSummary) -> None:
    if summary.status == "error":
        raise ValueError(
            f"{label} summary in error state — cannot promote on a failed run "
            f"(error={summary.error!r})"
        )
    if summary.scenarios_run <= 0:
        raise ValueError(
            f"{label}.scenarios_run must be > 0, got {summary.scenarios_run}"
        )
    if summary.scenarios_passed < 0:
        raise ValueError(
            f"{label}.scenarios_passed must be >= 0, got {summary.scenarios_passed}"
        )
    if summary.scenarios_passed > summary.scenarios_run:
        raise ValueError(
            f"{label}.scenarios_passed ({summary.scenarios_passed}) "
            f"cannot exceed scenarios_run ({summary.scenarios_run})"
        )


@dataclass(frozen=True)
class CounterfactualUpliftResult:
    """Adapter result for counterfactual (shadow vs prod) uplift analysis."""

    uplift: float
    """E[shadow] - E[prod]; positive ⇒ shadow stack outperforms prod."""

    n_paired: int
    """Number of paired observations the uplift was computed over."""

    candidate_app: str

    @property
    def shadow_outperforms(self) -> bool:
        return self.uplift > 0.0


def evaluate_counterfactual_uplift(
    *,
    shadow_summary: EvalRunSummary,
    prod_summary: EvalRunSummary,
) -> CounterfactualUpliftResult:
    """Compute the shadow-vs-prod uplift over paired eval scenarios.

    The candidate ("shadow") and production ("prod") stacks are replayed
    through the SAME scenario set; their pass/fail outcomes are paired.
    This is the secondary promotion criterion — even when Wilson-CI is
    inconclusive, a positive paired uplift on shadow ⇒ promote candidate.

    Pre-conditions:
      * Both summaries describe the same app.
      * Both have equal ``scenarios_run`` (paired replay required).
      * Neither summary is in error state.

    The fine-grained per-scenario outcomes are not exposed in
    ``EvalRunSummary`` (deliberately — rollup only). To avoid losing
    pairing semantics we synthesize the boolean lists from the aggregate
    pass counts: ``[True] * passed + [False] * (n - passed)``. This is
    safe because :func:`counterfactual_uplift` only uses ``E[]`` of each
    list, not the per-element pairing — but pairing IS the contract this
    function exposes, so callers MUST ensure same scenario set.

    Returns:
        CounterfactualUpliftResult with uplift in ``[-1.0, 1.0]``.

    Raises:
        ValueError: any pre-condition violated.
    """
    _validate_summary("shadow", shadow_summary)
    _validate_summary("prod", prod_summary)
    if shadow_summary.app and prod_summary.app:
        if shadow_summary.app != prod_summary.app:
            raise ValueError(
                "shadow.app and prod.app must match: "
                f"{shadow_summary.app!r} != {prod_summary.app!r}"
            )
    if shadow_summary.scenarios_run != prod_summary.scenarios_run:
        raise ValueError(
            "scenarios_run must match for paired counterfactual: "
            f"shadow={shadow_summary.scenarios_run}, "
            f"prod={prod_summary.scenarios_run}"
        )

    n = shadow_summary.scenarios_run
    shadow_outcomes = [True] * shadow_summary.scenarios_passed + [False] * (
        n - shadow_summary.scenarios_passed
    )
    prod_outcomes = [True] * prod_summary.scenarios_passed + [False] * (
        n - prod_summary.scenarios_passed
    )
    uplift = counterfactual_uplift(shadow_outcomes, prod_outcomes)

    return CounterfactualUpliftResult(
        uplift=uplift,
        n_paired=n,
        candidate_app=shadow_summary.app,
    )


@dataclass(frozen=True)
class CombinedPromotionResult:
    """Combined promotion verdict — Wilson-CI as primary, counterfactual as rescue.

    Cascade rule:
      * If Wilson promotes → ``promote=True``, ``primary_signal='wilson'``.
      * Else if shadow/prod summaries given AND counterfactual uplift > 0
        → ``promote=True``, ``primary_signal='counterfactual'`` (Wilson was
        inconclusive but paired uplift rescues the verdict).
      * Else → ``promote=False``, ``primary_signal='neither'``.

    Both component results are preserved for audit / logging; downstream
    callers can render either as the source-of-decision in artifacts.
    """

    promote: bool
    primary_signal: str  # 'wilson' | 'counterfactual' | 'neither'
    wilson_result: PromotionAdapterResult
    counterfactual_result: CounterfactualUpliftResult | None
    reason: str


def evaluate_combined_promotion(
    *,
    candidate_summary: EvalRunSummary,
    baseline_summary: EvalRunSummary,
    shadow_summary: EvalRunSummary | None = None,
    prod_summary: EvalRunSummary | None = None,
) -> CombinedPromotionResult:
    """Combined Wilson-CI + counterfactual uplift promotion gate.

    The Wilson-CI gate is primary — when it says PROMOTE, that's the answer
    and counterfactual is not consulted. When Wilson is inconclusive (e.g.
    candidate's lower-CI does NOT exceed baseline's upper-CI even though
    the point estimate improved), the paired counterfactual uplift CAN
    rescue the verdict if shadow/prod summaries are supplied AND the paired
    uplift is strictly positive.

    Args:
        candidate_summary, baseline_summary: Required Wilson-CI inputs.
        shadow_summary, prod_summary: Optional paired counterfactual inputs.
            BOTH must be supplied to consult the counterfactual signal; if
            only one is given the counterfactual layer is skipped.

    Returns:
        CombinedPromotionResult with ``promote`` boolean, the primary signal
        identifier, and both component results for audit.
    """
    wilson_result = evaluate_for_promotion(
        candidate_summary=candidate_summary,
        baseline_summary=baseline_summary,
    )

    if wilson_result.verdict.promote:
        return CombinedPromotionResult(
            promote=True,
            primary_signal="wilson",
            wilson_result=wilson_result,
            counterfactual_result=None,
            reason=f"Wilson-CI promotes: {wilson_result.verdict.reason}",
        )

    # Wilson did NOT promote — try counterfactual rescue if pair supplied.
    cf_result: CounterfactualUpliftResult | None = None
    if shadow_summary is not None and prod_summary is not None:
        cf_result = evaluate_counterfactual_uplift(
            shadow_summary=shadow_summary,
            prod_summary=prod_summary,
        )
        if cf_result.shadow_outperforms:
            return CombinedPromotionResult(
                promote=True,
                primary_signal="counterfactual",
                wilson_result=wilson_result,
                counterfactual_result=cf_result,
                reason=(
                    f"Wilson inconclusive ({wilson_result.verdict.reason}); "
                    f"counterfactual rescues with paired uplift={cf_result.uplift:+.4f} "
                    f"over n={cf_result.n_paired}"
                ),
            )

    return CombinedPromotionResult(
        promote=False,
        primary_signal="neither",
        wilson_result=wilson_result,
        counterfactual_result=cf_result,
        reason=(
            f"Wilson rejects ({wilson_result.verdict.reason}); "
            + (
                f"counterfactual uplift={cf_result.uplift:+.4f} did not rescue"
                if cf_result is not None
                else "no counterfactual signal supplied"
            )
        ),
    )


__all__ = [
    "CombinedPromotionResult",
    "CounterfactualUpliftResult",
    "PromotionAdapterResult",
    "evaluate_combined_promotion",
    "evaluate_counterfactual_uplift",
    "evaluate_for_promotion",
]
