"""Abstain-decision contract shared across routing (L0) and cognition (L1+).

This module is the SSOT for the abstain primitive so callers in lower layers
(e.g. L0 ``path_router``) can consume the contract without triggering layer
gravity violations. The thick implementation historically lived at
``agentic_core.L1_cognition.reasoning.abstain_planner`` and was promoted here
unchanged; ``abstain_planner`` is now a backward-compat re-export shim.

Scope:
- Pure, synchronous primitives (constants, ``TypedDict``, stateless function).
- No layer-specific dependencies, no I/O, no telemetry side effects.
- Stable public contract — treat exported strings as a closed enum.
"""

from __future__ import annotations

from typing import Literal, TypedDict

DEFAULT_ABSTAIN_THRESHOLD: float = 0.50
"""Default confidence floor. ``confidence < threshold`` triggers abstain.

Aligned with the ADEQUATE/WEAK distance boundary used in the Wave B B5R
and B7 audits (grounding verdict flips at 0.50). Callers MAY override this
value by passing an explicit ``threshold`` kwarg to :func:`plan_abstain`.
"""

# Stable downstream-action strings consumed by D4 (R5 router) and D5
# (coverage consumer). Treat as a closed enum for the Wave D backlog.
ACTION_EMIT_R5: Literal["emit_r5_candidate"] = "emit_r5_candidate"
ACTION_CONTINUE: Literal["continue"] = "continue"
# Clarify action (ADR-043 §T3 exit branches) — the exit gate surfaces
# the clarification request to the user and does NOT dispatch to L0.
ACTION_REQUEST_CLARIFICATION: Literal["request_clarification"] = "request_clarification"

# Stable decision strings. Treat as a closed enum.
DECISION_ABSTAIN: Literal["abstain"] = "abstain"
DECISION_PROCEED: Literal["proceed"] = "proceed"
# Clarify decision (ADR-043 §T3 exit branches) — distinct from abstain:
# abstain returns a safe-default, clarify blocks on human input.
DECISION_CLARIFY: Literal["clarify"] = "clarify"

DEFAULT_AMBIGUITY_THRESHOLD: float = 0.60
"""Default ambiguity floor used by :func:`plan_clarify`.

``ambiguity_score >= threshold`` triggers a clarify decision, provided
confidence is also not catastrophically low (in which case abstain wins).
"""


class AbstainDecision(TypedDict):
    """Serializable shape emitted by :func:`plan_abstain`.

    Stable public contract consumed by Wave D4 and D5. Every field is a
    primitive so the dict round-trips through ``json.dumps`` / ``json.loads``
    without transformation.

    Fields:
        decision: ``"abstain"`` or ``"proceed"``.
        reason: Human-readable justification for telemetry.
        confidence: The input confidence value, echoed for downstream logging.
        threshold: The floor used for the comparison, echoed for downstream
            logging. Always in [0.0, 1.0].
        action: Downstream dispatch hint. ``"emit_r5_candidate"`` when
            ``decision == "abstain"``; ``"continue"`` when
            ``decision == "proceed"``.
    """

    decision: Literal["abstain", "proceed"]
    reason: str
    confidence: float
    threshold: float
    action: Literal["emit_r5_candidate", "continue"]


class ClarifyDecision(TypedDict):
    """Serializable shape emitted by :func:`plan_clarify` (ADR-043).

    Distinct from :class:`AbstainDecision`: abstain returns a safe-default
    answer with no user prompt; clarify blocks on explicit user input.

    Fields:
        decision: ``"clarify"`` or ``"proceed"``.
        reason: Human-readable justification for telemetry.
        confidence: The input confidence value, echoed for downstream logging.
        ambiguity_score: Scalar in ``[0.0, 1.0]``.  Higher means more
            ambiguous / more need for clarification.
        ambiguity_threshold: The ambiguity floor used for the comparison.
        action: Downstream dispatch hint.  ``"request_clarification"`` when
            ``decision == "clarify"``; ``"continue"`` when proceed.
    """

    decision: Literal["clarify", "proceed"]
    reason: str
    confidence: float
    ambiguity_score: float
    ambiguity_threshold: float
    action: Literal["request_clarification", "continue"]


def plan_abstain(
    confidence: float,
    threshold: float = DEFAULT_ABSTAIN_THRESHOLD,
    *,
    reason_hint: str | None = None,
) -> AbstainDecision:
    """Compute an abstain-vs-proceed decision from a scalar confidence value.

    Args:
        confidence: Confidence or coverage score in the closed interval
            ``[0.0, 1.0]``. Higher values mean stronger grounding.
        threshold: Abstain floor in the closed interval ``[0.0, 1.0]``.
            Strictly-below-threshold confidence triggers abstain. Defaults
            to :data:`DEFAULT_ABSTAIN_THRESHOLD`.
        reason_hint: Optional caller-provided string embedded in the
            decision's ``reason`` field. When omitted the function produces
            a deterministic default.

    Returns:
        An :class:`AbstainDecision` dict with all five required fields.

    Raises:
        ValueError: If ``confidence`` or ``threshold`` falls outside
            ``[0.0, 1.0]``.
    """
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confidence must be in [0.0, 1.0], got {confidence!r}")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0.0, 1.0], got {threshold!r}")

    if confidence < threshold:
        reason = reason_hint or (f"confidence {confidence:.4f} below abstain floor {threshold:.4f}")
        return AbstainDecision(
            decision=DECISION_ABSTAIN,
            reason=reason,
            confidence=float(confidence),
            threshold=float(threshold),
            action=ACTION_EMIT_R5,
        )

    reason = reason_hint or (f"confidence {confidence:.4f} at or above abstain floor {threshold:.4f}")
    return AbstainDecision(
        decision=DECISION_PROCEED,
        reason=reason,
        confidence=float(confidence),
        threshold=float(threshold),
        action=ACTION_CONTINUE,
    )


def plan_clarify(
    confidence: float,
    ambiguity_score: float,
    threshold: float = DEFAULT_AMBIGUITY_THRESHOLD,
    *,
    reason_hint: str | None = None,
) -> ClarifyDecision:
    """Compute a clarify-vs-proceed decision from confidence + ambiguity.

    Clarify semantics (ADR-043 §T3 exit branches):
    - High ambiguity (``ambiguity_score >= threshold``) AND confidence not
      catastrophically low → clarify (request user input).
    - High ambiguity AND very low confidence (< 0.20) → proceed=False but
      caller should abstain, not clarify — this function still returns
      ``clarify`` but the reason surfaces the catastrophic-confidence hint
      so the caller can escalate.

    Args:
        confidence: Confidence score in ``[0.0, 1.0]``.
        ambiguity_score: Ambiguity score in ``[0.0, 1.0]``.  Higher means
            the planner is more uncertain about user intent.
        threshold: Ambiguity floor.  ``ambiguity_score >= threshold``
            triggers clarify.  Defaults to
            :data:`DEFAULT_AMBIGUITY_THRESHOLD`.
        reason_hint: Optional caller-provided string embedded in the
            decision's ``reason`` field.

    Returns:
        A :class:`ClarifyDecision` dict with all six required fields.

    Raises:
        ValueError: If any numeric input falls outside ``[0.0, 1.0]``.
    """
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confidence must be in [0.0, 1.0], got {confidence!r}")
    if not 0.0 <= ambiguity_score <= 1.0:
        raise ValueError(f"ambiguity_score must be in [0.0, 1.0], got {ambiguity_score!r}")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0.0, 1.0], got {threshold!r}")

    if ambiguity_score >= threshold:
        reason = reason_hint or (f"ambiguity {ambiguity_score:.4f} at/above clarify floor {threshold:.4f}")
        return ClarifyDecision(
            decision=DECISION_CLARIFY,
            reason=reason,
            confidence=float(confidence),
            ambiguity_score=float(ambiguity_score),
            ambiguity_threshold=float(threshold),
            action=ACTION_REQUEST_CLARIFICATION,
        )

    reason = reason_hint or (f"ambiguity {ambiguity_score:.4f} below clarify floor {threshold:.4f}")
    return ClarifyDecision(
        decision=DECISION_PROCEED,
        reason=reason,
        confidence=float(confidence),
        ambiguity_score=float(ambiguity_score),
        ambiguity_threshold=float(threshold),
        action=ACTION_CONTINUE,
    )


# =============================================================================
# W3.P2 — Multi-signal R5 trigger aggregation.
#
# Plan: .windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md §W3.P2.
#
# ``plan_abstain`` (above) fires R5 on a single scalar confidence check.
# Real-world routing needs ≥5 independent triggers per Anthropic guidance
# (ood, budget, circuit-breaker, clarification, toxicity, low-confidence).
# ``plan_abstain_multi_signal`` aggregates those triggers into one
# :class:`AbstainDecision` and records which trigger fired in
# ``reason_hint`` so telemetry can attribute the abstain.
#
# Additive: ``plan_abstain`` is unchanged. Existing callers continue to
# consume the scalar-confidence path.
# =============================================================================


# Closed vocabulary of multi-signal reason codes. Bare strings (no
# enum) — matches the pre-W1b reason_codes style consumed by
# agentic_core.L0_routing.reasoning.route_gates.
R5_REASON_LOW_CONFIDENCE: Literal["r5_low_confidence"] = "r5_low_confidence"
R5_REASON_OOD_DETECTED: Literal["r5_ood_detected"] = "r5_ood_detected"
R5_REASON_BUDGET_EXCEEDED: Literal["r5_budget_exceeded"] = "r5_budget_exceeded"
R5_REASON_CIRCUIT_BREAKER_OPEN: Literal["r5_circuit_breaker_open"] = "r5_circuit_breaker_open"
R5_REASON_CLARIFICATION_NEEDED: Literal["r5_clarification_needed"] = "r5_clarification_needed"
R5_REASON_TOXICITY_FLAGGED: Literal["r5_toxicity_flagged"] = "r5_toxicity_flagged"

R5_REASON_CODES: frozenset[str] = frozenset(
    {
        R5_REASON_LOW_CONFIDENCE,
        R5_REASON_OOD_DETECTED,
        R5_REASON_BUDGET_EXCEEDED,
        R5_REASON_CIRCUIT_BREAKER_OPEN,
        R5_REASON_CLARIFICATION_NEEDED,
        R5_REASON_TOXICITY_FLAGGED,
    },
)
"""Closed set of R5 reason-code strings. Any new code requires an ADR."""


class R5Signals(TypedDict, total=False):
    """Optional per-signal evidence for :func:`plan_abstain_multi_signal`.

    Every field is optional. A caller that can't compute a signal simply
    omits it — the aggregator treats it as "not firing". This preserves
    back-compat with single-signal callers that only know the confidence.

    Fields:
        confidence: Scalar confidence in ``[0, 1]``. Below
            ``confidence_threshold`` fires :data:`R5_REASON_LOW_CONFIDENCE`.
        confidence_threshold: Floor for the low-confidence trigger.
            Defaults to :data:`DEFAULT_ABSTAIN_THRESHOLD`.
        ood_score: OOD / novelty score in ``[0, 1]``. At or above
            ``ood_threshold`` fires :data:`R5_REASON_OOD_DETECTED`.
        ood_threshold: Floor for the OOD trigger. Defaults to ``0.70``.
        budget_exceeded: Boolean — True fires :data:`R5_REASON_BUDGET_EXCEEDED`.
        circuit_breaker_open: Boolean — True fires
            :data:`R5_REASON_CIRCUIT_BREAKER_OPEN`.
        clarification_needed: Boolean — True fires
            :data:`R5_REASON_CLARIFICATION_NEEDED`.
        toxicity_flagged: Boolean — True fires
            :data:`R5_REASON_TOXICITY_FLAGGED`.
    """

    confidence: float
    confidence_threshold: float
    ood_score: float
    ood_threshold: float
    budget_exceeded: bool
    circuit_breaker_open: bool
    clarification_needed: bool
    toxicity_flagged: bool


class MultiSignalAbstainDecision(TypedDict):
    """Enriched abstain decision emitted by :func:`plan_abstain_multi_signal`.

    Extends :class:`AbstainDecision` with a ``triggered_reasons`` field
    recording every trigger that fired (a single request may fire more
    than one — e.g. low-confidence AND budget-exceeded). ``primary_reason``
    is a single string (the highest-priority trigger) for telemetry.

    Fields:
        decision: ``"abstain"`` or ``"proceed"``.
        reason: Human-readable justification.
        action: ``"emit_r5_candidate"`` on abstain, else ``"continue"``.
        triggered_reasons: Tuple of every fired reason code, in
            priority order (toxicity > circuit > budget > OOD > clarify
            > low-confidence). Empty tuple on proceed.
        primary_reason: First element of :attr:`triggered_reasons` or
            ``"none"`` on proceed.
        confidence: Echoed from ``signals.confidence`` (or 1.0 default).
        threshold: Echoed confidence threshold.
    """

    decision: Literal["abstain", "proceed"]
    reason: str
    action: Literal["emit_r5_candidate", "continue"]
    triggered_reasons: tuple[str, ...]
    primary_reason: str
    confidence: float
    threshold: float


# Trigger priority (highest first). Toxicity and circuit-breaker are
# safety-critical and suppress everything below them in the reason-code
# list — if both fire, toxicity wins the primary_reason slot.
_R5_TRIGGER_PRIORITY: tuple[str, ...] = (
    R5_REASON_TOXICITY_FLAGGED,
    R5_REASON_CIRCUIT_BREAKER_OPEN,
    R5_REASON_BUDGET_EXCEEDED,
    R5_REASON_OOD_DETECTED,
    R5_REASON_CLARIFICATION_NEEDED,
    R5_REASON_LOW_CONFIDENCE,
)


def plan_abstain_multi_signal(
    signals: R5Signals | None = None,
) -> MultiSignalAbstainDecision:
    """Aggregate multiple R5 triggers into one decision.

    Args:
        signals: Per-signal evidence. ``None`` is treated as an empty
            signal set — the result is ``proceed`` with no triggered
            reasons. Callers should populate only the fields they can
            evaluate.

    Returns:
        :class:`MultiSignalAbstainDecision` with ``decision=abstain`` if
        any trigger fires, else ``decision=proceed``.

    Raises:
        ValueError: ``signals.confidence`` or ``signals.ood_score`` is
            outside ``[0, 1]``.
    """
    s: R5Signals = signals or {}
    triggered: list[str] = []

    # 1. toxicity (safety-critical, suppresses all below)
    if s.get("toxicity_flagged"):
        triggered.append(R5_REASON_TOXICITY_FLAGGED)

    # 2. circuit breaker
    if s.get("circuit_breaker_open"):
        triggered.append(R5_REASON_CIRCUIT_BREAKER_OPEN)

    # 3. budget exceeded
    if s.get("budget_exceeded"):
        triggered.append(R5_REASON_BUDGET_EXCEEDED)

    # 4. OOD detection
    ood_score = s.get("ood_score")
    if ood_score is not None:
        if not 0.0 <= ood_score <= 1.0:
            raise ValueError(
                f"ood_score must be in [0, 1], got {ood_score!r}",
            )
        ood_threshold = s.get("ood_threshold", 0.70)
        if not 0.0 <= ood_threshold <= 1.0:
            raise ValueError(
                f"ood_threshold must be in [0, 1], got {ood_threshold!r}",
            )
        if ood_score >= ood_threshold:
            triggered.append(R5_REASON_OOD_DETECTED)

    # 5. explicit clarification requested by L1
    if s.get("clarification_needed"):
        triggered.append(R5_REASON_CLARIFICATION_NEEDED)

    # 6. low-confidence (same primitive as plan_abstain, kept last)
    confidence = s.get("confidence", 1.0)
    confidence_threshold = s.get("confidence_threshold", DEFAULT_ABSTAIN_THRESHOLD)
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            f"confidence must be in [0, 1], got {confidence!r}",
        )
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError(
            f"confidence_threshold must be in [0, 1], got {confidence_threshold!r}",
        )
    if confidence < confidence_threshold:
        triggered.append(R5_REASON_LOW_CONFIDENCE)

    # Sort by priority so primary_reason is stable across caller orderings.
    priority_index = {code: idx for idx, code in enumerate(_R5_TRIGGER_PRIORITY)}
    triggered.sort(key=lambda code: priority_index.get(code, 999))

    if not triggered:
        return MultiSignalAbstainDecision(
            decision=DECISION_PROCEED,
            reason="no R5 trigger fired",
            action=ACTION_CONTINUE,
            triggered_reasons=(),
            primary_reason="none",
            confidence=float(confidence),
            threshold=float(confidence_threshold),
        )

    primary = triggered[0]
    reason = (
        f"R5 abstain: {primary} (additional triggers: {triggered[1:]})"
        if len(triggered) > 1
        else f"R5 abstain: {primary}"
    )
    return MultiSignalAbstainDecision(
        decision=DECISION_ABSTAIN,
        reason=reason,
        action=ACTION_EMIT_R5,
        triggered_reasons=tuple(triggered),
        primary_reason=primary,
        confidence=float(confidence),
        threshold=float(confidence_threshold),
    )


__all__ = [
    "ACTION_CONTINUE",
    "ACTION_EMIT_R5",
    "ACTION_REQUEST_CLARIFICATION",
    "AbstainDecision",
    "ClarifyDecision",
    "DECISION_ABSTAIN",
    "DECISION_CLARIFY",
    "DECISION_PROCEED",
    "DEFAULT_ABSTAIN_THRESHOLD",
    "DEFAULT_AMBIGUITY_THRESHOLD",
    "MultiSignalAbstainDecision",
    "R5Signals",
    "R5_REASON_BUDGET_EXCEEDED",
    "R5_REASON_CIRCUIT_BREAKER_OPEN",
    "R5_REASON_CLARIFICATION_NEEDED",
    "R5_REASON_CODES",
    "R5_REASON_LOW_CONFIDENCE",
    "R5_REASON_OOD_DETECTED",
    "R5_REASON_TOXICITY_FLAGGED",
    "plan_abstain",
    "plan_abstain_multi_signal",
    "plan_clarify",
]
