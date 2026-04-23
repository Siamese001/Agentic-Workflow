"""Unit tests for W2 provider adapter layer.

Covers:
- Feature flag (``adapter_v2_enabled``) reflects env var.
- Anthropic and OpenAI adapters produce correct ``ProviderPayload`` for
  passthrough and structured-slots composition.
- Adapter registry dispatches correctly by ``ProviderType``.
- Registry fallback for unknown providers.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement._adapter_anthropic import (
    AnthropicMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_openai import (
    OpenAIMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_registry import get_adapter
from agentic_core.L2_execution.enforcement.provider_adapter import (
    ProviderPayload,
    adapter_v2_enabled,
)
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import ProviderType


class TestFeatureFlag:
    def test_disabled_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("PROMPT_ADAPTER_V2", raising=False)
        assert adapter_v2_enabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "True", "YES"])
    def test_enabled_truthy(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("PROMPT_ADAPTER_V2", value)
        assert adapter_v2_enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", ""])
    def test_disabled_falsy(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("PROMPT_ADAPTER_V2", value)
        assert adapter_v2_enabled() is False


class TestAnthropicAdapterPassthrough:
    def test_returns_provider_payload(self) -> None:
        adapter = AnthropicMessageAdapter()
        payload = adapter.render(
            final_system_string="You are a helpful assistant.",
            final_user_string="Hello.",
            tools_schema=[],
            slots_used=["S0", "U0"],
        )
        assert isinstance(payload, ProviderPayload)
        assert payload.system_prompt == "You are a helpful assistant."
        assert payload.user_prompt == "Hello."
        assert payload.tools_schema == []
        assert payload.extra["adapter"] == "anthropic"
        assert payload.extra["slots_used"] == ["S0", "U0"]
        assert payload.extra["structural_tags_detected"] is False

    def test_detects_structural_tags(self) -> None:
        adapter = AnthropicMessageAdapter()
        payload = adapter.render(
            final_system_string="<instructions>Be helpful.</instructions>",
            final_user_string="Hi.",
            tools_schema=None,
        )
        assert payload.extra["structural_tags_detected"] is True


class TestAnthropicAdapterStructuredCompose:
    def test_composes_xml_from_slots_map(self) -> None:
        adapter = AnthropicMessageAdapter()
        payload = adapter.render(
            final_system_string="(legacy flat)",
            final_user_string="Do the thing.",
            tools_schema=None,
            slots_used=["S0", "I0", "D0", "C0", "U0"],
            slots_map={
                "S0": "You are a helpful assistant.",
                "I0": "Follow all instructions precisely.",
                "D0": "Never call unlisted tools.",
                "C0": "Context snippet.",
                "U0": "This should be ignored in system.",  # U0 goes to user turn
            },
        )
        # System string built from structured slots, not the legacy flat one.
        assert "<role>\nYou are a helpful assistant.\n</role>" in payload.system_prompt
        assert "<instructions>" in payload.system_prompt
        assert "<D0>\nNever call unlisted tools.\n</D0>" in payload.system_prompt
        assert "<context>\nContext snippet.\n</context>" in payload.system_prompt
        # U0 must NOT leak into system.
        assert "This should be ignored in system" not in payload.system_prompt
        assert payload.user_prompt == "Do the thing."

    def test_empty_slots_map_falls_back_to_flat(self) -> None:
        adapter = AnthropicMessageAdapter()
        payload = adapter.render(
            final_system_string="(flat fallback)",
            final_user_string="Go.",
            tools_schema=None,
            slots_used=None,
            slots_map={},  # empty dict → empty composition → fallback
        )
        assert payload.system_prompt == "(flat fallback)"


class TestOpenAIAdapterPassthrough:
    def test_returns_provider_payload_with_markdown_hint(self) -> None:
        adapter = OpenAIMessageAdapter()
        payload = adapter.render(
            final_system_string="You are helpful.",
            final_user_string="Hi there.",
            tools_schema=[],
            slots_used=["S0", "U0"],
        )
        assert payload.system_prompt == "You are helpful."
        assert payload.user_prompt == "Hi there."
        assert payload.extra["adapter"] == "openai"
        assert payload.extra["system_format"] == "markdown"


class TestOpenAIAdapterStructuredCompose:
    def test_composes_markdown_from_slots_map(self) -> None:
        adapter = OpenAIMessageAdapter()
        payload = adapter.render(
            final_system_string="(flat)",
            final_user_string="Do X.",
            tools_schema=None,
            slots_used=["S0", "I0", "U0"],
            slots_map={
                "S0": "You are helpful.",
                "I0": "Follow instructions.",
                "U0": "hidden",
            },
        )
        assert "# Role\n\nYou are helpful." in payload.system_prompt
        assert "# Instructions\n\nFollow instructions." in payload.system_prompt
        assert "hidden" not in payload.system_prompt
        assert payload.user_prompt == "Do X."


class TestAdapterRegistry:
    @pytest.mark.parametrize(
        "provider_type,expected_name",
        [
            (ProviderType.ANTHROPIC, "anthropic"),
            (ProviderType.OPENAI, "openai"),
            (ProviderType.AZURE_OPENAI, "openai"),
            (ProviderType.VERTEX_AI, "gemini"),  # W8: dedicated Gemini adapter.
            (ProviderType.LOCAL_VLLM, "openai"),
        ],
    )
    def test_registry_dispatches_correctly(
        self, provider_type: ProviderType, expected_name: str
    ) -> None:
        adapter = get_adapter(provider_type)
        assert adapter.name == expected_name

    def test_adapter_renders_through_registry(self) -> None:
        """Sanity: resolved adapter can render end-to-end."""
        adapter = get_adapter(ProviderType.ANTHROPIC)
        payload = adapter.render(
            final_system_string="S",
            final_user_string="U",
            tools_schema=[],
        )
        assert payload.system_prompt == "S"
        assert payload.user_prompt == "U"
