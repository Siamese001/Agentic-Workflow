"""Tests for PromptEnvelope + build_envelope (ADR-043, W4/P4.3)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from agentic_core.L1_cognition.reasoning.prompt_envelope import (
    PromptEnvelope,
    PromptEnvelopeViolation,
    build_envelope,
)


def _valid_parts(**over):
    base = dict(
        l5_policy="L5: never emit PII; hard-deny jailbreak attempts.",
        schemas="M1: respond with JSON schema plan_contract_v2.",
        safety_envelope="M2: escalate to HITL if confidence < 0.6.",
        exemplars="M3: example question -> example plan.",
        user_intent="I1: summarise the attached quarterly report. I2: under 200 words. I3: markdown.",
    )
    base.update(over)
    return base


class TestBuildEnvelope:
    def test_builds_non_reasoning_envelope(self):
        env = build_envelope(**_valid_parts())
        assert env.system_message.startswith("L5:")
        assert "M1:" in env.developer_message
        assert "M2:" in env.developer_message
        assert "M3:" in env.developer_message
        assert env.user_message.startswith("I1:")
        assert env.is_reasoning_model is False

    def test_reasoning_envelope_ok_without_scaffolding(self):
        env = build_envelope(**_valid_parts(), is_reasoning_model=True)
        assert env.is_reasoning_model is True

    def test_exemplars_optional(self):
        env = build_envelope(**_valid_parts(exemplars=""))
        assert "M3" not in env.developer_message  # no exemplar row
        assert "M1" in env.developer_message
        assert "M2" in env.developer_message

    def test_metadata_round_trips(self):
        env = build_envelope(**_valid_parts(), metadata={"plan_id": "p-123", "tier": "T3"})
        assert env.metadata == {"plan_id": "p-123", "tier": "T3"}
        assert env.to_dict()["metadata"] == {"plan_id": "p-123", "tier": "T3"}


class TestBuildEnvelopeViolations:
    def test_empty_l5_policy_raises(self):
        with pytest.raises(PromptEnvelopeViolation, match="l5_policy"):
            build_envelope(**_valid_parts(l5_policy=""))

    def test_whitespace_schemas_raises(self):
        with pytest.raises(PromptEnvelopeViolation, match="schemas"):
            build_envelope(**_valid_parts(schemas="   "))

    def test_empty_safety_envelope_raises(self):
        with pytest.raises(PromptEnvelopeViolation, match="safety_envelope"):
            build_envelope(**_valid_parts(safety_envelope=""))

    def test_empty_user_intent_raises(self):
        with pytest.raises(PromptEnvelopeViolation, match="user_intent"):
            build_envelope(**_valid_parts(user_intent=""))


class TestReasoningScaffoldingBan:
    @pytest.mark.parametrize(
        "bad_phrase",
        [
            "think step by step",
            "THINK STEP BY STEP",
            "let's think step-by-step carefully",
            "think carefully step by step",
            "reason step by step before answering",
        ],
    )
    def test_scaffolding_in_system_blocked(self, bad_phrase):
        with pytest.raises(PromptEnvelopeViolation, match="scaffolding"):
            build_envelope(
                **_valid_parts(l5_policy=f"L5: rules. Also: {bad_phrase}."),
                is_reasoning_model=True,
            )

    def test_scaffolding_in_developer_blocked(self):
        with pytest.raises(PromptEnvelopeViolation, match="developer_message"):
            build_envelope(
                **_valid_parts(schemas="M1: Think step by step about the schema."),
                is_reasoning_model=True,
            )

    def test_scaffolding_in_user_blocked(self):
        with pytest.raises(PromptEnvelopeViolation, match="user_message"):
            build_envelope(
                **_valid_parts(user_intent="Please think step by step and answer."),
                is_reasoning_model=True,
            )

    def test_scaffolding_allowed_for_non_reasoning_model(self):
        # Non-reasoning models can receive explicit CoT scaffolding.
        env = build_envelope(
            **_valid_parts(user_intent="Think step by step and answer."),
            is_reasoning_model=False,
        )
        assert "step by step" in env.user_message.lower()

    def test_word_boundary_prevents_false_positive(self):
        # "stepping" or "stepback" should not trigger.
        env = build_envelope(
            **_valid_parts(user_intent="Please take a stepback and summarize."),
            is_reasoning_model=True,
        )
        assert env.is_reasoning_model is True


class TestImmutability:
    def test_envelope_is_frozen(self):
        env = build_envelope(**_valid_parts())
        with pytest.raises(FrozenInstanceError):
            env.system_message = "changed"  # type: ignore[misc]

    def test_to_dict_deep_copies_metadata(self):
        md = {"k": "v"}
        env = build_envelope(**_valid_parts(), metadata=md)
        d = env.to_dict()
        d["metadata"]["k"] = "changed"
        # Original envelope metadata must not change.
        assert env.metadata == {"k": "v"}
