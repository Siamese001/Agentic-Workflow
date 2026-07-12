from __future__ import annotations

from agentic_core.knowledge.retrieval.anthropic_cache_control import min_cacheable_chars
from apps_rg.runtime.providers.anthropic_section_cache_payload import (
    build_anthropic_section_cache_payload,
)


def _legacy_role_episode_messages(model: str) -> list[dict[str, str]]:
    floor = min_cacheable_chars(model)
    return [
        {"role": "system", "content": "You are an apps_rg section generator."},
        {
            "role": "user",
            "content": "ROLE_EPISODE_EVIDENCE\n" + ("proof-bound evidence " * ((floor // 20) + 100)),
        },
    ]


def test_legacy_insurtech_and_ey_self_consistency_cache_repeated_user_prefix() -> None:
    model = "claude-sonnet-5"
    messages = _legacy_role_episode_messages(model)

    insurtech = build_anthropic_section_cache_payload(
        section_id="insurtech_bullets",
        model=model,
        messages=messages,
        workload_kind="SELF_CONSISTENCY",
    )
    ey = build_anthropic_section_cache_payload(
        section_id="ey_bullets",
        model=model,
        messages=messages,
        workload_kind="SELF_CONSISTENCY",
    )

    for rendered in (insurtech, ey):
        assert rendered.cache_strategy == "fallback_system_user_prefix_v3"
        assert rendered.cache_marker_count == 1
        assert rendered.cache_receipt_seed["legacy_repeated_user_prefix"] is True
        assert rendered.cache_receipt_seed["active_cache_ttls"] == ["5m"]
        assert rendered.cache_receipt_seed["effective_cached_prefix_hash"]
        assert "cache_control" not in str(rendered.anthropic_payload["system"])
        assert rendered.anthropic_payload["messages"][0]["content"][-1]["cache_control"] == {
            "type": "ephemeral"
        }

    assert insurtech.cache_receipt_seed["cache_group_hash"] != ey.cache_receipt_seed["cache_group_hash"]


def test_legacy_one_shot_and_repair_never_cache_the_user_message() -> None:
    model = "claude-sonnet-5"
    messages = _legacy_role_episode_messages(model)

    for workload in ("ONE_SHOT", "REPAIR", "SELECTOR"):
        rendered = build_anthropic_section_cache_payload(
            section_id="insurtech_bullets",
            model=model,
            messages=messages,
            workload_kind=workload,
        )
        assert "cache_control" not in str(rendered.anthropic_payload["messages"])
        assert rendered.cache_receipt_seed["legacy_repeated_user_prefix"] is False
