"""apps_lic Asymmetric Insight Engine (SE-P1d).

Evaluates whether an ``AsymmetricInsight`` is required, optional, or
not applicable for an outreach context.  Config-gated: requirement is
driven by ``lic_plan_rules.yaml`` ``recipient_class_rules.<rc>.asymmetric_insight_required``.

Contract
--------
- Decision-only: no provider calls, no state writes, no subprocess.
- Config-gated: only required when ``asymmetric_insight_required: true`` is
  configured for the (recipient_class, outreach_mode) combination.
- Simple recruiter follow-up is correct, short, and high-converting without
  asymmetric insight.
- ``AsymmetricInsight`` is an observation that the recipient is unlikely to
  have already formed — derived from company/market/role intelligence in
  the briefing artifact.

Insight requirement matrix (from lic_plan_rules.yaml):
  EXECUTIVE, C_LEVEL, CTO, VP_ENG → asymmetric_insight_required: true
  HIRING_MANAGER, RECRUITER, SENIOR_TA, REFERRAL_CONTACT → false

Outreach mode override:
  followup → never required (brevity-first)
  referral → never required (forwarding ease > insight depth)

Plan: .windsurf/plans/apps-lic-canonical-spine-wireup-e7c2a5.md SE-P1d
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, Optional, Tuple

# ---------------------------------------------------------------------------
# Default config (mirrors lic_plan_rules.yaml recipient_class_rules)
# ---------------------------------------------------------------------------

_DEFAULT_INSIGHT_REQUIRED: Dict[str, bool] = {
    "EXECUTIVE":        True,
    "C_LEVEL":          True,
    "CTO":              True,
    "VP_ENG":           True,
    "HIRING_MANAGER":   False,
    "RECRUITER":        False,
    "SENIOR_TA":        False,
    "REFERRAL_CONTACT": False,
}

# Outreach modes that ALWAYS bypass insight requirement
_BYPASS_MODES: FrozenSet[str] = frozenset({"followup", "referral"})

# ---------------------------------------------------------------------------
# AsymmetricInsight artifact
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AsymmetricInsight:
    """A single asymmetric insight claim for an outreach draft.

    An asymmetric insight is an observation that the recipient is unlikely
    to have already formed themselves — derived from company/market/role
    intelligence in the briefing artifact.

    source_ref: must be non-empty and bound to a briefing source item URI.
    confidence: 0.0–1.0; below 0.5 → engine will flag as weak.
    """

    insight_text: str
    source_ref: str      # bound to briefing source item URI
    insight_type: str    # "company_strategy"|"market_observation"|"role_context"|"technical_angle"
    confidence: float = 1.0


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

VERDICT_REQUIRED       = "required"
VERDICT_OPTIONAL       = "optional"
VERDICT_NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class InsightRequirement:
    """Result of evaluating asymmetric insight requirement.

    verdict: "required" | "optional" | "not_applicable"
    is_satisfied: True if verdict != "required" OR insight_provided.
    is_fail_closed: True when required AND insight_provided=False AND
                    omission_policy="fail_closed".
    hitl_required: True when required AND insight_provided=False AND
                   omission_policy="hitl_required".
    rationale: human-readable explanation.
    evidence_ref: machine-readable evidence string.
    """

    verdict: str
    is_satisfied: bool
    is_fail_closed: bool
    hitl_required: bool
    rationale: str
    evidence_ref: str
    warnings: Tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class AsymmetricInsightEngine:
    """Evaluate whether asymmetric insight is required for an outreach context.

    Usage::

        engine = AsymmetricInsightEngine()
        req = engine.evaluate(
            recipient_class="EXECUTIVE",
            outreach_mode="cold",
            insight_provided=False,
            omission_policy="hitl_required",
        )
        if req.hitl_required:
            # produce draft but escalate to HITL for insight review
            ...

    Config-override at construction time (for testing and per-deployment config)::

        engine = AsymmetricInsightEngine(
            config_overrides={"HIRING_MANAGER": True}
        )
    """

    def __init__(
        self,
        *,
        config_overrides: Optional[Dict[str, bool]] = None,
    ) -> None:
        self._config: Dict[str, bool] = dict(_DEFAULT_INSIGHT_REQUIRED)
        if config_overrides:
            self._config.update(config_overrides)

    @classmethod
    def from_plan_rules(cls, plan_rules: Dict[str, Any]) -> "AsymmetricInsightEngine":
        """Build engine from parsed ``lic_plan_rules.yaml`` content.

        Reads ``recipient_class_rules.<rc>.asymmetric_insight_required``.
        """
        overrides: Dict[str, bool] = {}
        for rc, conf in (plan_rules.get("recipient_class_rules") or {}).items():
            if isinstance(conf, dict) and "asymmetric_insight_required" in conf:
                overrides[rc] = bool(conf["asymmetric_insight_required"])
        return cls(config_overrides=overrides)

    def is_required_for(self, recipient_class: str) -> bool:
        """Return True when asymmetric insight is configured as required."""
        return self._config.get(recipient_class, False)

    def evaluate(
        self,
        *,
        recipient_class: str,
        outreach_mode: str,
        insight_provided: bool = False,
        omission_policy: str = "omit_unsupported",
        insights: Optional[Tuple[AsymmetricInsight, ...]] = None,
    ) -> InsightRequirement:
        """Evaluate asymmetric insight requirement for the given context.

        Args:
            recipient_class: target recipient class.
            outreach_mode: "cold"|"warm"|"referral"|"followup"
            insight_provided: True if caller already provides a valid insight.
            omission_policy: "omit_unsupported"|"hitl_required"|"fail_closed"
            insights: optional tuple of AsymmetricInsight objects to validate.

        Returns:
            InsightRequirement.
        """
        warnings = []

        # Validate provided insights
        if insights:
            for ins in insights:
                if not ins.source_ref:
                    warnings.append(
                        f"AsymmetricInsight {ins.insight_text[:40]!r} has no source_ref — "
                        "must be bound to a briefing source item"
                    )
                if ins.confidence < 0.5:
                    warnings.append(
                        f"AsymmetricInsight confidence={ins.confidence:.2f} < 0.5 — weak signal"
                    )

        # Determine base verdict
        verdict, rationale = self._resolve_verdict(
            recipient_class=recipient_class,
            outreach_mode=outreach_mode,
        )

        # Resolve satisfaction
        if verdict == VERDICT_REQUIRED:
            # Satisfied only when insight_provided=True AND insights have valid source_refs
            has_valid = insight_provided and bool(insights) and all(
                bool(ins.source_ref) for ins in (insights or ())
            )
            is_satisfied = has_valid
        else:
            is_satisfied = True

        is_fail_closed = (
            verdict == VERDICT_REQUIRED
            and not is_satisfied
            and omission_policy == "fail_closed"
        )
        hitl_required = (
            verdict == VERDICT_REQUIRED
            and not is_satisfied
            and omission_policy == "hitl_required"
        )

        evidence_ref = (
            f"recipient_class={recipient_class} outreach_mode={outreach_mode} "
            f"omission_policy={omission_policy} "
            f"insight_provided={insight_provided} "
            f"insights_count={len(insights) if insights else 0} "
            f"verdict={verdict} "
            f"is_satisfied={is_satisfied} "
            f"is_fail_closed={is_fail_closed} "
            f"hitl_required={hitl_required}"
        )

        return InsightRequirement(
            verdict=verdict,
            is_satisfied=is_satisfied,
            is_fail_closed=is_fail_closed,
            hitl_required=hitl_required,
            rationale=rationale,
            evidence_ref=evidence_ref,
            warnings=tuple(warnings),
        )

    # ------------------------------------------------------------------
    # Verdict resolution
    # ------------------------------------------------------------------

    def _resolve_verdict(
        self,
        *,
        recipient_class: str,
        outreach_mode: str,
    ) -> Tuple[str, str]:
        """Return (verdict, rationale)."""

        # Bypass modes always skip insight requirement
        if outreach_mode in _BYPASS_MODES:
            return (
                VERDICT_NOT_APPLICABLE,
                f"outreach_mode={outreach_mode!r} — asymmetric insight not required "
                "(brevity/forwarding ease takes priority)",
            )

        config_required = self._config.get(recipient_class, False)

        if config_required:
            return (
                VERDICT_REQUIRED,
                f"asymmetric_insight_required=true for {recipient_class!r} "
                f"in outreach_mode={outreach_mode!r} — "
                "insight must be derived from briefing and bound to source_ref",
            )

        return (
            VERDICT_NOT_APPLICABLE,
            f"asymmetric_insight_required=false for {recipient_class!r} — not required",
        )
