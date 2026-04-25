"""First Safety / Authority Reading — v5 doctrine § PARSE INTENT [end].

Doctrine reference: ``02_L1_Reasoning_Plan_Generation_v5.md``
``§ FIRST SAFETY / AUTHORITY READING`` (10-question gate that runs after
intent parsing, before plan drafting).

Decoupled from the plan validators because this is an *intent-only* check —
it does not need the plan, only the parsed :class:`IntentFrame`. It produces
a :class:`FirstSafetyReading` that the planner can read to bias the route hint
toward refusal / safe-redirect / direct-conversation when appropriate.

Hard invariant: the reading is heuristic; it never overrides validation.
Downstream V2 (``is_it_safe``) remains the structural authority.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L1_cognition.types.intent_frame_types import (
    ActionRequirement,
    IntentFrame,
    OutputTargetKind,
    WorkClass,
)

__all__ = [
    "FirstSafetyReading",
    "first_safety_reading",
]


# ----------------------------------------------------------------------
# Heuristic detection tables.
# ----------------------------------------------------------------------

# Prompt-injection canaries: phrases that try to override system authority
# from inside a user-provided document, retrieved snippet, or quoted block.
_INJECTION_CANARIES: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bignore (the |all |previous )?(instructions|rules|system prompt)\b", re.IGNORECASE),
    re.compile(r"\bdisregard (the |all )?(prior|previous|above) (instructions|rules)\b", re.IGNORECASE),
    re.compile(r"\boverride (the |all )?(system|safety|policy|guardrails?)\b", re.IGNORECASE),
    re.compile(r"\byou are now (a|an) (?!helpful)", re.IGNORECASE),  # role-override
    re.compile(r"\bnew instructions:\s", re.IGNORECASE),
    re.compile(r"\bdeveloper mode\b|\bdan mode\b|\bjailbreak\b", re.IGNORECASE),
    re.compile(r"\b(act|behave|pretend) as (if you are |a |an )(?!helpful)", re.IGNORECASE),
    re.compile(r"\bforget (everything|all|the prior)\b", re.IGNORECASE),
)

# Tokens that suggest the user is requesting something the system MUST refuse.
_REFUSAL_TRIGGERS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(make|create|generate)( me)? (a |an )?(bomb|weapon|explosive|malware|virus|exploit|ransomware)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bhow (do i|to) (kill|murder|harm|stalk|dox)\b", re.IGNORECASE),
    re.compile(r"\b(hack|breach|crack|bypass) (into )?(?!my own)\b", re.IGNORECASE),
    re.compile(r"\bchild (sexual|pornographic|exploitation)\b", re.IGNORECASE),
)

# Soft authority-override tokens that should bias toward safe redirect, not refusal.
_SAFE_REDIRECT_TRIGGERS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdiagnose (my|her|his|their) (illness|disease|condition)\b", re.IGNORECASE),
    re.compile(r"\b(legal|medical|financial) advice\b", re.IGNORECASE),
    re.compile(r"\bguarantee (i|you) (will|can)\b", re.IGNORECASE),
)

_HITL_TRIGGER_TOKENS: frozenset[str] = frozenset(
    {
        "production",
        "customer database",
        "send to all",
        "broadcast",
        "wire transfer",
        "delete all",
        "drop database",
        "merge to main",
        "force push",
        "deploy",
        "publish live",
    }
)

_UWG_TRIGGER_TOKENS: frozenset[str] = frozenset(
    {
        "commit",
        "merge",
        "save permanently",
        "persist",
        "write to disk",
        "write to db",
        "write to database",
        "store permanently",
        "publish",
    }
)


# ----------------------------------------------------------------------
# Reading record.
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class FirstSafetyReading:
    """v5 § FIRST SAFETY / AUTHORITY READING — structured 10-question result.

    Each field maps 1:1 to a question in the doctrine box. ``True`` = the
    user-visible request matches that signal. The planner reads this as
    advisory bias; final disposition is decided by V1-V5 validators.
    """

    request_id: str
    is_read_only: bool = False  # Q1: read-only response?
    is_reversible_action: bool = False  # Q2: reversible action?
    is_durable_write: bool = False  # Q3: durable write?
    has_external_side_effects: bool = False  # Q4: external side effects?
    attempts_authority_override: bool = False  # Q5: tries to override system/policy/safety?
    has_prompt_injection_signal: bool = False  # Q6: hidden prompt-injection in quoted/retrieved text?
    requires_hitl_later: bool = False  # Q7: HITL later?
    requires_uwg_later: bool = False  # Q8: UWG later?
    recommend_refusal: bool = False  # Q9 (a): direct refusal warranted?
    recommend_safe_redirect: bool = False  # Q9 (b): safe redirect warranted?
    safest_is_direct_conversation: bool = False  # Q10: safest answer is direct, no workflow?

    # Contextual evidence — short, deterministic strings the validator can cite.
    triggers: tuple[str, ...] = field(default_factory=tuple)

    def has_any_safety_concern(self) -> bool:
        return (
            self.attempts_authority_override
            or self.has_prompt_injection_signal
            or self.recommend_refusal
            or self.recommend_safe_redirect
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "is_read_only": self.is_read_only,
            "is_reversible_action": self.is_reversible_action,
            "is_durable_write": self.is_durable_write,
            "has_external_side_effects": self.has_external_side_effects,
            "attempts_authority_override": self.attempts_authority_override,
            "has_prompt_injection_signal": self.has_prompt_injection_signal,
            "requires_hitl_later": self.requires_hitl_later,
            "requires_uwg_later": self.requires_uwg_later,
            "recommend_refusal": self.recommend_refusal,
            "recommend_safe_redirect": self.recommend_safe_redirect,
            "safest_is_direct_conversation": self.safest_is_direct_conversation,
            "triggers": list(self.triggers),
        }


# ----------------------------------------------------------------------
# Producer.
# ----------------------------------------------------------------------


def _scan_patterns(patterns: tuple[re.Pattern[str], ...], text: str) -> tuple[str, ...]:
    """Return the literal trigger phrases that fired (for evidence trail)."""
    hits: list[str] = []
    for p in patterns:
        m = p.search(text)
        if m:
            hits.append(m.group(0))
    return tuple(hits)


def _scan_token_set(tokens: frozenset[str], text: str) -> tuple[str, ...]:
    """Return matching tokens (case-insensitive substring) preserving order."""
    lowered = text.lower()
    return tuple(t for t in tokens if t in lowered)


def first_safety_reading(
    intent: IntentFrame,
    *,
    request_text: str = "",
) -> FirstSafetyReading:
    """Run the v5 § FIRST SAFETY / AUTHORITY READING gate over an IntentFrame.

    Args:
        intent: Validated IntentFrame from :func:`parse_intent`.
        request_text: Optional raw user text used for stronger pattern hits
            (the IntentFrame already carries goal + constraint sentences,
            but the original text may contain additional context the
            normalizer dropped).

    Returns:
        A :class:`FirstSafetyReading` record. The reading is *advisory*: it
        biases planner behavior but never auto-rejects a plan. Final
        rejection authority lives in the V2 (`is_it_safe`) validator.
    """
    if not isinstance(intent, IntentFrame):
        raise TypeError("intent must be IntentFrame")

    # Prefer the raw request when given; otherwise fall back to a synthetic
    # text built from the intent surface so the heuristics still have signal.
    text = request_text or " ".join(
        [
            intent.goal,
            intent.success_condition,
            *(c.statement for c in intent.constraints),
            *intent.details,
        ]
    )

    triggers: list[str] = []

    # Q5: authority-override attempts — direct keyword hits.
    inj_hits = _scan_patterns(_INJECTION_CANARIES, text)
    has_injection = bool(inj_hits)
    triggers.extend(f"injection:{h.lower()}" for h in inj_hits)

    # Q6: same canaries also flag prompt-injection signal — they often appear
    # in retrieved/quoted content. Caller supplies request_text=quoted_block
    # to differentiate "user wrote it" vs "retrieved-source contained it".
    has_authority_override = has_injection

    # Q9 (a): hard-refusal triggers.
    refusal_hits = _scan_patterns(_REFUSAL_TRIGGERS, text)
    recommend_refusal = bool(refusal_hits)
    triggers.extend(f"refusal:{h.lower()}" for h in refusal_hits)

    # Q9 (b): safe-redirect triggers (medical/legal/financial advice).
    redirect_hits = _scan_patterns(_SAFE_REDIRECT_TRIGGERS, text)
    recommend_safe_redirect = bool(redirect_hits) and not recommend_refusal
    triggers.extend(f"redirect:{h.lower()}" for h in redirect_hits)

    # Q1-Q4: derive from the parsed intent's action_requirement.
    is_read_only = intent.action_requirement in (
        ActionRequirement.NONE,
        ActionRequirement.READ_ONLY,
    )
    is_reversible_action = intent.action_requirement == ActionRequirement.REVERSIBLE
    is_durable_write = intent.action_requirement == ActionRequirement.WRITE_PROPOSAL
    has_external_side_effects = intent.action_requirement == ActionRequirement.HIGH_IMPACT

    # Q7: HITL trigger — high-impact action OR keyword match.
    hitl_keyword_hits = _scan_token_set(_HITL_TRIGGER_TOKENS, text)
    requires_hitl_later = has_external_side_effects or intent.high_risk or bool(hitl_keyword_hits)
    triggers.extend(f"hitl:{h}" for h in hitl_keyword_hits)

    # Q8: UWG trigger — durable write OR keyword match.
    uwg_keyword_hits = _scan_token_set(_UWG_TRIGGER_TOKENS, text)
    requires_uwg_later = is_durable_write or bool(uwg_keyword_hits)
    triggers.extend(f"uwg:{h}" for h in uwg_keyword_hits)

    # Q10: safest = direct conversation if everything below holds:
    #   • the work class is conversational (summarize/explain/compare)
    #   • the action requirement is NONE or READ_ONLY
    #   • no refusal / redirect / injection triggers
    #   • output kind is ANSWER
    safest_is_direct_conversation = (
        is_read_only
        and intent.work_class
        in (WorkClass.SUMMARIZE, WorkClass.COMPARE, WorkClass.ANALYZE, WorkClass.FACTUAL)
        and intent.output_target_kind == OutputTargetKind.ANSWER
        and not (recommend_refusal or recommend_safe_redirect or has_injection)
        and not requires_hitl_later
        and not requires_uwg_later
    )

    return FirstSafetyReading(
        request_id=intent.request_id,
        is_read_only=is_read_only,
        is_reversible_action=is_reversible_action,
        is_durable_write=is_durable_write,
        has_external_side_effects=has_external_side_effects,
        attempts_authority_override=has_authority_override,
        has_prompt_injection_signal=has_injection,
        requires_hitl_later=requires_hitl_later,
        requires_uwg_later=requires_uwg_later,
        recommend_refusal=recommend_refusal,
        recommend_safe_redirect=recommend_safe_redirect,
        safest_is_direct_conversation=safest_is_direct_conversation,
        triggers=tuple(triggers),
    )
