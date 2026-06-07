"""Code-based X2 aggregation for bullet sections (apps_rg-only; no agentic_core).

Per the section-orchestration redesign: after the deterministic hard validator (X2 gates) and the
ONE composite LLM judge run, a deterministic aggregation step combines them into a section-level
accept decision. This is the "X2 AGGREGATION" box in the design pattern:

    hard validator failure        -> reject (do not accept)
    judge decisive failure        -> reject
    valid + judge >= pass_floor   -> candidate-accept
    margin below margin_threshold -> mark "should adjudicate" (borderline)

This does NOT replace X3 disposition (which remains the single authority that emits the final
x3_code). It produces an advisory aggregation record that:
  * confirms the deterministic+judge agreement, and
  * flags borderline cases the adjudicator should escalate.

The aggregation is pure/deterministic and testable; the lane writes its output to
``bullet_x2_aggregation.json`` for evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

# Section-level accept floor for the composite judge (normalized). A judge below this is not an
# accept regardless of X2. Kept conservative; the judge's own threshold still governs pass/fail.
DEFAULT_PASS_THRESHOLD = 0.72

# Minimum normalized gap between the composite judge score and its threshold for the accept to be
# "confident". Below this gap the section is borderline -> adjudicate.
DEFAULT_MARGIN_THRESHOLD = 0.05

AGG_ACCEPT = "ACCEPT"
AGG_REJECT_X2 = "REJECT_X2_HARD_FAILURE"
AGG_REJECT_JUDGE = "REJECT_JUDGE_DECISIVE"
AGG_BORDERLINE = "ACCEPT_BORDERLINE_ADJUDICATE"


@dataclass(frozen=True)
class BulletAggregation:
    """Deterministic section-level aggregation of X2 gates + composite judge."""

    decision: str
    accepted: bool
    should_adjudicate: bool
    pass_threshold: float
    margin_threshold: float
    composite_score: float | None
    composite_threshold: float | None
    margin: float | None
    x2_failed_gate_ids: tuple[str, ...]
    reasons: tuple[str, ...] = ()
    detail: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "accepted": self.accepted,
            "should_adjudicate": self.should_adjudicate,
            "pass_threshold": self.pass_threshold,
            "margin_threshold": self.margin_threshold,
            "composite_score": self.composite_score,
            "composite_threshold": self.composite_threshold,
            "margin": self.margin,
            "x2_failed_gate_ids": list(self.x2_failed_gate_ids),
            "reasons": list(self.reasons),
            "detail": dict(self.detail),
        }


def _best_model_backed_composite(
    composite_judges: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    """Pick the highest normalized-score MODEL_BACKED composite row (the section's judge verdict)."""
    model_rows = [j for j in composite_judges if str(j.get("evaluator_mode") or "") == "MODEL_BACKED"]
    if not model_rows:
        return None

    def _ns(j: Mapping[str, Any]) -> float:
        v = j.get("normalized_score", j.get("score"))
        try:
            return float(v) if v is not None else -1.0
        except (TypeError, ValueError):
            return -1.0

    return max(model_rows, key=_ns)


def aggregate_bullet_section(
    *,
    section_id: str,
    composite_judges: Sequence[Mapping[str, Any]],
    x2_failed_gate_ids: Sequence[str],
    pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    margin_threshold: float = DEFAULT_MARGIN_THRESHOLD,
) -> BulletAggregation:
    """Combine hard X2 gates + composite judge into a deterministic section accept decision.

    Order of precedence (matches the design-pattern X2-aggregation box):
      1. Any hard X2 gate failure  -> REJECT_X2_HARD_FAILURE (no accept, no adjudication).
      2. Judge decisive failure    -> REJECT_JUDGE_DECISIVE.
      3. Composite below pass floor -> REJECT_JUDGE_DECISIVE (treated as not-accept).
      4. Accept; if margin below threshold -> ACCEPT_BORDERLINE_ADJUDICATE (should_adjudicate).
      5. Otherwise -> ACCEPT.
    """
    failed = tuple(str(g) for g in x2_failed_gate_ids)
    reasons: list[str] = []
    detail: dict[str, Any] = {"section_id": section_id}

    composite = _best_model_backed_composite(composite_judges)
    cs: float | None = None
    ct: float | None = None
    margin: float | None = None
    if composite is not None:
        raw_cs = composite.get("normalized_score", composite.get("score"))
        raw_ct = composite.get("normalized_threshold", composite.get("threshold"))
        try:
            cs = float(raw_cs) if raw_cs is not None else None
            ct = float(raw_ct) if raw_ct is not None else None
        except (TypeError, ValueError):
            cs = ct = None
        if cs is not None and ct is not None:
            margin = cs - ct
        detail["composite_provider_key"] = composite.get("provider_key")
        detail["composite_decisive_failure"] = bool(composite.get("decisive_failure"))

    # 1. Hard X2 failure dominates.
    if failed:
        reasons.append(f"x2_hard_failure:{','.join(failed)}")
        return BulletAggregation(
            decision=AGG_REJECT_X2,
            accepted=False,
            should_adjudicate=False,
            pass_threshold=pass_threshold,
            margin_threshold=margin_threshold,
            composite_score=cs,
            composite_threshold=ct,
            margin=margin,
            x2_failed_gate_ids=failed,
            reasons=tuple(reasons),
            detail=detail,
        )

    # 2/3. Judge decisive failure or below the pass floor => not an accept.
    if composite is None:
        reasons.append("no_model_backed_composite_judge")
        return BulletAggregation(
            decision=AGG_REJECT_JUDGE,
            accepted=False,
            should_adjudicate=False,
            pass_threshold=pass_threshold,
            margin_threshold=margin_threshold,
            composite_score=cs,
            composite_threshold=ct,
            margin=margin,
            x2_failed_gate_ids=failed,
            reasons=tuple(reasons),
            detail=detail,
        )
    if bool(composite.get("decisive_failure")):
        reasons.append("judge_decisive_failure")
        return BulletAggregation(
            decision=AGG_REJECT_JUDGE,
            accepted=False,
            should_adjudicate=False,
            pass_threshold=pass_threshold,
            margin_threshold=margin_threshold,
            composite_score=cs,
            composite_threshold=ct,
            margin=margin,
            x2_failed_gate_ids=failed,
            reasons=tuple(reasons),
            detail=detail,
        )
    if cs is None or cs < pass_threshold:
        reasons.append(f"composite_below_pass_threshold:{cs}<{pass_threshold}")
        return BulletAggregation(
            decision=AGG_REJECT_JUDGE,
            accepted=False,
            should_adjudicate=False,
            pass_threshold=pass_threshold,
            margin_threshold=margin_threshold,
            composite_score=cs,
            composite_threshold=ct,
            margin=margin,
            x2_failed_gate_ids=failed,
            reasons=tuple(reasons),
            detail=detail,
        )

    # 4/5. Accept; borderline if margin is thin.
    borderline = margin is not None and margin < margin_threshold
    if borderline:
        reasons.append(f"low_margin:{margin}<{margin_threshold}")
        return BulletAggregation(
            decision=AGG_BORDERLINE,
            accepted=True,
            should_adjudicate=True,
            pass_threshold=pass_threshold,
            margin_threshold=margin_threshold,
            composite_score=cs,
            composite_threshold=ct,
            margin=margin,
            x2_failed_gate_ids=failed,
            reasons=tuple(reasons),
            detail=detail,
        )
    reasons.append("accept_confident")
    return BulletAggregation(
        decision=AGG_ACCEPT,
        accepted=True,
        should_adjudicate=False,
        pass_threshold=pass_threshold,
        margin_threshold=margin_threshold,
        composite_score=cs,
        composite_threshold=ct,
        margin=margin,
        x2_failed_gate_ids=failed,
        reasons=tuple(reasons),
        detail=detail,
    )


__all__ = [
    "AGG_ACCEPT",
    "AGG_BORDERLINE",
    "AGG_REJECT_JUDGE",
    "AGG_REJECT_X2",
    "BulletAggregation",
    "DEFAULT_MARGIN_THRESHOLD",
    "DEFAULT_PASS_THRESHOLD",
    "aggregate_bullet_section",
]
