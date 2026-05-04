"""apps_lic Scope-Calibrated Ask Engine (SE-P0c).

Derives the appropriate CTA (call-to-action) ask for an outreach message
from the intersection of recipient seniority, relationship distance,
hiring posture, channel, and outreach mode.

Contract
--------
- Decision-only: no provider calls, no state writes, no subprocess.
- Produces ask_friction_score 0.0–1.0.
  - 0.0 = minimal friction (easy for recipient to engage or decline)
  - 1.0 = maximum friction (demanding, high-effort ask)
- Bound-fail if ask_friction_score > 0.5 AND override not configured.
- Reciprocity-front pattern required for executive cold outreach
  (offer perspective/value BEFORE making the ask).
- Forbidden default CTA: "discuss opportunities" — too generic.
- Referral path: make forwarding easy (short, forwardable).

Ask calibration matrix:
  Cold + EXEC/C_LEVEL/CTO/VP_ENG → low-friction, reciprocity-front
  Cold + HIRING_MANAGER          → direct value-first, low friction
  Cold + RECRUITER/SENIOR_TA     → direct, concise, role-specific
  Warm + any                     → medium friction ok (shared context)
  Referral + any                 → forwardable, light CTA
  Followup + any                 → light nudge, very brief

Plan: .windsurf/plans/apps-lic-canonical-spine-wireup-e7c2a5.md SE-P0c
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ASK_FRICTION_BOUND = 0.5   # fail-closed above this unless override

EXECUTIVE_CLASSES = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})
RECRUITER_CLASSES  = frozenset({"RECRUITER", "SENIOR_TA"})

# CTA style descriptors
CTA_STYLE_LOW_FRICTION_RECIPROCITY   = "low_friction_reciprocity_first"
CTA_STYLE_DIRECT_VALUE_FIRST         = "direct_value_first"
CTA_STYLE_DIRECT_CONCISE             = "direct_concise"
CTA_STYLE_MEDIUM_ASK                 = "medium_ask"
CTA_STYLE_FORWARDABLE                = "forwardable_light"
CTA_STYLE_LIGHT_NUDGE                = "light_nudge"

FORBIDDEN_CTA_PATTERNS = frozenset({
    "discuss opportunities",
    "explore opportunities",
    "connect about opportunities",
})


# ---------------------------------------------------------------------------
# Hiring posture (signal from briefing / manifest)
# ---------------------------------------------------------------------------

HIRING_POSTURES = frozenset({
    "actively_hiring",  # JD posted, headcount open
    "warm",             # known to be hiring but no open JD
    "cold",             # no signal
    "unknown",          # no data — treated like cold
})


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AskCalibration:
    """Calibrated ask recommendation for a specific outreach context.

    ask_friction_score: float 0.0–1.0
    cta_style: descriptor string
    is_bound_fail: True if ask_friction_score > ASK_FRICTION_BOUND
                   (unless override_configured=True)
    recommended_cta: short guidance string (not verbatim copy — guidance only)
    reciprocity_first: True when the message should offer value before asking
    evidence_ref: machine-readable evidence string
    """

    ask_friction_score: float
    cta_style: str
    is_bound_fail: bool
    recommended_cta: str
    reciprocity_first: bool
    override_configured: bool
    evidence_ref: str
    warnings: Tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class ScopeCalibratedAskEngine:
    """Derive the appropriate CTA ask for an outreach context.

    Usage::

        engine = ScopeCalibratedAskEngine()
        calibration = engine.calibrate(
            recipient_class="EXECUTIVE",
            outreach_mode="cold",
            channel="email",
            relationship_distance="cold",
            hiring_posture="unknown",
        )
        if calibration.is_bound_fail:
            # ask is too demanding — must lower friction before dispatch
            ...

    override_high_friction can be set True for contexts where high friction
    is explicitly acceptable (configured override). The score is still computed
    and emitted in evidence_ref; only is_bound_fail is suppressed.
    """

    def calibrate(
        self,
        *,
        recipient_class: str,
        outreach_mode: str,
        channel: str,
        relationship_distance: str = "cold",
        hiring_posture: str = "unknown",
        override_high_friction: bool = False,
    ) -> AskCalibration:
        """Calibrate the ask for the given outreach context.

        Args:
            recipient_class: e.g. "EXECUTIVE", "RECRUITER", "HIRING_MANAGER"
            outreach_mode: "cold"|"warm"|"referral"|"followup"
            channel: "email"|"linkedin"|"text"
            relationship_distance: "cold"|"warm"|"referral"|"known"
            hiring_posture: "actively_hiring"|"warm"|"cold"|"unknown"
            override_high_friction: suppress bound-fail (still scores + warns)

        Returns:
            AskCalibration with ask_friction_score, cta_style, is_bound_fail,
            recommended_cta, reciprocity_first.
        """
        warnings: List[str] = []

        score, cta_style, recommended_cta, reciprocity_first = self._score(
            recipient_class=recipient_class,
            outreach_mode=outreach_mode,
            channel=channel,
            relationship_distance=relationship_distance,
            hiring_posture=hiring_posture,
        )

        # Warn if any forbidden CTA pattern is close to default
        for forbidden in FORBIDDEN_CTA_PATTERNS:
            if forbidden in recommended_cta.lower():
                warnings.append(
                    f"recommended_cta contains forbidden pattern: {forbidden!r}"
                )

        is_bound_fail = score > ASK_FRICTION_BOUND and not override_high_friction

        evidence_ref = (
            f"recipient_class={recipient_class} outreach_mode={outreach_mode} "
            f"channel={channel} relationship_distance={relationship_distance} "
            f"hiring_posture={hiring_posture} "
            f"ask_friction_score={score:.2f} cta_style={cta_style} "
            f"bound_fail={is_bound_fail} override={override_high_friction}"
        )

        return AskCalibration(
            ask_friction_score=score,
            cta_style=cta_style,
            is_bound_fail=is_bound_fail,
            recommended_cta=recommended_cta,
            reciprocity_first=reciprocity_first,
            override_configured=override_high_friction,
            evidence_ref=evidence_ref,
            warnings=tuple(warnings),
        )

    # ------------------------------------------------------------------
    # Scoring logic
    # ------------------------------------------------------------------

    def _score(
        self,
        *,
        recipient_class: str,
        outreach_mode: str,
        channel: str,
        relationship_distance: str,
        hiring_posture: str,
    ) -> Tuple[float, str, str, bool]:
        """Return (score, cta_style, recommended_cta, reciprocity_first)."""

        # Base score by outreach_mode × relationship_distance
        base = self._base_score(outreach_mode, relationship_distance)

        # Recipient-class modifier
        rc_mod = self._recipient_class_modifier(recipient_class, outreach_mode)

        # Channel modifier (linkedin/text push toward lower friction — short = easier)
        ch_mod = self._channel_modifier(channel)

        # Hiring posture modifier (actively_hiring → easier to ask)
        hp_mod = self._hiring_posture_modifier(hiring_posture)

        raw = max(0.0, min(1.0, base + rc_mod + ch_mod + hp_mod))

        cta_style, recommended_cta, reciprocity_first = self._cta_guidance(
            recipient_class=recipient_class,
            outreach_mode=outreach_mode,
            channel=channel,
            relationship_distance=relationship_distance,
        )

        return round(raw, 2), cta_style, recommended_cta, reciprocity_first

    def _base_score(self, outreach_mode: str, relationship_distance: str) -> float:
        # Lower base = lower friction = good
        mode_base = {
            "cold":     0.40,
            "warm":     0.25,
            "referral": 0.20,
            "followup": 0.15,
        }.get(outreach_mode, 0.40)

        dist_adj = {
            "cold":     +0.10,
            "warm":     -0.05,
            "referral": -0.10,
            "known":    -0.15,
        }.get(relationship_distance, +0.10)

        return mode_base + dist_adj

    def _recipient_class_modifier(self, recipient_class: str, outreach_mode: str) -> float:
        # Executive cold = most friction-sensitive (they get flooded — keep low)
        if recipient_class in EXECUTIVE_CLASSES:
            return 0.0 if outreach_mode != "cold" else -0.05
        if recipient_class == "HIRING_MANAGER":
            return -0.05
        if recipient_class in RECRUITER_CLASSES:
            return -0.10  # recruiters expect direct asks
        if recipient_class == "REFERRAL_CONTACT":
            return -0.10  # referral is forwardable — easy ask
        return 0.0

    def _channel_modifier(self, channel: str) -> float:
        # LinkedIn and text are already short — shorter = easier to engage
        return {
            "linkedin": -0.05,
            "text":     -0.10,
            "email":    0.00,
        }.get(channel, 0.00)

    def _hiring_posture_modifier(self, hiring_posture: str) -> float:
        # Actively hiring → ask is easier (they want to hear from candidates)
        return {
            "actively_hiring": -0.10,
            "warm":            -0.05,
            "cold":            +0.05,
            "unknown":         0.00,
        }.get(hiring_posture, 0.00)

    def _cta_guidance(
        self,
        *,
        recipient_class: str,
        outreach_mode: str,
        channel: str,
        relationship_distance: str,
    ) -> Tuple[str, str, bool]:
        """Return (cta_style, recommended_cta, reciprocity_first)."""

        if outreach_mode == "followup":
            return (
                CTA_STYLE_LIGHT_NUDGE,
                "A brief note following up — happy to share more if useful.",
                False,
            )

        if outreach_mode == "referral" or relationship_distance == "referral":
            return (
                CTA_STYLE_FORWARDABLE,
                "If you think this could be a fit, would you be open to a quick intro? Easy to forward.",
                False,
            )

        if recipient_class in EXECUTIVE_CLASSES and outreach_mode == "cold":
            return (
                CTA_STYLE_LOW_FRICTION_RECIPROCITY,
                "Happy to share the one-paragraph version — would a 15-minute call work?",
                True,  # reciprocity_first=True
            )

        if recipient_class == "HIRING_MANAGER":
            return (
                CTA_STYLE_DIRECT_VALUE_FIRST,
                "Would a brief call make sense to see if there's a fit?",
                False,
            )

        if recipient_class in RECRUITER_CLASSES:
            return (
                CTA_STYLE_DIRECT_CONCISE,
                "Happy to send a resume — would that be helpful?",
                False,
            )

        if recipient_class in EXECUTIVE_CLASSES:  # warm/referral
            return (
                CTA_STYLE_MEDIUM_ASK,
                "Would a 20-minute call work to explore whether there's a fit?",
                False,
            )

        return (
            CTA_STYLE_DIRECT_CONCISE,
            "Would a quick call be useful?",
            False,
        )
