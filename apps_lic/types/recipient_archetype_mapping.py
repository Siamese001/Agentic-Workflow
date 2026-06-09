"""Canonical LIC recipient-class to prompt-archetype mapping.

The C0 recipient classifier may emit granular classes such as CEO, CTO, or
VP_ENG. Prompt Assembly intentionally keeps only four writing archetypes so
template behavior stays bounded and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from apps_lic.engines.recipient_classification import (
    CLASS_CEO,
    CLASS_CTO,
    CLASS_C_LEVEL,
    CLASS_EXECUTIVE,
    CLASS_HIRING_MANAGER,
    CLASS_RECRUITER,
    CLASS_REFERRAL_CONTACT,
    CLASS_SENIOR_TA,
    CLASS_UNKNOWN,
    CLASS_VP_ENG,
)
from apps_lic.types.linkedin_route_envelope import (
    CHANNEL_LINKEDIN_CHAT,
    CHANNEL_LINKEDIN_INMAIL,
    CONNECTION_REQUEST_CHAR_CAP,
    INMAIL_BODY_CHAR_CAP,
)


ARCHETYPE_RECRUITER = "RECRUITER"
ARCHETYPE_SENIOR_TA = "SENIOR_TA"
ARCHETYPE_EXECUTIVE = "EXECUTIVE"
ARCHETYPE_C_LEVEL = "C_LEVEL"

CANONICAL_RECIPIENT_ARCHETYPES: tuple[str, ...] = (
    ARCHETYPE_RECRUITER,
    ARCHETYPE_SENIOR_TA,
    ARCHETYPE_EXECUTIVE,
    ARCHETYPE_C_LEVEL,
)

LIC_RECIPIENT_CLASS_TO_ARCHETYPE: dict[str, str] = {
    CLASS_RECRUITER: ARCHETYPE_RECRUITER,
    CLASS_REFERRAL_CONTACT: ARCHETYPE_RECRUITER,
    CLASS_SENIOR_TA: ARCHETYPE_SENIOR_TA,
    CLASS_HIRING_MANAGER: ARCHETYPE_EXECUTIVE,
    CLASS_EXECUTIVE: ARCHETYPE_EXECUTIVE,
    CLASS_VP_ENG: ARCHETYPE_EXECUTIVE,
    CLASS_C_LEVEL: ARCHETYPE_C_LEVEL,
    CLASS_CEO: ARCHETYPE_C_LEVEL,
    CLASS_CTO: ARCHETYPE_C_LEVEL,
}

_RECIPIENT_CLASS_ALIASES: dict[str, str] = {
    "C-LEVEL": CLASS_C_LEVEL,
    "C LEVEL": CLASS_C_LEVEL,
    "C SUITE": CLASS_C_LEVEL,
    "C-SUITE": CLASS_C_LEVEL,
    "CEO": CLASS_CEO,
    "CHIEF EXECUTIVE OFFICER": CLASS_CEO,
    "CTO": CLASS_CTO,
    "CHIEF TECHNOLOGY OFFICER": CLASS_CTO,
    "VP ENG": CLASS_VP_ENG,
    "VP ENGINEERING": CLASS_VP_ENG,
    "VP_ENG": CLASS_VP_ENG,
    "SENIOR TA": CLASS_SENIOR_TA,
    "SENIOR_TA": CLASS_SENIOR_TA,
}


@dataclass(frozen=True)
class RecipientArchetypePromptProfile:
    archetype: str
    template_id: str
    altitude: str
    style: str
    fact_grounding: str
    focus: str
    cta: str
    advisory_word_range: tuple[int, int]
    recommended_sentence_range: tuple[int, int]
    recommended_hard_cap_chars: int

    def to_hash_payload(self) -> dict[str, Any]:
        return {
            "archetype": self.archetype,
            "template_id": self.template_id,
            "altitude": self.altitude,
            "style": self.style,
            "fact_grounding": self.fact_grounding,
            "focus": self.focus,
            "cta": self.cta,
            "advisory_word_range": list(self.advisory_word_range),
            "recommended_sentence_range": list(self.recommended_sentence_range),
            "recommended_hard_cap_chars": self.recommended_hard_cap_chars,
        }


@dataclass(frozen=True)
class TemplateLengthPolicy:
    budget_key: str
    min_words: int
    max_words: int
    min_sentences: int
    max_sentences: int
    hard_cap_chars: int
    channel: str
    route_family: str
    subject_required: bool
    signature_required: bool
    cta_style: str

    def to_length_budget_packet(self) -> dict[str, Any]:
        return {
            "budget_key": self.budget_key,
            "min_words": self.min_words,
            "max_words": self.max_words,
            "min_sentences": self.min_sentences,
            "max_sentences": self.max_sentences,
            "hard_cap_chars": self.hard_cap_chars,
            "hard_controls": ["max_sentences", "hard_cap_chars"],
            "advisory_controls": ["min_words", "max_words"],
            "channel": self.channel,
            "route_family": self.route_family,
            "subject_required": self.subject_required,
            "signature_required": self.signature_required,
            "cta_style": self.cta_style,
        }


@dataclass(frozen=True)
class RecipientTemplatePolicy:
    archetype_profile: RecipientArchetypePromptProfile
    length_policy: TemplateLengthPolicy

    def to_hash_payload(self) -> dict[str, Any]:
        return {
            "archetype_profile": self.archetype_profile.to_hash_payload(),
            "length_policy": self.length_policy.to_length_budget_packet(),
        }


ARCHETYPE_PROMPT_PROFILES: dict[str, RecipientArchetypePromptProfile] = {
    ARCHETYPE_RECRUITER: RecipientArchetypePromptProfile(
        archetype=ARCHETYPE_RECRUITER,
        template_id="apps_lic.recipient_archetype.recruiter.v1",
        altitude="role-fit and screening logistics",
        style="direct, credential-forward, scannable, low ornament",
        fact_grounding=(
            "Use JD and sender proof first; avoid strategic company claims unless "
            "C0/C0.3 supplied them."
        ),
        focus="role match, relevant proof, resume review or short screen",
        cta="Ask for a resume review, fit check, or short recruiting screen.",
        advisory_word_range=(45, 80),
        recommended_sentence_range=(2, 4),
        recommended_hard_cap_chars=750,
    ),
    ARCHETYPE_SENIOR_TA: RecipientArchetypePromptProfile(
        archetype=ARCHETYPE_SENIOR_TA,
        template_id="apps_lic.recipient_archetype.senior_ta.v1",
        altitude="hiring-system and talent-strategy fit",
        style="concise, senior recruiting-aware, evidence-led",
        fact_grounding=(
            "Connect proof to hiring priorities, requisition quality, or talent "
            "pipeline signals only when supplied."
        ),
        focus="quality-of-fit, team hiring context, differentiated proof",
        cta="Ask for a fit review or brief calibration against the team need.",
        advisory_word_range=(45, 75),
        recommended_sentence_range=(2, 4),
        recommended_hard_cap_chars=700,
    ),
    ARCHETYPE_EXECUTIVE: RecipientArchetypePromptProfile(
        archetype=ARCHETYPE_EXECUTIVE,
        template_id="apps_lic.recipient_archetype.executive.v1",
        altitude="operating mandate and team outcomes",
        style="peer-professional, crisp, operationally credible",
        fact_grounding=(
            "Use one concrete company, role, or proof signal; do not overstate "
            "relationship, mandate, or business impact."
        ),
        focus="why this proof matters to their organization or role ownership",
        cta="Ask for a low-friction exchange, redirect, or fit signal.",
        advisory_word_range=(35, 70),
        recommended_sentence_range=(2, 3),
        recommended_hard_cap_chars=600,
    ),
    ARCHETYPE_C_LEVEL: RecipientArchetypePromptProfile(
        archetype=ARCHETYPE_C_LEVEL,
        template_id="apps_lic.recipient_archetype.c_level.v1",
        altitude="enterprise strategy and executive priorities",
        style="strategic, spare, high-confidence, no tactical sprawl",
        fact_grounding=(
            "Use only verified strategic triggers and proof; CEO, CTO, and C-level "
            "drafts require the most conservative claims."
        ),
        focus="strategic relevance, governed proof, and a respectful executive ask",
        cta="Ask for a brief executive exchange or the right owner to speak with.",
        advisory_word_range=(30, 60),
        recommended_sentence_range=(2, 3),
        recommended_hard_cap_chars=550,
    ),
}


_INMAIL_LENGTH_POLICIES: dict[tuple[str, str], tuple[str, int, int, int, int]] = {
    (ARCHETYPE_RECRUITER, "role_specific"): ("recruiter_role_specific_inmail", 95, 145, 5, 7),
    (ARCHETYPE_SENIOR_TA, "role_specific"): ("senior_ta_role_specific_inmail", 90, 140, 5, 7),
    (ARCHETYPE_C_LEVEL, "role_specific"): ("c_level_role_specific_inmail", 75, 120, 4, 6),
    (ARCHETYPE_EXECUTIVE, "role_specific"): ("executive_role_specific_inmail", 85, 130, 4, 6),
    (ARCHETYPE_RECRUITER, "trigger_based_insight"): ("recruiter_trigger_inmail", 85, 130, 4, 6),
    (ARCHETYPE_SENIOR_TA, "trigger_based_insight"): ("senior_ta_trigger_inmail", 80, 125, 4, 6),
    (ARCHETYPE_C_LEVEL, "trigger_based_insight"): ("c_level_trigger_inmail", 75, 120, 4, 6),
    (ARCHETYPE_EXECUTIVE, "trigger_based_insight"): ("executive_trigger_inmail", 80, 130, 4, 6),
    (ARCHETYPE_RECRUITER, "referral_ask"): ("referral_ask_inmail", 85, 130, 4, 6),
    (ARCHETYPE_SENIOR_TA, "referral_ask"): ("referral_ask_inmail", 85, 130, 4, 6),
    (ARCHETYPE_EXECUTIVE, "referral_ask"): ("referral_ask_inmail", 85, 130, 4, 6),
    (ARCHETYPE_C_LEVEL, "referral_ask"): ("referral_ask_inmail", 85, 130, 4, 6),
    (ARCHETYPE_RECRUITER, "follow_up"): ("follow_up_inmail", 70, 115, 3, 5),
    (ARCHETYPE_SENIOR_TA, "follow_up"): ("follow_up_inmail", 70, 115, 3, 5),
    (ARCHETYPE_EXECUTIVE, "follow_up"): ("follow_up_inmail", 70, 115, 3, 5),
    (ARCHETYPE_C_LEVEL, "follow_up"): ("follow_up_inmail", 70, 115, 3, 5),
    (ARCHETYPE_RECRUITER, "general_intro"): ("recruiter_general_intro_inmail", 85, 130, 4, 6),
    (ARCHETYPE_SENIOR_TA, "general_intro"): ("senior_ta_general_intro_inmail", 80, 125, 4, 6),
    (ARCHETYPE_EXECUTIVE, "general_intro"): ("executive_general_intro_inmail", 75, 120, 4, 6),
    (ARCHETYPE_C_LEVEL, "general_intro"): ("c_level_general_intro_inmail", 70, 115, 4, 6),
}

_STANDARD_LENGTH_POLICIES: dict[tuple[str, str], tuple[str, int, int, int, int, int]] = {
    (ARCHETYPE_RECRUITER, "role_specific"): ("recruiter_role_specific", 55, 80, 3, 4, 750),
    (ARCHETYPE_SENIOR_TA, "role_specific"): ("senior_ta_role_specific", 50, 75, 3, 4, 700),
    (ARCHETYPE_C_LEVEL, "role_specific"): ("c_level_role_specific", 35, 60, 2, 3, 550),
    (ARCHETYPE_EXECUTIVE, "role_specific"): ("executive_role_specific", 45, 70, 3, 4, 700),
    (ARCHETYPE_RECRUITER, "trigger_based_insight"): ("executive_trigger", 35, 60, 2, 3, 550),
    (ARCHETYPE_SENIOR_TA, "trigger_based_insight"): ("executive_trigger", 35, 60, 2, 3, 550),
    (ARCHETYPE_EXECUTIVE, "trigger_based_insight"): ("executive_trigger", 35, 60, 2, 3, 550),
    (ARCHETYPE_C_LEVEL, "trigger_based_insight"): ("executive_trigger", 35, 60, 2, 3, 550),
    (ARCHETYPE_RECRUITER, "referral_ask"): ("referral_ask", 50, 75, 3, 4, 700),
    (ARCHETYPE_SENIOR_TA, "referral_ask"): ("referral_ask", 50, 75, 3, 4, 700),
    (ARCHETYPE_EXECUTIVE, "referral_ask"): ("referral_ask", 50, 75, 3, 4, 700),
    (ARCHETYPE_C_LEVEL, "referral_ask"): ("referral_ask", 50, 75, 3, 4, 700),
    (ARCHETYPE_RECRUITER, "follow_up"): ("follow_up_short", 25, 45, 1, 2, 400),
    (ARCHETYPE_SENIOR_TA, "follow_up"): ("follow_up_short", 25, 45, 1, 2, 400),
    (ARCHETYPE_EXECUTIVE, "follow_up"): ("follow_up_short", 25, 45, 1, 2, 400),
    (ARCHETYPE_C_LEVEL, "follow_up"): ("follow_up_short", 25, 45, 1, 2, 400),
    (ARCHETYPE_RECRUITER, "general_intro"): ("recruiter_general_intro", 40, 60, 2, 3, 500),
    (ARCHETYPE_SENIOR_TA, "general_intro"): ("senior_ta_general_intro", 35, 60, 2, 3, 500),
    (ARCHETYPE_EXECUTIVE, "general_intro"): ("executive_general_intro", 35, 55, 2, 3, 500),
    (ARCHETYPE_C_LEVEL, "general_intro"): ("c_level_general_intro", 30, 55, 2, 3, 500),
}


def _normalize_message_type(message_type: str) -> str:
    normalized = str(message_type or "").strip().lower()
    return normalized or "general_intro"


def _normalize_channel(channel: str) -> str:
    return str(channel or "").strip().lower()


def resolve_recipient_template_policy(
    *,
    recipient_class: str,
    message_type: str,
    channel: str = "linkedin",
    modifiers: Mapping[str, bool] | None = None,
) -> RecipientTemplatePolicy:
    archetype = map_lic_recipient_class_to_archetype(recipient_class)
    profile = ARCHETYPE_PROMPT_PROFILES[archetype]
    normalized_message = _normalize_message_type(message_type)
    normalized_channel = _normalize_channel(channel)
    modifier_map = dict(modifiers or {})

    if normalized_channel == CHANNEL_LINKEDIN_CHAT:
        length = TemplateLengthPolicy(
            budget_key="linkedin_chat_connection_request",
            min_words=25,
            max_words=45,
            min_sentences=1,
            max_sentences=2,
            hard_cap_chars=CONNECTION_REQUEST_CHAR_CAP,
            channel=CHANNEL_LINKEDIN_CHAT,
            route_family="CONNECTION_REQ",
            subject_required=False,
            signature_required=False,
            cta_style="micro",
        )
    elif normalized_channel == CHANNEL_LINKEDIN_INMAIL:
        key, min_words, max_words, min_sentences, max_sentences = _INMAIL_LENGTH_POLICIES[
            (archetype, normalized_message)
        ]
        length = TemplateLengthPolicy(
            budget_key=key,
            min_words=min_words,
            max_words=max_words,
            min_sentences=min_sentences,
            max_sentences=max_sentences,
            hard_cap_chars=INMAIL_BODY_CHAR_CAP,
            channel=CHANNEL_LINKEDIN_INMAIL,
            route_family="INMAIL",
            subject_required=True,
            signature_required=True,
            cta_style=profile.cta,
        )
    else:
        if normalized_message == "follow_up" and (
            modifier_map.get("uses_jd") or modifier_map.get("application_status_claimed")
        ):
            raw = ("follow_up_role_or_status", 35, 60, 2, 3, 600)
        else:
            raw = _STANDARD_LENGTH_POLICIES[(archetype, normalized_message)]
        key, min_words, max_words, min_sentences, max_sentences, hard_cap = raw
        length = TemplateLengthPolicy(
            budget_key=key,
            min_words=min_words,
            max_words=max_words,
            min_sentences=min_sentences,
            max_sentences=max_sentences,
            hard_cap_chars=hard_cap,
            channel="linkedin",
            route_family="LINKEDIN_DRAFT",
            subject_required=False,
            signature_required=True,
            cta_style=profile.cta,
        )
    return RecipientTemplatePolicy(archetype_profile=profile, length_policy=length)


def normalize_lic_recipient_class(recipient_class: str) -> str:
    normalized = " ".join(str(recipient_class or "").strip().upper().split())
    normalized = _RECIPIENT_CLASS_ALIASES.get(normalized, normalized.replace("-", "_"))
    if normalized == CLASS_UNKNOWN:
        raise ValueError("UNKNOWN recipient class is not targetable for PA archetype mapping")
    return normalized


def map_lic_recipient_class_to_archetype(recipient_class: str) -> str:
    normalized = normalize_lic_recipient_class(recipient_class)
    try:
        return LIC_RECIPIENT_CLASS_TO_ARCHETYPE[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported LIC recipient class for archetype mapping: {recipient_class!r}"
        ) from exc


def recipient_archetype_profile(
    recipient_class_or_archetype: str,
) -> RecipientArchetypePromptProfile:
    normalized = normalize_lic_recipient_class(recipient_class_or_archetype)
    archetype = (
        normalized
        if normalized in CANONICAL_RECIPIENT_ARCHETYPES
        else map_lic_recipient_class_to_archetype(normalized)
    )
    return ARCHETYPE_PROMPT_PROFILES[archetype]


def build_archetype_prompt_lines(
    *,
    lic_recipient_class: str,
    profile: RecipientArchetypePromptProfile,
    length_budget: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    budget = dict(length_budget or {})
    max_sentences = int(
        budget.get("max_sentences") or profile.recommended_sentence_range[1]
    )
    hard_cap_chars = int(
        budget.get("hard_cap_chars") or profile.recommended_hard_cap_chars
    )
    min_words = int(budget.get("min_words") or profile.advisory_word_range[0])
    max_words = int(budget.get("max_words") or profile.advisory_word_range[1])
    return (
        "RECIPIENT ARCHETYPE TEMPLATE:",
        f"  - LIC recipient class: {normalize_lic_recipient_class(lic_recipient_class)}.",
        f"  - Mapped archetype: {profile.archetype}.",
        f"  - Archetype template id: {profile.template_id}.",
        f"  - Altitude: {profile.altitude}.",
        f"  - Style: {profile.style}.",
        f"  - Focus: {profile.focus}.",
        f"  - Fact grounding: {profile.fact_grounding}",
        f"  - CTA: {profile.cta}",
        (
            "  - Length controls: hard controls are "
            f"max {max_sentences} sentences and max {hard_cap_chars} characters; "
            f"the {min_words}-{max_words} word band is advisory only."
        ),
        (
            "  - Do not optimize for exact word count; tokenizers split text into "
            "character sequences, so sentence count and character cap are the stable controls."
        ),
    )


__all__ = [
    "ARCHETYPE_C_LEVEL",
    "ARCHETYPE_EXECUTIVE",
    "ARCHETYPE_PROMPT_PROFILES",
    "ARCHETYPE_RECRUITER",
    "ARCHETYPE_SENIOR_TA",
    "CANONICAL_RECIPIENT_ARCHETYPES",
    "LIC_RECIPIENT_CLASS_TO_ARCHETYPE",
    "RecipientArchetypePromptProfile",
    "RecipientTemplatePolicy",
    "TemplateLengthPolicy",
    "build_archetype_prompt_lines",
    "map_lic_recipient_class_to_archetype",
    "normalize_lic_recipient_class",
    "recipient_archetype_profile",
    "resolve_recipient_template_policy",
]
