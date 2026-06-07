"""apps_lic Channel-Length Enforcer (SE-P0b).

Enforces configurable word-count ceilings per (channel, recipient_class, outreach_mode).
Ceiling configuration is read from ``lic_plan_rules.yaml`` channel_rules.

Fail-closed when word_count > ceiling × tolerance (default 1.10).
Below ceiling: returns a contextual advisory (not a hard-fail).

Contract
--------
- Decision-only: no provider calls, no state writes, no subprocess.
- Tolerance is configurable; default 1.10 (plan spec).
- Ceiling lookup is (channel, recipient_class, outreach_mode) →
  falls back to channel-wide defaults if no exact match.
- Produces evidence_ref (ceiling, actual, tolerance) on fail.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-canonical-spine-wireup-e7c2a5.md SE-P0b
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

DEFAULT_TOLERANCE = 1.10

# ---------------------------------------------------------------------------
# Built-in ceiling table (mirrors lic_plan_rules.yaml channel_rules)
# Format: (channel, recipient_class_or_"any", outreach_mode_or_"any") → max_words
# ---------------------------------------------------------------------------

_BUILTIN_CEILINGS: Dict[Tuple[str, str, str], int] = {
    # email — exec / senior
    ("email", "EXECUTIVE",      "cold"):     100,
    ("email", "EXECUTIVE",      "warm"):     120,
    ("email", "EXECUTIVE",      "referral"): 120,
    ("email", "EXECUTIVE",      "followup"): 120,
    ("email", "C_LEVEL",        "cold"):     100,
    ("email", "C_LEVEL",        "warm"):     120,
    ("email", "C_LEVEL",        "referral"): 120,
    ("email", "C_LEVEL",        "followup"): 120,
    ("email", "VP_ENG",         "cold"):     100,
    ("email", "VP_ENG",         "warm"):     120,
    ("email", "VP_ENG",         "referral"): 120,
    ("email", "VP_ENG",         "followup"): 120,
    ("email", "CTO",            "cold"):     100,
    ("email", "CTO",            "warm"):     120,
    ("email", "CTO",            "referral"): 120,
    ("email", "CTO",            "followup"): 120,
    # email — hiring manager
    ("email", "HIRING_MANAGER", "cold"):     150,
    ("email", "HIRING_MANAGER", "warm"):     200,
    ("email", "HIRING_MANAGER", "referral"): 200,
    ("email", "HIRING_MANAGER", "followup"): 200,
    # email — recruiter / TA
    ("email", "RECRUITER",      "cold"):     150,
    ("email", "RECRUITER",      "warm"):     200,
    ("email", "RECRUITER",      "referral"): 200,
    ("email", "RECRUITER",      "followup"): 200,
    ("email", "SENIOR_TA",      "cold"):     150,
    ("email", "SENIOR_TA",      "warm"):     200,
    ("email", "SENIOR_TA",      "referral"): 200,
    ("email", "SENIOR_TA",      "followup"): 200,
    # email — referral contact
    ("email", "REFERRAL_CONTACT", "cold"):     150,
    ("email", "REFERRAL_CONTACT", "warm"):     200,
    ("email", "REFERRAL_CONTACT", "referral"): 80,
    ("email", "REFERRAL_CONTACT", "followup"): 200,
    # linkedin — any recipient class
    ("linkedin", "any", "cold"):     60,
    ("linkedin", "any", "warm"):     80,
    ("linkedin", "any", "referral"): 80,
    ("linkedin", "any", "followup"): 80,
    # text — any
    ("text", "any", "any"): 50,
    # referral_intro special channel
    ("referral_intro", "any", "any"): 80,
}

# Email fallback for recipient classes not explicitly listed
_EMAIL_FALLBACK_COLD = 200
_EMAIL_FALLBACK_WARM = 250


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LengthEnforcementResult:
    """Result of channel-length enforcement check.

    is_compliant=True: draft is within ceiling (possibly advisory warning).
    is_compliant=False AND is_hard_fail=True: word_count > ceiling × tolerance.
    is_compliant=False AND is_hard_fail=False: word_count in (ceiling, ceiling × tolerance].
    """

    is_compliant: bool           # True when word_count <= ceiling
    is_hard_fail: bool           # True when word_count > ceiling × tolerance
    word_count: int
    ceiling: int
    tolerance: float
    hard_fail_threshold: int     # = ceil(ceiling × tolerance)
    channel: str
    recipient_class: str
    outreach_mode: str
    evidence_ref: str            # human-readable evidence string


# ---------------------------------------------------------------------------
# Enforcer
# ---------------------------------------------------------------------------

class ChannelLengthEnforcer:
    """Enforce channel word-count ceilings.

    Usage::

        enforcer = ChannelLengthEnforcer()
        result = enforcer.check(
            draft_text="...",
            channel="email",
            recipient_class="EXECUTIVE",
            outreach_mode="cold",
        )
        if result.is_hard_fail:
            # fail-closed
            ...

    Custom ceiling overrides can be injected at construction time (for tests)
    or loaded from ``lic_plan_rules.yaml`` via ``from_plan_rules()``.
    """

    def __init__(
        self,
        *,
        ceiling_overrides: Optional[Dict[Tuple[str, str, str], int]] = None,
        tolerance: float = DEFAULT_TOLERANCE,
    ) -> None:
        self._ceilings: Dict[Tuple[str, str, str], int] = dict(_BUILTIN_CEILINGS)
        if ceiling_overrides:
            self._ceilings.update(ceiling_overrides)
        self._tolerance = tolerance

    @classmethod
    def from_plan_rules(cls, plan_rules: Dict[str, Any]) -> "ChannelLengthEnforcer":
        """Build enforcer from parsed ``lic_plan_rules.yaml`` content.

        Merges builtin ceilings with any overrides in channel_rules.
        """
        overrides: Dict[Tuple[str, str, str], int] = {}
        tolerance = DEFAULT_TOLERANCE

        channel_rules = plan_rules.get("channel_rules", {}) or {}
        for channel_name, channel_conf in channel_rules.items():
            if not isinstance(channel_conf, dict):
                continue
            ch_tolerance = channel_conf.get("ceiling_tolerance", DEFAULT_TOLERANCE)
            if channel_name not in ("email", "linkedin", "text"):
                continue
            max_word_counts = channel_conf.get("max_word_counts", {}) or {}
            for key_str, ceiling in max_word_counts.items():
                if not isinstance(ceiling, int):
                    continue
                # Parse "RECIPIENT_CLASS_mode" pattern
                parts = key_str.rsplit("_", 1)
                if len(parts) == 2:
                    rc, mode = parts[0], parts[1]
                    overrides[(channel_name, rc, mode)] = ceiling
                else:
                    overrides[(channel_name, key_str, "any")] = ceiling
            # Per-channel tolerance
            tolerance = min(tolerance, float(ch_tolerance))

        return cls(ceiling_overrides=overrides, tolerance=tolerance)

    def resolve_ceiling(
        self,
        channel: str,
        recipient_class: str,
        outreach_mode: str,
    ) -> int:
        """Resolve the effective ceiling for this (channel, recipient_class, outreach_mode) triple.

        Lookup order:
        1. Exact (channel, recipient_class, outreach_mode)
        2. (channel, "any", outreach_mode)
        3. (channel, recipient_class, "any")
        4. (channel, "any", "any")
        5. Hard fallback based on channel + outreach_mode
        """
        for rc_key in (recipient_class, "any"):
            for mode_key in (outreach_mode, "any"):
                key = (channel, rc_key, mode_key)
                if key in self._ceilings:
                    return self._ceilings[key]

        # Hard fallback
        if channel == "linkedin":
            return 80
        if channel == "text":
            return 50
        if outreach_mode in ("warm", "referral", "followup"):
            return _EMAIL_FALLBACK_WARM
        return _EMAIL_FALLBACK_COLD

    def check(
        self,
        draft_text: str,
        *,
        channel: str,
        recipient_class: str,
        outreach_mode: str,
    ) -> LengthEnforcementResult:
        """Check draft_text against the resolved ceiling.

        Returns LengthEnforcementResult.
        is_hard_fail=True when word_count > ceiling × tolerance.
        """
        word_count = len(draft_text.split())
        ceiling = self.resolve_ceiling(channel, recipient_class, outreach_mode)
        hard_fail_threshold = int(ceiling * self._tolerance)
        is_compliant = word_count <= ceiling
        is_hard_fail = word_count > hard_fail_threshold

        evidence_ref = (
            f"channel={channel} recipient_class={recipient_class} "
            f"outreach_mode={outreach_mode} "
            f"word_count={word_count} ceiling={ceiling} "
            f"tolerance={self._tolerance} "
            f"hard_fail_threshold={hard_fail_threshold} "
            f"{'HARD_FAIL' if is_hard_fail else 'ADVISORY' if not is_compliant else 'PASS'}"
        )

        return LengthEnforcementResult(
            is_compliant=is_compliant,
            is_hard_fail=is_hard_fail,
            word_count=word_count,
            ceiling=ceiling,
            tolerance=self._tolerance,
            hard_fail_threshold=hard_fail_threshold,
            channel=channel,
            recipient_class=recipient_class,
            outreach_mode=outreach_mode,
            evidence_ref=evidence_ref,
        )
