"""apps_lic Recipient Trigger Engine (SE-P1a).

Evaluates available personalization triggers for an outreach message,
scoped by recipient_class.

Contract
--------
- Decision-only: no provider calls, no retrieval, no state writes, no subprocess.
- NOT universally mandatory — requirements differ by recipient_class.
- Never invents triggers; only validates what is provided.
- Missing triggers → downgrade personalization_mode or require HITL;
  NOT a hard-fail unless omission_policy=fail_closed.

Trigger requirements by recipient_class:
  EXECUTIVE, C_LEVEL, CTO, VP_ENG (cold):
    Require 1-2 person-level or company-strategy triggers where available.
    Missing → downgrade personalization_mode to "company" or "role";
              or if policy=fail_closed → fail.

  HIRING_MANAGER (cold):
    Require at least 1 company/role/project trigger.
    Person-level preferred but not mandatory.

  RECRUITER, SENIOR_TA:
    Allow role, company, hiring-priority triggers.
    Do NOT fail because person-level triggers unavailable.

  REFERRAL_CONTACT:
    Allow relationship-context triggers.
    Person-level optional.

Trigger types:
  person_level          — specific person data (publications, talks, posts, GitHub)
  company_strategy      — public company news, funding, product launches, strategy
  role_context          — JD-derived context, team structure, hiring need
  hiring_priority       — evidence of active hiring posture
  relationship_context  — shared connection, prior interaction, referral chain
  application_context   — current/prior application status

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-canonical-spine-wireup-e7c2a5.md SE-P1a
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Trigger types
# ---------------------------------------------------------------------------

TRIGGER_TYPE_PERSON_LEVEL      = "person_level"
TRIGGER_TYPE_COMPANY_STRATEGY  = "company_strategy"
TRIGGER_TYPE_ROLE_CONTEXT      = "role_context"
TRIGGER_TYPE_HIRING_PRIORITY   = "hiring_priority"
TRIGGER_TYPE_RELATIONSHIP      = "relationship_context"
TRIGGER_TYPE_APPLICATION       = "application_context"

ALL_TRIGGER_TYPES: FrozenSet[str] = frozenset({
    TRIGGER_TYPE_PERSON_LEVEL,
    TRIGGER_TYPE_COMPANY_STRATEGY,
    TRIGGER_TYPE_ROLE_CONTEXT,
    TRIGGER_TYPE_HIRING_PRIORITY,
    TRIGGER_TYPE_RELATIONSHIP,
    TRIGGER_TYPE_APPLICATION,
})

# Recipient class groupings
EXEC_CLASSES      = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})
RECRUITER_CLASSES = frozenset({"RECRUITER", "SENIOR_TA"})

# Minimum triggers required for exec cold
EXEC_COLD_MIN_TRIGGERS = 1


# ---------------------------------------------------------------------------
# Trigger
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RecipientTrigger:
    """A single personalization trigger extracted from the briefing.

    source_ref must be bound to a source_item.uri from the manifest for
    the trigger to count as verified. Unverified triggers are noted in
    the decision but downgraded.
    """

    trigger_type: str           # one of ALL_TRIGGER_TYPES
    description: str            # human-readable label
    source_ref: str             # URI or hash of source; must be non-empty to count
    confidence: float = 1.0     # 0.0–1.0


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TriggerDecision:
    """Decision for a single trigger under the engine's evaluation."""

    trigger: RecipientTrigger
    verdict: str            # "use" | "downgrade" | "omit" | "fail"
    reason: str


@dataclass(frozen=True)
class TriggerEvaluationResult:
    """Full result of recipient trigger evaluation.

    is_satisfied: True when trigger requirements for this recipient_class are met.
    recommended_personalization_mode: downgraded mode if triggers are insufficient.
    hitl_required: True when policy=hitl_required and triggers are insufficient.
    is_fail_closed: True when policy=fail_closed and triggers are insufficient.
    trigger_decisions: one TriggerDecision per input trigger.
    evidence_ref: machine-readable evidence string.
    """

    is_satisfied: bool
    recommended_personalization_mode: str   # "none"|"company"|"role"|"recipient"|"relationship"|"asymmetric"
    hitl_required: bool
    is_fail_closed: bool
    trigger_decisions: Tuple[TriggerDecision, ...]
    evidence_ref: str
    warnings: Tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class RecipientTriggerEngine:
    """Evaluate personalization triggers for an outreach context.

    Usage::

        engine = RecipientTriggerEngine()
        result = engine.evaluate(
            triggers=[
                RecipientTrigger(
                    trigger_type="person_level",
                    description="Recent K8s talk at KubeCon",
                    source_ref="sha256:abc",
                )
            ],
            recipient_class="EXECUTIVE",
            outreach_mode="cold",
            omission_policy="omit_unsupported",
        )
        if result.is_fail_closed:
            # cannot produce draft without triggers
            ...
        elif result.hitl_required:
            # produce draft but escalate to HITL
            ...

    Never invents triggers; only evaluates provided ones.
    """

    def evaluate(
        self,
        *,
        triggers: List[RecipientTrigger],
        recipient_class: str,
        outreach_mode: str,
        omission_policy: str = "omit_unsupported",
    ) -> TriggerEvaluationResult:
        """Evaluate trigger availability for this outreach context.

        Args:
            triggers: Available verified personalization triggers from briefing.
            recipient_class: Target recipient class.
            outreach_mode: "cold"|"warm"|"referral"|"followup"
            omission_policy: "omit_unsupported"|"hitl_required"|"fail_closed"

        Returns:
            TriggerEvaluationResult.
        """
        warnings: List[str] = []
        decisions: List[TriggerDecision] = []

        # Validate and evaluate each trigger
        verified_by_type: Dict[str, List[RecipientTrigger]] = {}
        for t in triggers:
            if t.trigger_type not in ALL_TRIGGER_TYPES:
                decisions.append(TriggerDecision(
                    trigger=t,
                    verdict="omit",
                    reason=f"unknown trigger_type={t.trigger_type!r}",
                ))
                warnings.append(f"unknown trigger_type={t.trigger_type!r} — omitted")
                continue

            if not t.source_ref:
                decisions.append(TriggerDecision(
                    trigger=t,
                    verdict="downgrade",
                    reason="source_ref is empty — trigger cannot be verified; downgraded",
                ))
                warnings.append(f"trigger {t.trigger_type!r} has no source_ref — downgraded")
                continue

            if t.confidence < 0.3:
                decisions.append(TriggerDecision(
                    trigger=t,
                    verdict="omit",
                    reason=f"confidence={t.confidence:.2f} < 0.3 — trigger too weak; omitted",
                ))
                continue

            decisions.append(TriggerDecision(
                trigger=t,
                verdict="use",
                reason=f"verified trigger of type {t.trigger_type!r}; confidence={t.confidence:.2f}",
            ))
            verified_by_type.setdefault(t.trigger_type, []).append(t)

        # Evaluate sufficiency for this recipient_class + outreach_mode
        is_satisfied, mode, miss_reason = self._evaluate_sufficiency(
            verified_by_type=verified_by_type,
            recipient_class=recipient_class,
            outreach_mode=outreach_mode,
        )

        hitl_required = False
        is_fail_closed = False

        if not is_satisfied:
            if omission_policy == "fail_closed":
                is_fail_closed = True
            elif omission_policy == "hitl_required":
                hitl_required = True
            # "omit_unsupported" → just downgrade mode silently

        evidence_ref = (
            f"recipient_class={recipient_class} outreach_mode={outreach_mode} "
            f"omission_policy={omission_policy} "
            f"triggers_provided={len(triggers)} "
            f"verified_types={sorted(verified_by_type.keys())} "
            f"is_satisfied={is_satisfied} "
            f"recommended_mode={mode} "
            f"hitl_required={hitl_required} "
            f"fail_closed={is_fail_closed}"
        )
        if miss_reason:
            evidence_ref += f" miss_reason={miss_reason!r}"

        return TriggerEvaluationResult(
            is_satisfied=is_satisfied,
            recommended_personalization_mode=mode,
            hitl_required=hitl_required,
            is_fail_closed=is_fail_closed,
            trigger_decisions=tuple(decisions),
            evidence_ref=evidence_ref,
            warnings=tuple(warnings),
        )

    # ------------------------------------------------------------------
    # Sufficiency evaluation
    # ------------------------------------------------------------------

    def _evaluate_sufficiency(
        self,
        *,
        verified_by_type: Dict[str, List[RecipientTrigger]],
        recipient_class: str,
        outreach_mode: str,
    ) -> Tuple[bool, str, str]:
        """Return (is_satisfied, recommended_personalization_mode, miss_reason)."""

        if outreach_mode == "followup":
            # Followup never requires triggers — brevity-first
            return True, "none", ""

        if outreach_mode == "referral":
            # Referral: relationship context preferred; fallback to company/role
            if TRIGGER_TYPE_RELATIONSHIP in verified_by_type:
                return True, "relationship", ""
            if verified_by_type:
                return True, "company", ""
            return True, "none", ""  # referral can work without triggers

        if recipient_class in EXEC_CLASSES and outreach_mode == "cold":
            # Require ≥1 person_level OR company_strategy trigger
            high_quality = (
                verified_by_type.get(TRIGGER_TYPE_PERSON_LEVEL, []) +
                verified_by_type.get(TRIGGER_TYPE_COMPANY_STRATEGY, [])
            )
            if len(high_quality) >= EXEC_COLD_MIN_TRIGGERS:
                mode = "recipient" if verified_by_type.get(TRIGGER_TYPE_PERSON_LEVEL) else "company"
                return True, mode, ""
            # Insufficient: downgrade
            if verified_by_type:
                return False, "company", (
                    f"exec cold requires ≥{EXEC_COLD_MIN_TRIGGERS} "
                    f"person_level or company_strategy trigger; "
                    f"only found: {sorted(verified_by_type.keys())}"
                )
            return False, "role", (
                f"exec cold requires ≥{EXEC_COLD_MIN_TRIGGERS} "
                "person_level or company_strategy trigger; none found"
            )

        if recipient_class in EXEC_CLASSES:  # warm / other modes
            if verified_by_type:
                best = "recipient" if TRIGGER_TYPE_PERSON_LEVEL in verified_by_type else "company"
                return True, best, ""
            return True, "role", ""

        if recipient_class == "HIRING_MANAGER" and outreach_mode == "cold":
            allowed = {
                TRIGGER_TYPE_COMPANY_STRATEGY,
                TRIGGER_TYPE_ROLE_CONTEXT,
                TRIGGER_TYPE_PERSON_LEVEL,
                TRIGGER_TYPE_HIRING_PRIORITY,
            }
            if any(t in verified_by_type for t in allowed):
                mode = "recipient" if TRIGGER_TYPE_PERSON_LEVEL in verified_by_type else "company"
                return True, mode, ""
            return False, "role", "HIRING_MANAGER cold: no company/role/person trigger found"

        if recipient_class in RECRUITER_CLASSES:
            # Recruiters: any trigger accepted; no person-level requirement
            if verified_by_type:
                return True, "company", ""
            return True, "none", ""  # recruiters fine without personalization

        if recipient_class == "REFERRAL_CONTACT":
            if TRIGGER_TYPE_RELATIONSHIP in verified_by_type:
                return True, "relationship", ""
            if verified_by_type:
                return True, "company", ""
            return True, "none", ""

        # Unknown recipient class — allow but advisory
        return True, "none", f"unknown recipient_class={recipient_class!r}"
