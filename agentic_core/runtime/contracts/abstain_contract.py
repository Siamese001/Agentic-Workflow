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
        reason = reason_hint or (
            f"ambiguity {ambiguity_score:.4f} at/above clarify floor {threshold:.4f}"
        )
        return ClarifyDecision(
            decision=DECISION_CLARIFY,
            reason=reason,
            confidence=float(confidence),
            ambiguity_score=float(ambiguity_score),
            ambiguity_threshold=float(threshold),
            action=ACTION_REQUEST_CLARIFICATION,
        )

    reason = reason_hint or (
        f"ambiguity {ambiguity_score:.4f} below clarify floor {threshold:.4f}"
    )
    return ClarifyDecision(
        decision=DECISION_PROCEED,
        reason=reason,
        confidence=float(confidence),
        ambiguity_score=float(ambiguity_score),
        ambiguity_threshold=float(threshold),
        action=ACTION_CONTINUE,
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
    "plan_abstain",
    "plan_clarify",
]
