from __future__ import annotations

import pytest

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
from apps_lic.types.recipient_archetype_mapping import (
    ARCHETYPE_C_LEVEL,
    ARCHETYPE_EXECUTIVE,
    ARCHETYPE_PROMPT_PROFILES,
    ARCHETYPE_RECRUITER,
    ARCHETYPE_SENIOR_TA,
    CANONICAL_RECIPIENT_ARCHETYPES,
    map_lic_recipient_class_to_archetype,
    recipient_archetype_profile,
    resolve_recipient_template_policy,
)
from apps_lic.types.linkedin_route_envelope import (
    CHANNEL_LINKEDIN_CHAT,
    CHANNEL_LINKEDIN_INMAIL,
    CONNECTION_REQUEST_CHAR_CAP,
    INMAIL_BODY_CHAR_CAP,
)


def test_lic_prompt_archetypes_stay_capped_at_four() -> None:
    assert CANONICAL_RECIPIENT_ARCHETYPES == (
        ARCHETYPE_RECRUITER,
        ARCHETYPE_SENIOR_TA,
        ARCHETYPE_EXECUTIVE,
        ARCHETYPE_C_LEVEL,
    )
    assert set(ARCHETYPE_PROMPT_PROFILES) == set(CANONICAL_RECIPIENT_ARCHETYPES)


@pytest.mark.parametrize(
    ("recipient_class", "expected_archetype"),
    (
        (CLASS_RECRUITER, ARCHETYPE_RECRUITER),
        (CLASS_REFERRAL_CONTACT, ARCHETYPE_RECRUITER),
        (CLASS_SENIOR_TA, ARCHETYPE_SENIOR_TA),
        (CLASS_HIRING_MANAGER, ARCHETYPE_EXECUTIVE),
        (CLASS_EXECUTIVE, ARCHETYPE_EXECUTIVE),
        (CLASS_VP_ENG, ARCHETYPE_EXECUTIVE),
        (CLASS_C_LEVEL, ARCHETYPE_C_LEVEL),
        (CLASS_CEO, ARCHETYPE_C_LEVEL),
        (CLASS_CTO, ARCHETYPE_C_LEVEL),
    ),
)
def test_lic_recipient_classes_map_to_four_prompt_archetypes(
    recipient_class: str,
    expected_archetype: str,
) -> None:
    assert map_lic_recipient_class_to_archetype(recipient_class) == expected_archetype


def test_ceo_title_alias_maps_to_c_level_profile() -> None:
    profile = recipient_archetype_profile("Chief Executive Officer")

    assert profile.archetype == ARCHETYPE_C_LEVEL
    assert profile.template_id == "apps_lic.recipient_archetype.c_level.v1"
    assert profile.recommended_sentence_range[1] == 3


def test_unknown_recipient_class_is_not_targetable_for_prompt_archetypes() -> None:
    with pytest.raises(ValueError, match="UNKNOWN recipient class"):
        map_lic_recipient_class_to_archetype(CLASS_UNKNOWN)


def test_w5_template_policy_resolves_inmail_budget_and_route_subject_rules() -> None:
    policy = resolve_recipient_template_policy(
        recipient_class=CLASS_CEO,
        message_type="trigger_based_insight",
        channel=CHANNEL_LINKEDIN_INMAIL,
    )
    packet = policy.length_policy.to_length_budget_packet()

    assert policy.archetype_profile.archetype == ARCHETYPE_C_LEVEL
    assert packet["budget_key"] == "c_level_trigger_inmail"
    assert packet["hard_cap_chars"] == INMAIL_BODY_CHAR_CAP
    assert packet["channel"] == CHANNEL_LINKEDIN_INMAIL
    assert packet["route_family"] == "INMAIL"
    assert packet["subject_required"] is True
    assert packet["signature_required"] is True
    assert packet["cta_style"] == policy.archetype_profile.cta


def test_w5_template_policy_resolves_recruiting_trigger_inmail_budgets() -> None:
    recruiter = resolve_recipient_template_policy(
        recipient_class=CLASS_RECRUITER,
        message_type="trigger_based_insight",
        channel=CHANNEL_LINKEDIN_INMAIL,
    )
    senior_ta = resolve_recipient_template_policy(
        recipient_class=CLASS_SENIOR_TA,
        message_type="trigger_based_insight",
        channel=CHANNEL_LINKEDIN_INMAIL,
    )

    assert recruiter.length_policy.budget_key == "recruiter_trigger_inmail"
    assert senior_ta.length_policy.budget_key == "senior_ta_trigger_inmail"
    assert recruiter.length_policy.subject_required is True
    assert senior_ta.length_policy.subject_required is True


def test_w5_template_policy_resolves_connection_request_controls() -> None:
    policy = resolve_recipient_template_policy(
        recipient_class=CLASS_RECRUITER,
        message_type="general_intro",
        channel=CHANNEL_LINKEDIN_CHAT,
    )
    packet = policy.length_policy.to_length_budget_packet()

    assert packet["budget_key"] == "linkedin_chat_connection_request"
    assert packet["hard_cap_chars"] == CONNECTION_REQUEST_CHAR_CAP
    assert packet["channel"] == CHANNEL_LINKEDIN_CHAT
    assert packet["route_family"] == "CONNECTION_REQ"
    assert packet["subject_required"] is False
    assert packet["signature_required"] is False
