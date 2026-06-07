"""F14 / WC-G06 LOW_NORMATIVE_COVERAGE consumer.

Production consumer that reads the ``LOW_NORMATIVE_COVERAGE`` signal emitted
by ``agentic_core.L3_orchestration.reasoning.engines.evidence_shaper`` and
routes low-coverage outcomes through the Wave D3 abstain primitive into the
Wave D4 R5-compatible action shape.

Wave D scope: implements WC-G06 / F14 per ``docs/archive/windsurf/legacy-tree/plans/wave_d_plan.md``
§3 Slice D5.1.

Design notes (D5.1):
- ``evidence_shaper.py`` is FROZEN in Wave D (see `wave_d_plan.md` §2d). This
  module imports the ``LOW_NORMATIVE_COVERAGE`` constant only; it does not
  call, wrap, or subclass any shaper function, and does not mutate any shaper
  state.
- Threshold logic is NOT re-implemented here. The consumer delegates to
  :func:`agentic_core.L1_cognition.reasoning.abstain_planner.plan_abstain`,
  which is the single source of truth for confidence-vs-floor gating (see
  Wave D §3 Slice D3).
- The output shape is a :class:`CoverageConsumerResult` ``TypedDict`` whose
  ``action`` field is compatible with both D3 (``"emit_r5_candidate"`` /
  ``"continue"``) and D4 (``route`` / ``action`` pairing on
  :class:`agentic_core.L0_routing.reasoning.path_router.RoutingResult`). The
  ``route_hint`` field surfaces the corresponding D4 route label (``"R5"``
  or ``"continue"``) so D5.2 integration can dispatch without re-deriving it.
- Pure synchronous function. No LLM, no cache, no spine, no async. All
  outputs are primitive types so the result is trivially
  ``json.dumps``-serializable for telemetry and cross-process hand-off.
"""

from __future__ import annotations

from typing import Iterable, Literal, TypedDict, cast

from agentic_core.L0_routing.reasoning.path_router import R5_ROUTE
from agentic_core.L1_cognition.reasoning.abstain_planner import (
    DECISION_ABSTAIN,
    DEFAULT_ABSTAIN_THRESHOLD,
    plan_abstain,
)
from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
    LOW_NORMATIVE_COVERAGE,
)

SIGNAL_NORMAL: Literal["NORMAL"] = "NORMAL"
"""Sentinel emitted in :class:`CoverageConsumerResult` when the input signals
do not include :data:`LOW_NORMATIVE_COVERAGE`. Treated as a closed enum value
alongside :data:`LOW_NORMATIVE_COVERAGE`.
"""

ROUTE_HINT_CONTINUE: Literal["continue"] = "continue"
"""Route hint emitted when :func:`plan_abstain` returns ``decision="proceed"``.
Pairs with D3 ``action="continue"`` and signals D5.2 to let the caller fall
through to the regular L0 A/B/C/D path selection.
"""


class CoverageConsumerResult(TypedDict):
    """Serializable shape emitted by :func:`consume_coverage_signal`.

    Stable public contract consumed by Wave D5.2 integration. Every field is
    a primitive so the dict round-trips through ``json.dumps`` /
    ``json.loads`` without transformation.

    Fields:
        signal: Either ``"LOW_NORMATIVE_COVERAGE"`` (the
            :data:`LOW_NORMATIVE_COVERAGE` sentinel re-exported from
            ``evidence_shaper``) or ``"NORMAL"``.
        decision: ``"abstain"`` or ``"proceed"`` (verbatim from the D3
            :func:`plan_abstain` output).
        reason: Human-readable justification (verbatim from the D3 output).
        confidence: Input coverage / confidence value in ``[0.0, 1.0]``
            (verbatim from the D3 output).
        threshold: Abstain floor in ``[0.0, 1.0]`` (verbatim from the D3
            output).
        route_hint: ``"R5"`` on abstain, ``"continue"`` on proceed. This is
            the exact :data:`R5_ROUTE` constant from
            :mod:`agentic_core.L0_routing.reasoning.path_router` on the
            abstain branch so D5.2 can build a D4-compatible
            :class:`RoutingResult` without re-deriving the route label.
        action: ``"emit_r5_candidate"`` on abstain, ``"continue"`` on proceed
            (verbatim from the D3 output; identical to the D4
            :class:`RoutingResult.action` on both branches).
    """

    signal: Literal["LOW_NORMATIVE_COVERAGE", "NORMAL"]
    decision: Literal["abstain", "proceed"]
    reason: str
    confidence: float
    threshold: float
    route_hint: Literal["R5", "continue"]
    action: Literal["emit_r5_candidate", "continue"]


def consume_coverage_signal(
    *,
    coverage: float,
    signals: Iterable[str] = (),
    threshold: float = DEFAULT_ABSTAIN_THRESHOLD,
    reason_hint: str | None = None,
) -> CoverageConsumerResult:
    """Consume a shaper coverage signal and dispatch through D3 / D4.

    The consumer never re-implements threshold logic. It delegates the
    abstain-vs-proceed decision to :func:`plan_abstain` and then maps the
    resulting ``action`` to a D4-compatible ``route_hint``.

    Behavior:

    * If :data:`LOW_NORMATIVE_COVERAGE` is present in ``signals``: the
      output's ``signal`` field is set to :data:`LOW_NORMATIVE_COVERAGE`.
      The ``reason_hint`` (when not explicitly overridden by the caller)
      is built to name the signal, so downstream telemetry attributes the
      abstain / proceed decision to the shaper signal rather than to a bare
      confidence comparison.
    * ``coverage`` and ``threshold`` are forwarded unchanged to
      :func:`plan_abstain`. If ``plan_abstain`` raises :class:`ValueError`
      (out-of-range inputs), the exception propagates; the consumer does
      not swallow contract errors.
    * When the resulting D3 decision is ``"abstain"``: ``route_hint`` is
      :data:`R5_ROUTE` (``"R5"``) and ``action`` is
      ``"emit_r5_candidate"``. D5.2 can hand the result directly to the D4
      R5 branch.
    * Otherwise: ``route_hint`` is :data:`ROUTE_HINT_CONTINUE`
      (``"continue"``) and ``action`` is ``"continue"``. D5.2 should let
      the regular L0 A/B/C/D path selection proceed.

    Args:
        coverage: Caller-supplied coverage or confidence score in
            ``[0.0, 1.0]``. Higher values mean stronger normative grounding.
        signals: Iterable of shaper signal tags observed on the upstream
            evidence bundle. Only :data:`LOW_NORMATIVE_COVERAGE` is
            interpreted; unknown signals are preserved in the input but do
            not affect routing.
        threshold: Abstain floor in ``[0.0, 1.0]``. Defaults to
            :data:`DEFAULT_ABSTAIN_THRESHOLD`.
        reason_hint: Optional override for the ``reason`` field in the
            returned :class:`CoverageConsumerResult`. When omitted and the
            :data:`LOW_NORMATIVE_COVERAGE` signal is present, a deterministic
            default is used that names the signal.

    Returns:
        A :class:`CoverageConsumerResult` dict with all seven required
        fields.

    Raises:
        ValueError: Propagated from :func:`plan_abstain` when ``coverage``
            or ``threshold`` falls outside ``[0.0, 1.0]``.
    """
    signal_set = {str(s) for s in signals}
    if LOW_NORMATIVE_COVERAGE in signal_set:
        signal_tag: Literal["LOW_NORMATIVE_COVERAGE", "NORMAL"] = cast(
            Literal["LOW_NORMATIVE_COVERAGE"], LOW_NORMATIVE_COVERAGE
        )
    else:
        signal_tag = SIGNAL_NORMAL

    effective_hint = reason_hint
    if signal_tag == LOW_NORMATIVE_COVERAGE and reason_hint is None:
        effective_hint = (
            f"{LOW_NORMATIVE_COVERAGE}: coverage {coverage:.4f} "
            f"evaluated against abstain floor {threshold:.4f}"
        )

    decision = plan_abstain(coverage, threshold, reason_hint=effective_hint)

    if decision["decision"] == DECISION_ABSTAIN:
        route_hint: Literal["R5", "continue"] = cast(Literal["R5"], R5_ROUTE)
    else:
        route_hint = ROUTE_HINT_CONTINUE

    return CoverageConsumerResult(
        signal=signal_tag,
        decision=decision["decision"],
        reason=decision["reason"],
        confidence=decision["confidence"],
        threshold=decision["threshold"],
        route_hint=route_hint,
        action=decision["action"],
    )


__all__ = [
    "ROUTE_HINT_CONTINUE",
    "SIGNAL_NORMAL",
    "CoverageConsumerResult",
    "consume_coverage_signal",
]
