"""EQ-11 — AgentRoutingSpec tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.agent_routing_spec import (
    AgentRoutingSpec,
)


class TestDefaults:
    def test_default_construction_has_all_none_or_false(self) -> None:
        spec = AgentRoutingSpec()
        assert spec.thinking_budget is None
        assert spec.reasoning_effort is None
        assert spec.verbosity is None
        assert spec.markdown_output is False
        assert spec.response_schema is None

    def test_is_default_true_for_fresh_instance(self) -> None:
        assert AgentRoutingSpec().is_default() is True

    def test_is_default_false_when_any_field_set(self) -> None:
        assert AgentRoutingSpec(thinking_budget=1000).is_default() is False
        assert AgentRoutingSpec(reasoning_effort="low").is_default() is False
        assert AgentRoutingSpec(verbosity="medium").is_default() is False
        assert AgentRoutingSpec(markdown_output=True).is_default() is False
        assert (
            AgentRoutingSpec(response_schema={"type": "object"}).is_default()
            is False
        )


class TestValidation:
    def test_negative_thinking_budget_raises(self) -> None:
        with pytest.raises(ValueError, match="thinking_budget"):
            AgentRoutingSpec(thinking_budget=-1)

    def test_zero_thinking_budget_allowed(self) -> None:
        # Zero is a legitimate "disable thinking" signal for Anthropic.
        AgentRoutingSpec(thinking_budget=0)

    @pytest.mark.parametrize("bad", ["LOW", "extreme", "", "1"])
    def test_invalid_reasoning_effort_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="reasoning_effort"):
            AgentRoutingSpec(reasoning_effort=bad)

    @pytest.mark.parametrize("good", ["low", "medium", "high"])
    def test_valid_reasoning_effort_accepted(self, good: str) -> None:
        AgentRoutingSpec(reasoning_effort=good)

    @pytest.mark.parametrize("bad", ["verbose", "terse", "MEDIUM"])
    def test_invalid_verbosity_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="verbosity"):
            AgentRoutingSpec(verbosity=bad)


class TestSerialization:
    def test_to_dict_roundtrip_has_all_fields(self) -> None:
        spec = AgentRoutingSpec(
            thinking_budget=2000,
            reasoning_effort="high",
            verbosity="low",
            markdown_output=True,
            response_schema={"type": "object"},
        )
        data = spec.to_dict()
        assert data == {
            "thinking_budget": 2000,
            "reasoning_effort": "high",
            "verbosity": "low",
            "markdown_output": True,
            "response_schema": {"type": "object"},
        }


class TestMergeIntoExtra:
    def test_default_spec_returns_extra_unchanged(self) -> None:
        original = {"adapter": "x", "slots_used": []}
        merged = AgentRoutingSpec().merge_into_extra(original)
        assert merged == original
        assert "routing_meta" not in merged

    def test_populated_fields_land_under_routing_meta(self) -> None:
        spec = AgentRoutingSpec(
            thinking_budget=500,
            reasoning_effort="medium",
            markdown_output=True,
        )
        merged = spec.merge_into_extra({"adapter": "openai"})
        assert merged["routing_meta"] == {
            "thinking_budget": 500,
            "reasoning_effort": "medium",
            "markdown_output": True,
        }
        # Non-routing-meta keys preserved.
        assert merged["adapter"] == "openai"

    def test_merge_does_not_mutate_input_extra(self) -> None:
        original = {"adapter": "x"}
        snapshot = dict(original)
        AgentRoutingSpec(verbosity="high").merge_into_extra(original)
        assert original == snapshot

    def test_none_valued_fields_omitted_from_routing_meta(self) -> None:
        spec = AgentRoutingSpec(
            thinking_budget=100
        )  # only this one is populated
        merged = spec.merge_into_extra({})
        assert merged["routing_meta"] == {"thinking_budget": 100}
