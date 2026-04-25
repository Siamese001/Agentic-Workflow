"""W8 tests for Gemini adapter + registry dispatch."""

from __future__ import annotations

from agentic_core.L2_execution.enforcement._adapter_gemini import (
    GeminiMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_registry import get_adapter
from agentic_core.L2_execution.enforcement.provider_adapter import ProviderPayload
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import ProviderType


class TestGeminiPassthrough:
    def test_returns_provider_payload(self) -> None:
        adapter = GeminiMessageAdapter()
        payload = adapter.render(
            final_system_string="You are helpful.",
            final_user_string="Hello.",
            tools_schema=[],
            slots_used=["S0", "U0"],
        )
        assert isinstance(payload, ProviderPayload)
        assert payload.system_prompt == "You are helpful."
        assert payload.user_prompt == "Hello."
        assert payload.extra["adapter"] == "gemini"
        assert payload.extra["system_format"] == "markdown"
        assert payload.extra["envelope"] == "system_instruction+contents"

    def test_tools_schema_passthrough(self) -> None:
        schema = [{"function_declarations": [{"name": "search"}]}]
        adapter = GeminiMessageAdapter()
        payload = adapter.render(final_system_string="s", final_user_string="u", tools_schema=schema)
        assert payload.tools_schema is schema


class TestGeminiCompose:
    def test_composes_markdown_from_slots_map(self) -> None:
        adapter = GeminiMessageAdapter()
        payload = adapter.render(
            final_system_string="(ignored when slots present)",
            final_user_string="Go.",
            tools_schema=None,
            slots_used=["S0", "I0", "U0"],
            slots_map={
                "S0": "You are an engineer.",
                "I0": "Be precise.",
                "U0": "hidden",
            },
        )
        assert "# Role\n\nYou are an engineer." in payload.system_prompt
        assert "# Instructions\n\nBe precise." in payload.system_prompt
        assert "hidden" not in payload.system_prompt
        assert payload.user_prompt == "Go."

    def test_empty_slots_map_falls_back_to_flat(self) -> None:
        adapter = GeminiMessageAdapter()
        payload = adapter.render(
            final_system_string="(flat fallback)",
            final_user_string="u",
            tools_schema=None,
            slots_map={},
        )
        assert payload.system_prompt == "(flat fallback)"


class TestRegistryRouting:
    def test_vertex_ai_now_routes_to_gemini(self) -> None:
        adapter = get_adapter(ProviderType.VERTEX_AI)
        assert adapter.name == "gemini"

    def test_other_mappings_preserved(self) -> None:
        assert get_adapter(ProviderType.ANTHROPIC).name == "anthropic"
        assert get_adapter(ProviderType.OPENAI).name == "openai"
        assert get_adapter(ProviderType.AZURE_OPENAI).name == "openai"
        assert get_adapter(ProviderType.LOCAL_VLLM).name == "openai"
