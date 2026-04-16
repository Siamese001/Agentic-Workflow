"""F06 confidence-score abstain planning primitive.

Produces a serializable abstain decision based on a comparison of an input
confidence (or coverage) value against a configurable floor. Downstream
consumers are Wave D4 (R5 fallback / abstain route in `path_router`) and
Wave D5 (`LOW_NORMATIVE_COVERAGE` consumer). Both read the stable dict shape
emitted by :func:`plan_abstain`.

Wave D scope: implements WC-G07 / F06 per
`.windsurf/plans/wave_d_plan.md` §3 Slice D3.

Design notes (D3.1):
- Pure synchronous primitive. No LLM, no cache, no spine, no async.
- Intentionally decoupled from ``query_planner.py`` (which is async,
  LLM-driven, and already heavily decorated with ADG lifecycle emissions).
  Keeping the abstain logic separate delivers the smaller safe change set
  required by the Wave D plan's D3.1 entry-gate preference.
- All outputs are primitive types so the decision is trivially
  ``json.dumps``-serializable for telemetry and cross-process hand-off.
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

# Stable decision strings. Treat as a closed enum.
DECISION_ABSTAIN: Literal["abstain"] = "abstain"
DECISION_PROCEED: Literal["proceed"] = "proceed"


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


__all__ = [
    "ACTION_CONTINUE",
    "ACTION_EMIT_R5",
    "AbstainDecision",
    "DECISION_ABSTAIN",
    "DECISION_PROCEED",
    "DEFAULT_ABSTAIN_THRESHOLD",
    "plan_abstain",
]
