"""Unit tests for anthropic_model_tier_policy."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.anthropic_model_tier_policy import (
    DEFAULT_TASK_TIER_POLICY,
    HAIKU_4_5,
    OPUS_4_5,
    SONNET_4_6,
    TASK_CHUNK_CONTEXTUALIZATION,
    TASK_DEEP_REASONING,
    TASK_GROUNDED_ANSWER,
    TASK_JSON_SHAPING,
    TASK_MULTI_AGENT_ORCHESTRATION,
    TASK_QUICK_CLASSIFICATION,
    TASK_RERANKING,
    TASK_SYNTHESIS,
    TIER_HAIKU,
    TIER_MODELS,
    TIER_OPUS,
    TIER_SONNET,
    ModelSelection,
    compose_two_pass_models,
    select_model,
)


# ---------------------------------------------------------------------------
# Default policy correctness (matches Anthropic's tier guidance)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "task,expected_tier",
    [
        (TASK_CHUNK_CONTEXTUALIZATION, TIER_HAIKU),
        (TASK_RERANKING, TIER_HAIKU),
        (TASK_JSON_SHAPING, TIER_HAIKU),
        (TASK_QUICK_CLASSIFICATION, TIER_HAIKU),
        (TASK_SYNTHESIS, TIER_SONNET),
        (TASK_GROUNDED_ANSWER, TIER_SONNET),
        (TASK_DEEP_REASONING, TIER_OPUS),
        (TASK_MULTI_AGENT_ORCHESTRATION, TIER_OPUS),
    ],
)
def test_default_policy_maps_task_to_expected_tier(task, expected_tier):
    selection = select_model(task)
    assert selection.tier == expected_tier
    assert selection.task_type == task


def test_default_policy_cheap_tasks_resolve_to_haiku_model():
    assert select_model(TASK_CHUNK_CONTEXTUALIZATION).model == HAIKU_4_5
    assert select_model(TASK_JSON_SHAPING).model == HAIKU_4_5


def test_default_policy_synthesis_resolves_to_sonnet_model():
    assert select_model(TASK_SYNTHESIS).model == SONNET_4_6


def test_default_policy_deep_reasoning_resolves_to_opus_model():
    assert select_model(TASK_DEEP_REASONING).model == OPUS_4_5


# ---------------------------------------------------------------------------
# Unknown task fallback
# ---------------------------------------------------------------------------


def test_unknown_task_falls_back_to_default_tier():
    selection = select_model("totally_unknown_task")
    assert selection.tier == TIER_SONNET  # default is sonnet
    assert selection.model == SONNET_4_6
    assert "not in policy" in selection.reason


def test_unknown_task_custom_default_tier():
    selection = select_model("mystery_task", default_tier=TIER_HAIKU)
    assert selection.tier == TIER_HAIKU
    assert selection.model == HAIKU_4_5


# ---------------------------------------------------------------------------
# Policy override
# ---------------------------------------------------------------------------


def test_policy_override_changes_tier_selection():
    custom_policy = {
        TASK_SYNTHESIS: TIER_OPUS,  # escalate synthesis to Opus
    }
    selection = select_model(TASK_SYNTHESIS, policy=custom_policy)
    assert selection.tier == TIER_OPUS
    assert selection.model == OPUS_4_5


def test_tier_models_override_changes_model_id():
    custom_tier_models = {
        TIER_HAIKU: "claude-haiku-test-stub",
        TIER_SONNET: "claude-sonnet-test-stub",
        TIER_OPUS: "claude-opus-test-stub",
    }
    selection = select_model(
        TASK_CHUNK_CONTEXTUALIZATION, tier_models=custom_tier_models
    )
    assert selection.tier == TIER_HAIKU
    assert selection.model == "claude-haiku-test-stub"


def test_policy_override_works_with_custom_task():
    custom_policy = {"my_custom_task": TIER_HAIKU}
    selection = select_model("my_custom_task", policy=custom_policy)
    assert selection.tier == TIER_HAIKU


# ---------------------------------------------------------------------------
# Tier-missing-from-tier_models fallback
# ---------------------------------------------------------------------------


def test_tier_missing_falls_back_to_default_tier_model():
    # Policy says Opus, but tier_models only has Sonnet -> should fall back
    # to default tier (Sonnet) and still produce a usable model
    broken_tier_models = {TIER_SONNET: SONNET_4_6}
    selection = select_model(
        TASK_DEEP_REASONING,  # maps to Opus
        tier_models=broken_tier_models,
    )
    assert selection.model == SONNET_4_6
    assert "fallback" in selection.reason


def test_tier_missing_without_default_raises():
    broken_tier_models = {TIER_HAIKU: HAIKU_4_5}  # no sonnet either
    with pytest.raises(ValueError, match="missing both"):
        select_model(
            TASK_DEEP_REASONING,  # opus
            tier_models=broken_tier_models,
            default_tier=TIER_SONNET,  # sonnet also missing
        )


# ---------------------------------------------------------------------------
# compose_two_pass_models (integration w/ dual-pass orchestrator)
# ---------------------------------------------------------------------------


def test_two_pass_models_default_pair():
    pass1, pass2 = compose_two_pass_models()
    # Pass 1 is grounded-answer -> Sonnet
    assert pass1 == SONNET_4_6
    # Pass 2 is JSON shaping -> Haiku
    assert pass2 == HAIKU_4_5


def test_two_pass_models_custom_policy():
    custom = {
        TASK_GROUNDED_ANSWER: TIER_OPUS,
        TASK_JSON_SHAPING: TIER_SONNET,
    }
    pass1, pass2 = compose_two_pass_models(policy=custom)
    assert pass1 == OPUS_4_5
    assert pass2 == SONNET_4_6


# ---------------------------------------------------------------------------
# Result dataclass contract
# ---------------------------------------------------------------------------


def test_result_is_frozen_dataclass():
    s = select_model(TASK_SYNTHESIS)
    with pytest.raises((AttributeError, TypeError)):
        s.model = "other"  # type: ignore[misc]


def test_result_has_all_expected_fields():
    s = select_model(TASK_SYNTHESIS)
    assert isinstance(s, ModelSelection)
    assert s.model
    assert s.tier
    assert s.task_type == TASK_SYNTHESIS
    assert s.reason


# ---------------------------------------------------------------------------
# Policy completeness (documentation-as-test)
# ---------------------------------------------------------------------------


def test_every_task_constant_is_in_default_policy():
    """Guard: exported TASK_* constants should all have a default tier mapping."""
    task_constants = [
        TASK_CHUNK_CONTEXTUALIZATION,
        TASK_RERANKING,
        TASK_JSON_SHAPING,
        TASK_QUICK_CLASSIFICATION,
        TASK_SYNTHESIS,
        TASK_GROUNDED_ANSWER,
        TASK_DEEP_REASONING,
        TASK_MULTI_AGENT_ORCHESTRATION,
    ]
    missing = [t for t in task_constants if t not in DEFAULT_TASK_TIER_POLICY]
    assert missing == [], f"Task constants missing from default policy: {missing}"


def test_every_tier_has_a_model():
    """Guard: every tier referenced in DEFAULT_TASK_TIER_POLICY must map to a model."""
    tiers_in_use = set(DEFAULT_TASK_TIER_POLICY.values())
    missing = tiers_in_use - set(TIER_MODELS.keys())
    assert missing == set(), f"Tiers without models: {missing}"
