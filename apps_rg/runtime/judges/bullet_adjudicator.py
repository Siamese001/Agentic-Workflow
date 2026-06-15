"""Triggered bullet adjudicator (apps_rg-only; no agentic_core).

Design per the section-orchestration redesign (2026-06-06): bullet sections use a deterministic
hard validator + ONE batched composite LLM judge + an OPTIONAL adjudicator. The adjudicator is
NOT run on every bullet section — it escalates to the multi-provider panel ONLY when a borderline
condition makes a single-judge verdict risky.

Implemented triggers (all use data that already exists on the composite judge row + X2 gates):

  1. JUDGE_CONFIDENCE_LOW   — the composite judge's normalized_score sits within a narrow band
                               of its threshold (borderline pass or borderline fail). One judge's
                               opinion near the boundary is exactly where a second opinion helps.
  2. X2_PASS_JUDGE_RISK     — every hard X2 gate passed, the judge surfaced material risk, AND
                               the score is already borderline. Confident accepts stay fast-path;
                               adjudication is for uncertainty, not routine commentary.
  3. METRIC_BULLET_BORDERLINE (IBM) — a high-value metric-bearing bullet is present AND the judge
                               score is borderline. Metric bullets are the highest-cost place to
                               accept a wrong single-judge verdict.

NOT implemented (deferred): TOP_TWO_WITHIN_MARGIN. The Claude pool selector currently emits only
the winning score per slot (no runner-up), so a real candidate-to-candidate margin cannot be
computed without changing the selector output schema. Documented in
docs/reports/apps_rg/section_generation_design_pattern.md as a future refinement.

This module makes the DECISION only. The lane performs the panel escalation when
``AdjudicatorDecision.should_escalate`` is True.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from apps_rg.runtime.section_judge_policy import REQUIRED_JUDGE_PROVIDER_KEYS

# Default confidence band: scores within this fraction (relative to the threshold) on either side
# of the pass threshold are "borderline". E.g. threshold 4.0 on a 0-5 scale with band 0.10 ->
# borderline window [3.6, 4.4] (normalized). Tunable per call site.
DEFAULT_CONFIDENCE_BAND = 0.10

# Trigger reason codes (stable strings for artifacts/tests).
TRIGGER_JUDGE_CONFIDENCE_LOW = "JUDGE_CONFIDENCE_LOW"
TRIGGER_X2_PASS_JUDGE_RISK = "X2_PASS_JUDGE_RISK"
TRIGGER_METRIC_BULLET_BORDERLINE = "METRIC_BULLET_BORDERLINE"

# The optional adjudicator panel. Reached ONLY when a trigger fires. Judge panel SSOT =
# section_judge_policy.REQUIRED_JUDGE_PROVIDER_KEYS (cross-provider gemini_pro + openai_chatgpt;
# anthropic_claude dropped as a self-judge since Claude is the generator). Sourced from the SSOT.
ADJUDICATOR_PANEL_PROVIDER_KEYS: tuple[str, ...] = REQUIRED_JUDGE_PROVIDER_KEYS


@dataclass(frozen=True)
class AdjudicatorDecision:
    """Result of evaluating whether to escalate a bullet section to the adjudicator panel."""

    should_escalate: bool
    triggers: tuple[str, ...] = ()
    detail: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "should_escalate": self.should_escalate,
            "triggers": list(self.triggers),
            "detail": dict(self.detail),
        }


def _normalized_score_and_threshold(judge: Mapping[str, Any]) -> tuple[float | None, float | None]:
    ns = judge.get("normalized_score")
    nt = judge.get("normalized_threshold")
    if ns is None or nt is None:
        # Fall back to raw score/threshold (same scale assumption).
        ns = judge.get("score") if ns is None else ns
        nt = judge.get("threshold") if nt is None else nt
    try:
        ns_f = float(ns) if ns is not None else None
        nt_f = float(nt) if nt is not None else None
    except (TypeError, ValueError):
        return None, None
    return ns_f, nt_f


def _judge_is_model_backed(judge: Mapping[str, Any]) -> bool:
    return str(judge.get("evaluator_mode") or "") == "MODEL_BACKED"


def _judge_flags_material_risk(judge: Mapping[str, Any]) -> bool:
    """True when the judge surfaced risk despite not being a hard X2 failure."""
    if judge.get("decisive_failure"):
        return True
    if judge.get("pass") is False:
        return True
    for key in ("findings", "quality_flags", "fail_reasons", "unsupported_claims"):
        val = judge.get(key)
        if isinstance(val, (list, tuple)) and len(val) > 0:
            return True
    return False


def _score_is_borderline(
    judge: Mapping[str, Any],
    *,
    confidence_band: float,
) -> tuple[bool, dict[str, Any]]:
    ns, nt = _normalized_score_and_threshold(judge)
    if ns is None or nt is None:
        return False, {"reason": "missing_score_or_threshold"}
    # Band is relative to threshold magnitude (so it scales with 0-1 vs 0-5 rubrics).
    window = abs(nt) * confidence_band if nt else confidence_band
    low = nt - window
    high = nt + window
    borderline = low <= ns <= high
    return borderline, {
        "normalized_score": ns,
        "normalized_threshold": nt,
        "window": window,
        "band_low": low,
        "band_high": high,
    }


def _bullet_has_high_value_metric(bullet: Mapping[str, Any]) -> bool:
    if bool(bullet.get("has_metric")):
        return True
    if str(bullet.get("metric_raw") or "").strip():
        return True
    moid = bullet.get("metric_outcome_id")
    return bool(str(moid or "").strip())


def evaluate_bullet_adjudicator_trigger(
    *,
    section_id: str,
    composite_judges: Sequence[Mapping[str, Any]],
    x2_failed_gate_ids: Sequence[str],
    bullets: Sequence[Mapping[str, Any]] | None = None,
    confidence_band: float = DEFAULT_CONFIDENCE_BAND,
) -> AdjudicatorDecision:
    """Decide whether to escalate this bullet section to the multi-provider adjudicator panel.

    Args:
        section_id: e.g. "ibm_bullets" / "unify_bullets".
        composite_judges: the single-composite-judge X1D rows (already run).
        x2_failed_gate_ids: ids of failed hard X2 gates (empty => all hard gates passed).
        bullets: section bullets (for the IBM high-value-metric trigger). Optional.
        confidence_band: borderline window relative to the judge threshold.

    Returns:
        AdjudicatorDecision. ``should_escalate`` True means the lane SHOULD invoke the panel.
        Triggers are non-retry: they ask for a second opinion, not regeneration.
    """
    triggers: list[str] = []
    detail: dict[str, Any] = {"section_id": section_id}

    # Only the MODEL_BACKED composite rows are decision-relevant. Mocked/blocked rows are handled
    # by the existing X3 disposition path, not by adjudication.
    model_rows = [j for j in composite_judges if _judge_is_model_backed(j)]
    detail["model_backed_judge_count"] = len(model_rows)
    x2_all_pass = len(list(x2_failed_gate_ids)) == 0
    detail["x2_all_pass"] = x2_all_pass

    # Trigger 1: judge confidence low (borderline score on either side of threshold).
    borderline_any = False
    border_details: list[dict[str, Any]] = []
    for j in model_rows:
        bl, info = _score_is_borderline(j, confidence_band=confidence_band)
        info["provider_key"] = j.get("provider_key")
        border_details.append(info)
        if bl:
            borderline_any = True
    detail["borderline"] = border_details
    if borderline_any:
        triggers.append(TRIGGER_JUDGE_CONFIDENCE_LOW)

    # Trigger 2: hard validator passed, the judge flags material risk, and the score is already
    # borderline. A confident pass with ordinary findings remains the fast path.
    if x2_all_pass:
        risk_flagged = any(_judge_flags_material_risk(j) for j in model_rows)
        detail["x2_pass_judge_risk"] = risk_flagged
        if risk_flagged and borderline_any:
            triggers.append(TRIGGER_X2_PASS_JUDGE_RISK)

    # Trigger 3 (IBM): a high-value metric bullet is present AND the judge is borderline.
    if str(section_id).strip().lower() == "ibm_bullets" and bullets:
        has_metric_bullet = any(_bullet_has_high_value_metric(b) for b in bullets)
        detail["has_high_value_metric_bullet"] = has_metric_bullet
        if has_metric_bullet and borderline_any:
            triggers.append(TRIGGER_METRIC_BULLET_BORDERLINE)

    # De-dupe while preserving order.
    seen: set[str] = set()
    ordered_triggers = tuple(t for t in triggers if not (t in seen or seen.add(t)))
    return AdjudicatorDecision(
        should_escalate=bool(ordered_triggers),
        triggers=ordered_triggers,
        detail=detail,
    )


__all__ = [
    "ADJUDICATOR_PANEL_PROVIDER_KEYS",
    "AdjudicatorDecision",
    "DEFAULT_CONFIDENCE_BAND",
    "TRIGGER_JUDGE_CONFIDENCE_LOW",
    "TRIGGER_METRIC_BULLET_BORDERLINE",
    "TRIGGER_X2_PASS_JUDGE_RISK",
    "evaluate_bullet_adjudicator_trigger",
]
