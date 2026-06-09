from __future__ import annotations

from apps_lic.engines import generation_engine as ge
from apps_lic.engines import validation_exit as ve
from apps_lic.engines.generation_subject_policy import (
    channel_from_length_budget,
    subject_required,
)
from apps_lic.engines.x1d_judge_policy import (
    JUDGE_CEO_EVIDENCE_RISK,
    JUDGE_CEO_ORIGINALITY,
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_LINKEDIN_TONE,
    required_x1d_judge_ids_for_context,
    x1d_judge_profile_policy,
)
from apps_lic.runtime.dispatch import canonical_dispatch as cd
from apps_lic.runtime.dispatch.canonical_manifest_fields import (
    w4_manifest_fields,
    w5_manifest_fields,
)
from apps_lic.types.linkedin_route_envelope import (
    CHANNEL_LINKEDIN_CHAT,
    CHANNEL_LINKEDIN_INMAIL,
    CONNECTION_REQUEST_CHAR_CAP,
    INMAIL_BODY_CHAR_CAP,
)


def test_w7_generation_subject_policy_module_matches_generation_engine_compatibility() -> None:
    budgets = (
        {"budget_key": "c_level_trigger_inmail", "hard_cap_chars": INMAIL_BODY_CHAR_CAP},
        {"budget_key": "short", "hard_cap_chars": CONNECTION_REQUEST_CHAR_CAP},
        {"channel": CHANNEL_LINKEDIN_CHAT, "subject_required": False},
        {"channel": CHANNEL_LINKEDIN_INMAIL, "subject_required": True},
    )

    for budget in budgets:
        assert ge._subject_required(budget) == subject_required(budget)
        assert ge._channel_from_length_budget(budget) == channel_from_length_budget(budget)


def test_w7_x1d_policy_module_matches_validation_exit_compatibility_exports() -> None:
    assert ve.x1d_judge_profile_policy is x1d_judge_profile_policy
    assert ve.required_x1d_judge_ids_for_context is required_x1d_judge_ids_for_context

    assert required_x1d_judge_ids_for_context(
        recipient_class="CEO",
        message_type="trigger_based_insight",
    ) == (JUDGE_CEO_ORIGINALITY, JUDGE_CEO_EVIDENCE_RISK)
    assert required_x1d_judge_ids_for_context(
        recipient_class="EXECUTIVE",
        message_type="trigger_based_insight",
        proof_ids=("sp_platform_commercialization",),
    ) == (JUDGE_LINKEDIN_TONE, JUDGE_EVIDENCE_SUPPORT)

    profiles = x1d_judge_profile_policy()
    assert profiles[JUDGE_CEO_ORIGINALITY].threshold == 0.88
    assert profiles[JUDGE_CEO_EVIDENCE_RISK].threshold == 0.86


def test_w7_canonical_manifest_field_module_matches_dispatch_compatibility() -> None:
    assert cd._w4_manifest_fields is w4_manifest_fields
    assert cd._w5_manifest_fields is w5_manifest_fields

    assert w4_manifest_fields(None)["w4_candidate_invoked"] is False
    assert w5_manifest_fields(None)["w5_validation_exit_invoked"] is False
