from __future__ import annotations

from apps_lic.engines import generation_engine as ge
from apps_lic.engines.whole_message_generation import resolve_length_budget
from apps_lic.types.recipient_archetype_mapping import resolve_recipient_template_policy


def test_w5_whole_message_length_budget_materializes_shared_template_policy() -> None:
    policy = resolve_recipient_template_policy(
        recipient_class="CEO",
        message_type="trigger_based_insight",
        channel="linkedin_inmail",
    )
    budget = resolve_length_budget(
        recipient_class="CEO",
        message_type="trigger_based_insight",
        modifiers={},
        channel="linkedin_inmail",
    )

    assert budget.to_packet() == policy.length_policy.to_length_budget_packet()


def test_w5_generation_engine_reads_explicit_subject_and_channel_policy() -> None:
    budget = {
        "budget_key": "custom_policy_packet",
        "hard_cap_chars": 1900,
        "subject_required": False,
        "channel": "linkedin_chat",
    }

    assert ge._subject_required(budget) is False
    assert ge._channel_from_length_budget(budget) == "linkedin_chat"
