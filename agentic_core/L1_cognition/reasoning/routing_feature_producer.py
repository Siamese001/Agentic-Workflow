"""L1 producer hook for :class:`RoutingFeatureVector` — W5.P2 deposit.

Plan: ``docs/archive/windsurf/legacy-tree/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` §W5.P2.

A thin composition layer that L1 planners (or a shim over older planners
that don't yet emit the feature vector) can call to turn a request +
optional signals into a :class:`~agentic_core.runtime.contracts.routing_features.RoutingFeatureVector`
consumable by the L0 router.

Entry point :func:`build_routing_feature_vector`:

    - Takes the raw user query text + optional planner-supplied hints.
    - Uses :func:`classify_grounding_need` (W1.P2 heuristic classifier) to
      produce ``grounding_need_score`` when not provided explicitly.
    - Infers ``work_class`` from the query via :func:`classify_work_class`
      when not provided.
    - Passes through ``ood_score`` / ``budget_headroom_ratio`` /
      ``freshness_class`` verbatim when provided, using
      :data:`NO_SIGNAL` / sensible defaults when absent.

Back-compat: this module is **additive and optional**. No existing L1
planner is required to call it. New planners and shims import it to
emit a feature vector without each site having to assemble the scoring
plumbing itself.
"""

from __future__ import annotations

from agentic_core.L1_cognition.reasoning.ml_decision_support.features.grounding_need_features import (
    classify_grounding_need,
    classify_work_class,
)
from agentic_core.runtime.contracts.routing_features import (
    NO_SIGNAL,
    FreshnessClass,
    RoutingFeatureVector,
    WorkClass,
    build_feature_vector,
)


def build_routing_feature_vector(
    query: str,
    *,
    work_class: WorkClass | str | None = None,
    freshness_class: FreshnessClass = "bounded",
    grounding_need_score: float | None = None,
    ood_score: float = NO_SIGNAL,
    budget_headroom_ratio: float = NO_SIGNAL,
    metadata: dict | None = None,
) -> RoutingFeatureVector:
    """Produce a :class:`RoutingFeatureVector` for ``query``.

    Args:
        query: Raw user query text. Empty strings are allowed and produce
            a low grounding-need score via the heuristic classifier.
        work_class: Explicit L1 ``WorkClass`` (or its string value) when
            the caller has already classified the intent. ``None`` (default)
            invokes :func:`classify_work_class` on ``query``.
        freshness_class: Freshness SLA required by the L1 plan. Defaults
            to ``"bounded"``.
        grounding_need_score: Override the heuristic classifier's output.
            ``None`` (default) invokes :func:`classify_grounding_need`.
            Pass :data:`NO_SIGNAL` to explicitly mark "caller could not
            compute"; downstream gates will treat this as "no signal".
        ood_score: Optional OOD / novelty signal.
        budget_headroom_ratio: Optional remaining-budget signal.
        metadata: Optional free-form dict threaded through the vector.

    Returns:
        A populated :class:`RoutingFeatureVector`.
    """
    if query is None:
        raise ValueError("query must not be None — pass an empty string instead")

    # Normalize the caller's work_class hint into a WorkClass enum.
    resolved_work_class: WorkClass
    if work_class is None:
        resolved_work_class = classify_work_class(query)
    elif isinstance(work_class, WorkClass):
        resolved_work_class = work_class
    else:
        resolved_work_class = WorkClass(work_class)

    # Compute or accept the grounding-need score.
    resolved_ground_score: float
    if grounding_need_score is None:
        classification = classify_grounding_need(query, work_class=resolved_work_class)
        resolved_ground_score = classification.score
    else:
        resolved_ground_score = float(grounding_need_score)

    return build_feature_vector(
        work_class=resolved_work_class,
        freshness_class=freshness_class,
        grounding_need_score=resolved_ground_score,
        ood_score=ood_score,
        budget_headroom_ratio=budget_headroom_ratio,
        metadata=metadata or {},
    )


__all__ = ["build_routing_feature_vector"]
